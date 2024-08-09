import json
from functools import partial
from urllib.parse import parse_qs
from typing import Literal, TypeAlias, cast

from sqlalchemy import select
from nonebot_plugin_orm import get_session
from nonebot.drivers import Request, Response

from ..models import User
from ..config import config
from ..bootstrap import driver
from ..schema import Stats, Users
from ..exception import BindUserException, UserUnboundException

api_url = config.api_url
TimeScope: TypeAlias = Literal[
    "last_7_days", "last_30_days", "last_6_months", "last_year", "all_time"
]


class API:
    _access_token_cache: dict[int, str] = {}

    @classmethod
    async def get_access_token(cls, user_id: int) -> str:
        """Get the access token from database"""
        if user_id in cls._access_token_cache:
            return cls._access_token_cache[user_id]

        session = get_session()
        async with session.begin():
            stmt = select(User).where(User.id == user_id)
            user = (await session.execute(stmt)).scalar()

            if not user:
                raise UserUnboundException

            cls._access_token_cache[user_id] = user.access_token
            return user.access_token

    @classmethod
    async def bind_user(cls, code: str) -> partial[User]:
        """Get the secret access token.

        Args:
            code: The code parameter in the callback address

        Returns:
            partial[User]: The user object with access token

        Raises:
            BindUserException: When the request failed
        """
        async with driver.get_session() as session:
            resp = await session.request(
                Request(
                    "POST",
                    "https://wakatime.com/oauth/token",
                    data={
                        "client_id": config.client_id,
                        "client_secret": config.client_secret,
                        "redirect_uri": config.redirect_uri,
                        "grant_type": "authorization_code",
                        "code": code,
                    },
                )
            )
        if resp.status_code == 200:
            if not isinstance(resp.content, str):
                resp.content = cast(bytes, resp.content or b"").decode()
            parsed_data = parse_qs(resp.content)
            user_with_access_token = partial(
                User,
                access_token=parsed_data["access_token"][0],
            )
            return user_with_access_token

        raise BindUserException(resp.status_code, resp.content)

    @classmethod
    async def revoke_user_token(cls, user_id: int) -> Response:
        """Invalidate a secret access token"""
        access_token = await cls.get_access_token(user_id)
        async with driver.get_session() as session:
            response = await session.request(
                Request(
                    "POST",
                    "https://wakatime.com/oauth/revoke",
                    data={
                        "client_id": config.client_id,
                        "client_secret": config.client_secret,
                        "token": access_token,
                    },
                )
            )
        cls._access_token_cache.pop(user_id)
        return response

    @classmethod
    async def get_user_info(cls, user_id: int) -> Users:
        """Get user's information"""
        access_token = await cls.get_access_token(user_id)
        async with driver.get_session() as session:
            response = await session.request(
                Request(
                    "GET",
                    f"{api_url}/users/current",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            )
            assert response.content
        return Users(**(json.loads(response.content)["data"]))

    @classmethod
    async def get_user_stats(
        cls, user_id: int, scope: TimeScope = "last_7_days"
    ) -> Stats:
        """Get user's coding activity.

        Args:
            user_id: user id
            scope: "last_7_days" "last_30_days" "last_6_months" "last_year" "all_time"
        """
        assess_token = await cls.get_access_token(user_id)
        async with driver.get_session() as session:
            response = await session.request(
                Request(
                    "GET",
                    f"{api_url}/users/current/stats/{scope}",
                    headers={"Authorization": f"Bearer {assess_token}"},
                )
            )
            assert response.content
        return Stats(**(json.loads(response.content)["data"]))

    @classmethod
    async def get_all_time_since_today(cls, user_id: int) -> str:
        """Get the total time logged since account created."""
        assess_token = await cls.get_access_token(user_id)
        async with driver.get_session() as client:
            response = await client.request(
                Request(
                    "GET",
                    f"{api_url}/users/current/all_time_since_today",
                    headers={"Authorization": f"Bearer {assess_token}"},
                )
            )
            assert response.content
        return json.loads(response.content)["data"]["text"]
