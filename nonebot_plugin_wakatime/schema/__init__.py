from typing_extensions import TypedDict

from .stats import Stats as Stats
from .users import Users as Users


class WakaTime(TypedDict):
    user: Users
    stats: Stats
    all_time_since_today: str
