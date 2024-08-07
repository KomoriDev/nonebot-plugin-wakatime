from typing import NewType, NamedTuple

from nonebot import logger
from nonebot_plugin_user import User
from expiringdictx import ExpiringDict
from nonebot_plugin_orm import get_session
from nonebot_plugin_alconna.uniseg import Target
from nonebot.drivers import URL, Request, Response, HTTPServerSetup

from .apis import API
from .config import config
from .bootstrap import driver, mountable
from .render_pic import render_bind_result

State = NewType("State", str)


class WaitingRecord(NamedTuple):
    user: User
    target: Target


waiting_codes = ExpiringDict[State, WaitingRecord](capacity=100, default_age=300)


async def register_code_handler(req: Request):
    code = req.url.query.get("code")
    state = req.url.query.get("state")

    logger.debug(f"code: {code}, state: {state}")

    if code is None or state is None:
        return Response(400, content=await render_bind_result(400, "Bad Request."))

    record = waiting_codes.get(State(state))
    if record is None:
        return Response(
            404, content=await render_bind_result(404, "User Not Found or Expired.")
        )

    user_without_id = await API.bind_user(code)

    session = get_session()
    async with session.begin():
        session.add(user_without_id(id=record.user.id))
        await session.commit()

    await record.target.send("绑定成功！")

    return Response(200, content=await render_bind_result(200, "Bind OK."))


if mountable:
    logger.success("挂载 wakatime 自动注册路由")
    driver.setup_http_server(
        HTTPServerSetup(
            path=URL(config.register_route),
            method="GET",
            name="register_code",
            handle_func=register_code_handler,
        )
    )
