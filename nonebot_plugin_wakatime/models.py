from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):

    __tablename__ = "wakatime"

    id: Mapped[str] = mapped_column(primary_key=True)
    """User ID"""
    access_token: Mapped[str]
    """Wakatime Access Token"""
