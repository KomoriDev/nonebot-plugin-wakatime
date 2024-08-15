from sqlalchemy import Text
from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):

    __tablename__ = "wakatime"

    id: Mapped[int] = mapped_column(primary_key=True)
    """User ID"""
    access_token: Mapped[str] = mapped_column(Text)
    """Wakatime Access Token"""
