from nonebot import logger
from sqlalchemy import select
from nonebot_plugin_orm import get_session
from nonebot_plugin_user import get_user_by_id
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_alconna import Target, UniMessage

from .apis import API
from .render_pic import render_subscription
from .models import Subscription, SubscriptionType


async def post_subscription(type: SubscriptionType):
    async with get_session() as session:
        stmt = select(Subscription).where(Subscription.type == type)
        result = await session.scalars(stmt)
        subscriptions = result.all() if result else []
        for subscription in subscriptions:
            user = await get_user_by_id(subscription.user_id)
            target = Target.load(subscription.target)

            match subscription.type:
                case "weekly":
                    scope = "last_7_days"
                case "monthly":
                    scope = "last_30_days"
                case "yearly":
                    scope = "last_year"
                case _:
                    scope = "last_7_days"

            stats = await API.get_user_stats(user.id, scope=scope)

            post_image = await render_subscription(subscription.type, stats)

            logger.info(
                f"Posting subscription {subscription.type} for user {target.id}({target.adapter})"  # noqa: E501
            )

            await UniMessage.image(raw=post_image).send(target=target)
            return


logger.debug("Scheduling Wakatime subscription tasks...")
scheduler.add_job(
    post_subscription,
    "cron",
    day_of_week="mon",
    hour=6,
    minute=30,
    args=["weekly"],
    id="weekly",
)
scheduler.add_job(
    post_subscription,
    "cron",
    day=1,
    hour=6,
    minute=30,
    args=["monthly"],
    id="monthly",
)
scheduler.add_job(
    post_subscription,
    "cron",
    month=1,
    day=1,
    hour=6,
    minute=30,
    args=["yearly"],
    id="yearly",
)
