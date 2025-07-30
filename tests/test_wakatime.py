from io import BytesIO
from datetime import timedelta

import pytest
from yarl import URL
from nonebug import App
from nonebot import get_adapter
from pytest_mock import MockerFixture
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.onebot.v11 import Message as OneBotV11Message
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotV11MS

from .utils import (
    fake_waka_user_info,
    fake_v11_group_message_event,
    fake_v11_private_message_event,
)

FAKE_IMAGE = BytesIO(
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00"
    b"\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
async def _database(app: App):
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_wakatime.models import User

    async with get_session() as session:
        session.add(User(access_token="access_token_xxx"))
        await session.commit()


async def test_bind_wakatime_group(app: App):
    from nonebot_plugin_wakatime import wakatime

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_group_message_event(message=OneBotV11Message("/waka bind"))

        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event, OneBotV11MS.at("2310") + "绑定指令只允许在私聊中使用", result=True
        )
        ctx.should_finished()


async def test_bind_wakatime_private(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime import wakatime
    from nonebot_plugin_wakatime.bootstrap import mountable

    mocker.patch("os.urandom", return_value=b"0" * 40)

    mock_sha1 = mocker.Mock()
    mock_sha1.hexdigest.return_value = "state_xxx"
    mocker.patch(
        "hashlib.sha1",
        return_value=mock_sha1,
    )

    auth_url = URL("https://wakatime.com/oauth/authorize").with_query(
        {
            "client_id": "client_xxx_id",
            "response_type": "code",
            "redirect_uri": "https://xxx.com",
            "scope": "read_stats,read_summaries",
            "state": "state_xxx",
        }
    )

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka bind"))

        ctx.receive_event(bot, event)

        message = OneBotV11Message(
            [
                OneBotV11MS.at("2310"),
                OneBotV11MS.text(f"前往该页面绑定 wakatime 账号：{auth_url}"),
            ]
        )
        if not mountable:
            message.append(
                OneBotV11MS.text(
                    "请再次输入当前命令，并将获取到的 code 作为参数传入完成绑定"
                )
            )
        ctx.should_call_send(event, message, result=True)
        ctx.should_finished()


async def test_get_wakatime_info_without_binding(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime import wakatime

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11Message(
                OneBotV11MS.at("2310")
                + "你还没有绑定 Wakatime 账号！请私聊我并使用 /wakatime bind 命令进行绑定"
            ),
            result=True,
        )
        ctx.should_finished()


async def test_get_wakatime_info(app: App, mocker: MockerFixture):
    from nonebot_plugin_argot import Argot
    from nonebot_plugin_alconna import Image, UniMessage

    from nonebot_plugin_wakatime import wakatime

    user, stats, stats_bar = fake_waka_user_info()

    mocked_user_info = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_info",
        return_value=user,
    )
    mocked_user_stats = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_stats",
        return_value=stats,
    )
    mocked_user_stats_bar = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_stats_bar",
        return_value=stats_bar,
    )
    mocked_all_time_since_today = mocker.patch(
        "nonebot_plugin_wakatime.API.get_all_time_since_today",
        return_value="854 hrs 57 mins",
    )
    mocked_wakatime_info_image = mocker.patch(
        "nonebot_plugin_wakatime.render",
        return_value=FAKE_IMAGE,
    )
    mocked_wakatime_info_background = mocker.patch(
        "nonebot_plugin_wakatime.get_background_image",
        return_value="https://nonebot.dev/logo.png",
    )

    def check_process_argot_message(send: UniMessage) -> UniMessage:
        assert send[-1] == Argot(
            name="background",
            command="background",
            segment=Image(url="https://nonebot.dev/logo.png"),
            expired_at=timedelta(seconds=300),
        )
        return send.exclude(Argot)

    mocked_process_argot_message = mocker.patch(
        "nonebot_plugin_argot.extension.process_argot_message",
        side_effect=check_process_argot_message,
    )

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11Message(OneBotV11MS.at("2310") + OneBotV11MS.image(file=FAKE_IMAGE)),
            result=True,
        )
        ctx.should_finished()

    mocked_user_info.assert_called_once()
    mocked_user_stats.assert_called_once()
    mocked_user_stats_bar.assert_called_once()
    mocked_all_time_since_today.assert_called_once()
    mocked_wakatime_info_image.assert_called_once()
    mocked_wakatime_info_background.assert_called_once()
    mocked_process_argot_message.assert_called_once()


async def test_get_wakatime_info_timeout(app: App, mocker: MockerFixture):
    from httpx import ConnectTimeout

    from nonebot_plugin_wakatime import wakatime

    mocked_user_info = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_info",
        side_effect=ConnectTimeout("some reason"),
    )
    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("网络超时，再试试叭"),
            result=True,
        )
        ctx.should_finished()

    mocked_user_info.assert_called_once()


async def test_subscribe_group(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime import wakatime

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_group_message_event(message=OneBotV11Message("/waka subscribe"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("订阅指令只允许在私聊中使用"),
            result=True,
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_database")
async def test_subscribe_private(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime import wakatime

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe --list")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("暂无订阅记录"),
            result=True,
        )
        ctx.should_finished()

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("订阅成功"),
            result=True,
        )
        ctx.should_finished()

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("已在当前平台订阅过该类型"),
            result=True,
        )
        ctx.should_finished()

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe --list")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            (
                OneBotV11MS.at("2310")
                + OneBotV11MS.text("订阅记录：\nOneBot V11(2310): weekly")
            ),
            result=True,
        )
        ctx.should_finished()

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe --revoke monthly")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("未在当前平台订阅过该类型"),
            result=True,
        )
        ctx.should_finished()

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(
            message=OneBotV11Message("/waka subscribe --revoke weekly")
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11MS.at("2310") + OneBotV11MS.text("取消订阅成功"),
            result=True,
        )
        ctx.should_finished()
