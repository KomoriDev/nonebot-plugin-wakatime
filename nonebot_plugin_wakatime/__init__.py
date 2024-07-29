import asyncio
from urllib.parse import parse_qs

from nonebot import require
from nonebot.rule import Rule
from nonebot.log import logger
from httpx import ConnectTimeout
from nonebot.internal.adapter import Event
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_orm")
require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_alconna.uniseg import At, Button, UniMessage
from nonebot_plugin_alconna import Args, Match, Option, Alconna, MsgTarget, on_alconna

from .apis import API
from . import migrations
from .models import User
from .config import Config
from .shema import WakaTime
from .render_pic import render
from .exception import UserUnboundException
from .config import config as wakatime_config

__plugin_meta__ = PluginMetadata(
    name="谁是卷王",
    description="将代码统计嵌入 Bot 中",
    usage="/wakatime",
    type="application",
    config=Config,
    homepage="https://github.com/KomoriDev/nonebot-plugin-wakatime",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "unique_name": "WakaTime",
        "orm_version_location": migrations,
        "author": "Komorebi <mute231010@gmail.com>",
        "version": "0.1.3",
    },
)

client_id = wakatime_config.client_id
client_secret = wakatime_config.client_secret
redirect_uri = wakatime_config.redirect_uri

if client_id == "" or client_secret == "" or redirect_uri == "":
    logger.warning("缺失必要配置项，已禁用该插件")


def is_enable() -> Rule:

    def _rule() -> bool:
        return client_id != "" and client_secret != "" and redirect_uri != ""

    return Rule(_rule)


wakatime = on_alconna(
    Alconna(
        "wakatime",
        Args["target?", At | int],
        Option("-b|--bind|bind", Args["code?", str], help_text="绑定 wakatime"),
    ),
    aliases={"waka"},
    rule=is_enable(),
    use_cmd_start=True,
)


@wakatime.assign("$main")
async def _(event: Event, target: Match[At | int]):
    if target.available:
        if isinstance(target, At):
            target_name = "他"
            target_id = target.target
        else:
            target_name = "他"
            target_id = target.result
    else:
        target_name = "你"
        target_id = event.get_user_id()

    try:
        user_info_task = API.get_user_info(target_id)
        stats_info_task = API.get_user_stats(target_id)
        all_time_since_today_task = API.get_all_time_since_today(target_id)

        user_info, stats_info, all_time_since_today = await asyncio.gather(
            user_info_task, stats_info_task, all_time_since_today_task
        )
    except UserUnboundException:
        await UniMessage.text(
            f"{target_name}还没有绑定 Wakatime 账号！请私聊我并使用 /bind 命令进行绑定"
        ).finish(at_sender=True)
    except ConnectTimeout:
        await (
            UniMessage.text("网络超时，再试试叭")
            .keyboard(Button("input", "重试", text="/wakatime"))
            .finish(at_sender=True)
        )

    result = WakaTime(
        user=user_info, stats=stats_info, all_time_since_today=all_time_since_today
    )
    image = await render(result)
    await UniMessage.image(raw=image).finish(at_sender=True)


@wakatime.assign("bind")
async def _(
    code: Match[str], event: Event, msg_target: MsgTarget, session: async_scoped_session
):

    if await session.get(User, event.get_user_id()):
        await UniMessage("已绑定过 wakatime 账号").finish(at_sender=True)

    if not msg_target.private:
        await UniMessage("绑定指令只允许在私聊中使用").finish(at_sender=True)

    if not code.available:
        auth_url = (
            f"https://wakatime.com/oauth/authorize?client_id={client_id}&response_type=code"
            f"&redirect_uri={redirect_uri}"
        )

        await (
            UniMessage.text(f"前往该页面绑定 wakatime 账号：{auth_url}")
            # .keyboard(Button("link", label="即刻前往", url=auth_url))
            .finish(at_sender=True)
        )

    resp = await API.bind_user(code.result)

    if resp.status_code == 200:
        parsed_data = parse_qs(resp.text)
        user = User(
            user_id=event.get_user_id(),
            platform=msg_target.adapter,
            access_token=parsed_data["access_token"][0],
        )
        session.add(user)
        await session.commit()
        await UniMessage("绑定成功").finish(at_sender=True)

    logger.error(f"用户 {event.get_user_id()} 绑定失败。状态码：{resp.status_code}")
    await UniMessage("绑定失败").finish(at_sender=True)
