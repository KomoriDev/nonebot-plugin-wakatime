from io import BytesIO

from yarl import URL
from nonebug import App
from nonebot import get_adapter
from pytest_mock import MockerFixture
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.onebot.v11 import Message as OneBotV11Message
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotV11MS

from .utils import fake_v11_group_message_event, fake_v11_private_message_event

FAKE_IMAGE = BytesIO(
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00"
    b"\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82"
)


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
            "scope": "read_stats",
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
    from nonebot_plugin_wakatime import wakatime
    from nonebot_plugin_wakatime.schema import Stats, Users

    user = Users(
        id="48e5e537-efb7-4304-8562-132953542107",
        photo="https://wakatime.com/photo/48e5e537-efb7-4304-8562-132953542107",
        last_project="nonebot-plugin-wakatime",
        username="Komorebi",
        created_at="2023-02-02T07:24:13Z",
    )
    stats = Stats(
        human_readable_total="22 hrs 36 mins",
        human_readable_total_including_other_language="61 hrs 31 mins",
        daily_average=11627.0,
        daily_average_including_other_language=31644.0,
        human_readable_daily_average="3 hrs 13 mins",
        human_readable_daily_average_including_other_language="8 hrs 47 mins",
        categories=None,
        projects=None,
        languages=None,
        editors=None,
        operating_systems=None,
        user_id="48e5e537-efb7-4304-8562-132953542107",
        username="Komorebi",
    )

    mocked_user_info = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_info",
        return_value=user,
    )
    mocked_user_stats = mocker.patch(
        "nonebot_plugin_wakatime.API.get_user_stats",
        return_value=stats,
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

    async with app.test_matcher(wakatime) as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        bot = ctx.create_bot(base=OneBotV11Bot, adapter=adapter)
        event = fake_v11_private_message_event(message=OneBotV11Message("/waka"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            OneBotV11Message(OneBotV11MS.at("2310") + OneBotV11MS.image(file=FAKE_IMAGE)),
            result=True,
            argot={
                "name": "background",
                "command": "background",
                "content": "https://nonebot.dev/logo.png",
                "expire": 300,
            },
        )
        ctx.should_finished()

    mocked_user_info.assert_called_once()
    mocked_user_stats.assert_called_once()
    mocked_all_time_since_today.assert_called_once()
    mocked_wakatime_info_image.assert_called_once()
    mocked_wakatime_info_background.assert_called_once()
