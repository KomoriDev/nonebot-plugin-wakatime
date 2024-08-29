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

    def to_uri(self) -> Url:
        if isinstance(self.uri, Path):
            uri = self.uri
            if not uri.is_absolute():
                uri = Path(localstore.get_plugin_data_dir() / uri)

            if uri.is_dir():
                # random pick a file
                files = [f for f in uri.iterdir() if f.is_file()]
                logger.debug(
                    f"CustomSource: {uri} is a directory, random pick a file: {files}"
                )
                return Url((uri / random.choice(files)).as_uri())

            if not uri.exists():
                raise FileNotFoundError(f"CustomSource: {uri} not exists")

            return Url(uri.as_uri())

        return self.uri


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


class Config(BaseModel):
    wakatime: ScopedConfig = Field(default_factory=ScopedConfig)
    """Wakatime Plugin Config"""


config = get_plugin_config(Config).wakatime
logger.debug(f"load plugin config: {config}")
