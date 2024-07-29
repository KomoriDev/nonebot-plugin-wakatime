from pydantic import BaseModel

from .stats import Stats as Stats
from .users import Users as Users


class WakaTime(BaseModel):
    user: Users
    stats: Stats
    all_time_since_today: str
