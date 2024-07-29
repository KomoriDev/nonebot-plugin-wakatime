from typing import Literal, TypeAlias

import httpx
from httpx import Response
from sqlalchemy import select
from nonebot_plugin_orm import get_session

from ..models import User
from ..config import config
from ..shema import Stats, Users
from ..exception import UserUnboundException

api_url = config.api_url
TimeScope: TypeAlias = Literal[
    "last_7_days", "last_30_days", "last_6_months", "last_year", "all_time"
]


class API:

    _access_token_cache: dict[str, str] = {}

    @classmethod
    async def get_access_token(cls, user_id: str) -> str:
        """Get the access token from database"""
        if user_id in cls._access_token_cache:
            return cls._access_token_cache[user_id]

        session = get_session()
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            user = (await session.execute(stmt)).scalar()

            if not user:
                raise UserUnboundException

            cls._access_token_cache[user_id] = user.access_token
            return user.access_token

    @classmethod
    async def bind_user(cls, code: str) -> Response:
        """Get the secret access token.

        Args:
            code: The code parameter in the callback address
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wakatime.com/oauth/token",
                data={
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "redirect_uri": "https://wakatime.com/dashboard",
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
        return response

    @classmethod
    async def get_user_info(cls, user_id: str) -> Users:
        """Get user's information"""
        access_token = await cls.get_access_token(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_url}/users/current",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        return Users(**(response.json()["data"]))

    @classmethod
    async def get_user_stats(
        cls, user_id: str, scope: TimeScope = "last_7_days"
    ) -> Stats:
        """Get user's coding activity.

        Args:
            user_id: user id
            scope: "last_7_days" "last_30_days" "last_6_months" "last_year" "all_time"
        """
        assess_token = await cls.get_access_token(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_url}/users/current/stats/{scope}",
                headers={"Authorization": f"Bearer {assess_token}"},
            )
        return Stats(**(response.json()["data"]))

    @classmethod
    async def get_all_time_since_today(cls, user_id: str) -> str:
        """Get the total time logged since account created."""
        assess_token = await cls.get_access_token(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_url}/users/current/all_time_since_today",
                headers={"Authorization": f"Bearer {assess_token}"},
            )
        return response.json()["data"]["text"]
