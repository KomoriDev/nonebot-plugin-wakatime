import random
from pathlib import Path
from typing import Literal

from nonebot import logger
from pydantic import Field
from pydantic import BaseModel
from pydantic import AnyUrl as Url
from nonebot.plugin import get_plugin_config
import nonebot_plugin_localstore as localstore

RESOURCES_DIR: Path = Path(__file__).parent / "resources"
TEMPLATES_DIR: Path = RESOURCES_DIR / "templates"


class CustomSource(BaseModel):
    uri: Url | Path

    def get(self) -> Url | Path:
        if not isinstance(self.uri, Path):
            return self.uri

        uri = self.uri
        if not uri.is_absolute():
            uri = localstore.get_plugin_data_dir() / uri

        if uri.is_dir():
            # pick a file randomly from the directory
            files = [f for f in uri.iterdir() if f.is_file()]
            if not files:
                raise FileNotFoundError(f"CustomSource: {uri} is empty")

            logger.debug(
                f"CustomSource: {uri} is a directory, random pick a file: {files}"
            )
            return uri / random.choice(files)

        if not uri.exists():
            raise FileNotFoundError(f"CustomSource: {uri} not exists")

        return uri


class ArgotConfig(BaseModel):
    command: str | None = "background"
    expire: int = 300


class ScopedConfig(BaseModel):
    client_id: str = ""
    """Your App ID from https://wakatime.com/apps"""
    client_secret: str = ""
    """Your App Secret from https://wakatime.com/apps"""
    register_route: str = "/wakatime/register"
    """Register Route"""
    redirect_uri: str = ""
    """Authorized Redirect URI in https://wakatime.com/apps"""
    api_url: str = "https://wakatime.com/api/v1"
    """wakatime api"""
    background_source: Literal["default", "LoliAPI", "Lolicon"] | CustomSource = "default"
    """Background Source"""
    enable_qq_button: bool = False
    """Whether to enable the QQ button"""


class Config(BaseModel):
    wakatime: ScopedConfig = Field(default_factory=ScopedConfig)
    """Wakatime Plugin Config"""
    wakatime_argot: ArgotConfig = Field(default_factory=ArgotConfig)
    """Wakatime Argot Config"""


config = get_plugin_config(Config).wakatime
argot_config = get_plugin_config(Config).wakatime_argot
logger.debug(f"load plugin config: {config}")
