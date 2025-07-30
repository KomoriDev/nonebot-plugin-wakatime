import itertools
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GroupMessageEvent
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11PrivateMessageEvent

    from nonebot_plugin_wakatime.schema import Stats as StatsType
    from nonebot_plugin_wakatime.schema import Users as UsersType
    from nonebot_plugin_wakatime.schema import StatsBar as StatsBarType


# nonebot_plugin_alconna.extension:unimsg_cache 使用消息 ID 缓存 unimsg
_message_id = itertools.count(10000)


def fake_v11_group_message_event(**field) -> "V11GroupMessageEvent":
    from pydantic import create_model
    from nonebot.adapters.onebot.v11.event import Sender
    from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

    _Fake = create_model("_Fake", __base__=GroupMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 1
        post_type: Literal["message"] = "message"
        sub_type: str = "normal"
        user_id: int = 2310
        message_type: Literal["group"] = "group"
        group_id: int = 10000
        message_id: int = next(_message_id)
        message: Message = Message("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(
            card="",
            nickname="test",
            role="member",
        )
        to_me: bool = False

    return FakeEvent(**field)


def fake_v11_private_message_event(**field) -> "V11PrivateMessageEvent":
    from pydantic import create_model
    from nonebot.adapters.onebot.v11.event import Sender
    from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent

    _Fake = create_model("_Fake", __base__=PrivateMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 1
        post_type: Literal["message"] = "message"
        sub_type: str = "friend"
        user_id: int = 2310
        message_type: Literal["private"] = "private"
        message_id: int = next(_message_id)
        message: Message = Message("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(nickname="test")
        to_me: bool = False

    return FakeEvent(**field)


def fake_waka_user_info() -> tuple["UsersType", "StatsType", "StatsBarType"]:
    from nonebot_plugin_wakatime.schema import Stats, Users, StatsBar

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
        machines=None,
        user_id="48e5e537-efb7-4304-8562-132953542107",
        username="Komorebi",
        is_up_to_date=True,
    )
    stats_bar = StatsBar(
        grand_total={
            "hours": 1,
            "minutes": 27,
            "total_seconds": 5261.197845,
            "digital": "1:27",
            "decimal": "1.45",
            "text": "1 hr 27 mins",
        },
        categories=None,
        projects=None,
        languages=None,
        editors=None,
        operating_systems=None,
    )
    return user, stats, stats_bar
