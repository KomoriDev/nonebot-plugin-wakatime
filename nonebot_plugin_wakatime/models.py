from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):

    __tablename__ = "wakatime"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    """User ID"""
    platform: Mapped[str]
    """User Account Platform"""
    access_token: Mapped[str]
    """Wakatime Access Token"""
