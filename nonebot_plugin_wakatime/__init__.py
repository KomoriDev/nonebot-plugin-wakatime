import os
import asyncio
import hashlib
from pathlib import Path
from collections import defaultdict
from importlib.util import find_spec

from yarl import URL
from nonebot import require
from nonebot.rule import Rule
from nonebot.log import logger
from playwright.async_api import TimeoutError
from httpx import ConnectError, ConnectTimeout
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_orm")
require("nonebot_plugin_user")
require("nonebot_plugin_argot")
require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_localstore")
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_user import UserSession, get_user
from nonebot_plugin_argot import Argot, ArgotExtension
from nonebot_plugin_alconna.uniseg import At, Button, UniMessage, FallbackStrategy
from nonebot_plugin_alconna import (
    Args,
    Image,
    Match,
    Query,
    Option,
    Target,
    Alconna,
    MsgTarget,
    Subcommand,
    CommandMeta,
    on_alconna,
    store_true,
)

if find_spec("nonebot_plugin_apscheduler"):
    require("nonebot_plugin_apscheduler")
    apscheduler_enable = True

    from . import schedule as schedule
else:
    apscheduler_enable = False

from .apis import API
from . import migrations
from .schema import WakaTime
from .render_pic import render
from .utils import get_background_image
from .config import Config, argot_config
from .mount import State, WaitingRecord, waiting_codes
from .exception import BindUserException, UserUnboundException
from .bootstrap import client_id, mountable, redirect_uri, plugin_enable, qq_button_enable
from .models import (
    User,
    SubscriptionType,
    add_subscription,
    get_subscriptions,
    revoke_subscription,
)

__plugin_meta__ = PluginMetadata(
    name="谁是卷王",
    description="将代码统计嵌入 Bot 中",
    usage="/wakatime",
    type="application",
    config=Config,
    homepage="https://github.com/KomoriDev/nonebot-plugin-wakatime",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_user"
    ),
    extra={
        "unique_name": "WakaTime",
        "orm_version_location": migrations,
        "author": "Komorebi <mute231010@gmail.com>",
        "version": "0.2.9",
    },
)


def is_enable() -> Rule:
    def _rule() -> bool:
        return plugin_enable

    return Rule(_rule)


wakatime = on_alconna(
    Alconna(
        "wakatime",
        Args["target?#目标", At | int],
        Option("-b|--bind|bind", Args["code?", str], help_text="绑定 wakatime"),
        Option("--unbind|unbind|revoke", dest="revoke", help_text="取消绑定"),
        meta=CommandMeta(
            description=__plugin_meta__.description,
            usage=__plugin_meta__.usage,
            example="/wakatime [@某人]",
            fuzzy_match=True,
        ),
    ),
    block=True,
    aliases={"waka"},
    rule=is_enable(),
    use_cmd_start=True,
    auto_send_output=True,
    extensions=[ArgotExtension],
)

if apscheduler_enable:
    wakatime.command().add(
        Subcommand(
            "subscribe",
            Args["type?#订阅类型", SubscriptionType],
            Option("-l|--list", help_text="查看订阅"),
            Option(
                "-r|--revoke",
                dest="is_revoke",
                default=False,
                action=store_true,
                help_text="取消订阅",
            ),
            help_text="代码统计订阅",
        )
    )


@wakatime.assign("$main")
async def _(msg_target: MsgTarget, user_session: UserSession, target: Match[At | int]):
    if target.available:
        if isinstance(target.result, At):
            target_name = "他"
            target_platform_id = target.result.target
        else:
            target_name = "他"
            target_platform_id = target.result
        target_id = (await get_user(user_session.platform, str(target_platform_id))).id
    else:
        target_name = "你"
        target_id = user_session.user_id

    try:
        user_info_task = API.get_user_info(target_id)
        stats_info_task = API.get_user_stats(target_id)
        stats_bar_info_task = API.get_user_stats_bar(target_id)
        all_time_since_today_task = API.get_all_time_since_today(target_id)

        (
            user_info,
            stats_info,
            stats_bar_info,
            all_time_since_today,
        ) = await asyncio.gather(
            user_info_task,
            stats_info_task,
            stats_bar_info_task,
            all_time_since_today_task,
        )
    except UserUnboundException:
        await UniMessage.text(
            f"{target_name}还没有绑定 Wakatime 账号！请私聊我并使用 /wakatime bind 命令进行绑定"  # noqa: E501
        ).finish(at_sender=True)
    except (ConnectError, ConnectTimeout, TimeoutError):
        message = UniMessage.text("网络超时，再试试叭")
        if msg_target.adapter != "QQ" or qq_button_enable:
            message.keyboard(Button("input", "重试", text="/wakatime"))
        await message.finish(at_sender=True, fallback=FallbackStrategy.ignore)

    background_image = await get_background_image()

    result = WakaTime(
        user=user_info,
        stats=stats_info,
        stats_bar=stats_bar_info,
        all_time_since_today=all_time_since_today,
        background_image=background_image,
    )
    image = await render(result)
    msg = UniMessage.image(raw=image) + Argot(
        name="background",
        command=argot_config.command if argot_config.command else False,
        segment=(
            Image(path=background_image)
            if isinstance(background_image, Path)
            else Image(url=background_image)
        ),
        expired_at=argot_config.expire,
    )
    await msg.finish(at_sender=True)


