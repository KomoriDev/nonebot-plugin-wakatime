from typing import TYPE_CHECKING, cast

from yarl import URL
from nonebot import logger
from nonebot import get_driver as get_nonebot_driver
from nonebot.drivers import ASGIMixin, HTTPClientMixin

from .config import config as wakatime_config

driver = get_nonebot_driver()

plugin_enable = True
mountable = True

client_id = wakatime_config.client_id
client_secret = wakatime_config.client_secret
redirect_uri = wakatime_config.redirect_uri

if not client_id or not client_secret or not redirect_uri:
    plugin_enable = False
    mountable = False
    logger.error("缺失必要配置项，已禁用该插件")

elif not isinstance(driver, HTTPClientMixin):
    plugin_enable = False
    mountable = False
    raise RuntimeError("Driver must be HTTPClientMixin")

elif not isinstance(driver, ASGIMixin):
    mountable = False
    logger.warning(
        "当前 NoneBot Driver 并非 ASGIMixin，"
        "无法挂载自动注册 wakatime code 的路由，需要手动绑定"
    )

# 当 redirect_uri 未设置或是 wakatime.com 域名时，无法挂载自动注册 wakatime code 的路由
elif not redirect_uri or (
    (host := URL(redirect_uri).host) and (host.endswith("wakatime.com"))
):
    mountable = False
    logger.warning(
        "redirect_uri 未设置或是 wakatime.com 域名，"
        "无法挂载自动注册 wakatime code 的路由，需要手动绑定"
    )


if TYPE_CHECKING:

    class Driver(HTTPClientMixin, ASGIMixin): ...

    driver = cast(Driver, driver)
