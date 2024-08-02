from nonebug import App
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.onebot.v11 import Message as OneBotV11Message
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotV11MS

from .utils import fake_v11_group_message_event


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
