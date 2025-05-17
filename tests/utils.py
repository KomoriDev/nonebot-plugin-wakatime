import itertools
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GroupMessageEvent
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11PrivateMessageEvent

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
