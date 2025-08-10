from typing import Literal, TypeAlias

from nonebot_plugin_alconna import Target
from sqlalchemy import JSON, Text, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session

SubscriptionType: TypeAlias = Literal[
    # "daily",
    "weekly",
    "monthly",
    "yearly",
]


class User(Model):
    __tablename__ = "wakatime"

    id: Mapped[int] = mapped_column(primary_key=True)
    """User ID"""
    access_token: Mapped[str] = mapped_column(Text)
    """Wakatime Access Token"""


class Subscription(Model):
    __tablename__ = "wakatime_subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    """Subscription ID"""
    user_id: Mapped[int] = mapped_column()
    """User ID"""
    type: Mapped[SubscriptionType] = mapped_column(Text)
    """Subscription Type"""
    target: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    """Target information"""


async def get_subscriptions(user_id: int):
    async with get_session() as session:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        subscriptions = await session.scalars(stmt)
        return subscriptions.all() if subscriptions else None


async def add_subscription(user_id: int, type: SubscriptionType, target: Target):
    async with get_session() as session:
        subscription = Subscription(user_id=user_id, type=type, target=target.dump())
        session.add(subscription)
        await session.commit()
        return subscription


async def revoke_subscription(
    user_id: int, type: SubscriptionType | Literal["all"], target: Target
):
    async with get_session() as session:
        stmt = select(Subscription).where(
            Subscription.user_id == user_id, Subscription.target == target.dump()
        )
        if type != "all":
            stmt = stmt.where(Subscription.type == type)

        subscription = await session.scalar(stmt)
        if subscription:
            await session.delete(subscription)
            await session.commit()
            return True
        return False
