from yarl import URL
from nonebug import App
from nonebot import get_adapter
from pytest_mock import MockerFixture
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.onebot.v11 import Message as OneBotV11Message
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotV11MS

from .utils import fake_v11_group_message_event, fake_v11_private_message_event


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
            "scope": "read_stats",
            "state": "state_xxx",
        }
    )

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka bind"))

        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event,
            OneBotV11Message(
                OneBotV11MS.at("2310") + f"前往该页面绑定 wakatime 账号：{auth_url}" + ""
            ),
            result=True,
        ),
        ctx.should_finished()
