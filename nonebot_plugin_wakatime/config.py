from pathlib import Path
from typing import Literal

from nonebot import logger
from pydantic_core import Url
from pydantic import Field, BaseModel
from nonebot.plugin import get_plugin_config

RESOURCES_DIR: Path = Path(__file__).parent / "resources"
TEMPLATES_DIR: Path = RESOURCES_DIR / "templates"


class CustomSource(BaseModel):
    uri: Url | Path

    def to_uri(self) -> Url:
        if isinstance(self.uri, Path):
            return Url(f"file://{self.uri}")
        return self.uri


class ScopedConfig(BaseModel):

    client_id: str = ""
    """Your App ID from https://wakatime.com/apps"""
    client_secret: str = ""
    """Your App Secret from https://wakatime.com/apps"""
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
