from io import BytesIO

import pytest
from nonebug import App
from nonebot import get_adapter
from pytest_mock import MockerFixture
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotV11MS


@pytest.fixture
async def _database(app: App):
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_wakatime.models import Subscription

    async with get_session() as session:
        session.add(
            Subscription(
                user_id=1,
                type="weekly",
                target={
                    "id": "2310",
                    "parent_id": "",
                    "channel": False,
                    "private": True,
                    "self_id": "6371570149",
                    "extra": {"message_thread_id": None},
                    "scope": "QQClient",
                    "adapter": "OneBot V11",
                    "platforms": None,
                },
            )
        )
        session.add(
            Subscription(
                user_id=1,
                type="monthly",
                target={
                    "id": "2310",
                    "parent_id": "",
                    "channel": False,
                    "private": True,
                    "self_id": "6371570149",
                    "extra": {"message_thread_id": None},
                    "scope": "QQClient",
                    "adapter": "OneBot V11",
                    "platforms": None,
                },
            )
        )
        session.add(
            Subscription(
                user_id=1,
                type="yearly",
                target={
                    "id": "2310",
                    "parent_id": "",
                    "channel": False,
                    "private": True,
                    "self_id": "6371570149",
                    "extra": {"message_thread_id": None},
                    "scope": "QQClient",
                    "adapter": "OneBot V11",
                    "platforms": None,
                },
            )
        )
        await session.commit()


@pytest.mark.usefixtures("_database")
async def test_post_subscription(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime.schema import Stats
    from nonebot_plugin_wakatime.schedule import post_subscription

    image = BytesIO(b"test")

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

    mocker.patch("nonebot_plugin_wakatime.API.get_user_stats", return_value=stats)
    mocker.patch(
        "nonebot_plugin_wakatime.schedule.render_subscription",
        return_value=image,
    )

    async with app.test_api() as ctx:
        adapter = get_adapter(OneBotV11Adapter)
        ctx.create_bot(base=OneBotV11Bot, adapter=adapter)

        ctx.should_call_api(
            "send_msg",
            {
                "message_type": "private",
                "user_id": 2310,
                "message": [OneBotV11MS.image(image)],
            },
        )

        await post_subscription(type="weekly")

        ctx.should_call_api(
            "send_msg",
            {
                "message_type": "private",
                "user_id": 2310,
                "message": [OneBotV11MS.image(image)],
            },
        )

        await post_subscription(type="monthly")

        ctx.should_call_api(
            "send_msg",
            {
                "message_type": "private",
                "user_id": 2310,
                "message": [OneBotV11MS.image(image)],
            },
        )

        await post_subscription(type="yearly")