@wakatime.assign("bind")
async def _(
    code: Match[str],
    user_session: UserSession,
    msg_target: MsgTarget,
    session: async_scoped_session,
):
    if await session.get(User, user_session.user_id):
        await UniMessage("已绑定过 wakatime 账号").finish(at_sender=True)

    if not msg_target.private:
        await UniMessage("绑定指令只允许在私聊中使用").finish(at_sender=True)

    if not code.available:
        state = hashlib.sha1(os.urandom(40)).hexdigest()

        auth_url = URL("https://wakatime.com/oauth/authorize").with_query(
            {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "read_stats,read_summaries",
                "state": state,
            }
        )

        waiting_codes[State(state)] = WaitingRecord(user_session.user, msg_target)

        message = UniMessage.text(f"前往该页面绑定 wakatime 账号：{auth_url}").text(
            "\n请再次输入当前命令，并将获取到的 code 作为参数传入完成绑定"
            if not mountable
            else ""
        )
        if msg_target.adapter != "QQ" or qq_button_enable:
            message.keyboard(Button("link", "即刻前往", url=auth_url.human_repr()))
        await message.finish(at_sender=True, fallback=FallbackStrategy.ignore)

    try:
        user_without_id = await API.bind_user(code.result)

        session.add(user_without_id(id=user_session.user_id))
        await session.commit()
        await UniMessage("绑定成功").finish(at_sender=True)
    except BindUserException:
        logger.exception(f"用户 {user_session.user_id} 绑定失败。")
        await UniMessage("绑定失败").finish(at_sender=True)


@wakatime.assign("revoke")
async def _(user_session: UserSession, session: async_scoped_session):
    if not (user := await session.get(User, user_session.user_id)):
        await UniMessage.text(
            "还没有绑定 Wakatime 账号！请私聊我并使用 /wakatime bind 命令进行绑定"
        ).finish(at_sender=True)

    resp = await API.revoke_user_token(user_session.user_id)
    if resp.status_code == 200:
        await session.delete(user)
        await session.commit()
        await UniMessage("已解绑").finish(at_sender=True)

    logger.error(f"用户 {user_session.user_id} 解绑失败。状态码：{resp.status_code}")
    await UniMessage("解绑失败").finish(at_sender=True)


@wakatime.assign("subscribe.list")
async def _(
    user_session: UserSession,
    session: async_scoped_session,
):
    if not (user := await session.get(User, user_session.user_id)):
        await UniMessage.text(
            "还没有绑定 Wakatime 账号！请私聊我并使用 /wakatime bind 命令进行绑定"
        ).finish(at_sender=True)

    if not (subscriptions := await get_subscriptions(user.id)):
        await UniMessage.text("暂无订阅记录").finish(at_sender=True)

    platform_subscriptions: defaultdict[str, list[str]] = defaultdict(list)
    for sub in subscriptions:
        target_info = Target.load(sub.target)
        key = f"{target_info.adapter}({target_info.id})"
        platform_subscriptions[key].append(sub.type)

    message = "\n".join(
        f"{target_key}: {'; '.join(types)}"
        for target_key, types in platform_subscriptions.items()
    )

    await UniMessage.text(f"订阅记录：\n{message}").finish(at_sender=True)


@wakatime.assign("subscribe")
async def _(
    target: MsgTarget,
    type: Match[SubscriptionType],
    user_session: UserSession,
    session: async_scoped_session,
    is_revoke: Query[bool] = Query("subscribe.is_revoke.value", False),
):
    if not target.private:
        await UniMessage("订阅指令只允许在私聊中使用").finish(at_sender=True)

    if not (user := await session.get(User, user_session.user_id)):
        await UniMessage.text(
            "还没有绑定 Wakatime 账号！请私聊我并使用 /wakatime bind 命令进行绑定"
        ).finish(at_sender=True)

    if not type.available:
        type.result = "weekly"

    if subscriptions := await get_subscriptions(user.id):
        current_subs = [
            s.type for s in subscriptions if target.verify(Target.load(s.target))
        ]
        if not is_revoke.result and type.result in current_subs:
            await UniMessage.text("已在当前平台订阅过该类型").finish(at_sender=True)
        elif is_revoke.result and type.result not in current_subs:
            await UniMessage.text("未在当前平台订阅过该类型").finish(at_sender=True)

    if not is_revoke.result:
        await add_subscription(
            user.id,
            type.result,
            target,
        )
        await UniMessage("订阅成功").finish(at_sender=True)
    else:
        await revoke_subscription(
            user.id,
            type.result,
            target,
        )
        await UniMessage("取消订阅成功").finish(at_sender=True)
