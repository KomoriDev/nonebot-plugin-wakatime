from typing_extensions import TypedDict


class Categories(TypedDict):

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int


class Project(TypedDict):

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int


class Languages(TypedDict):
    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int
    seconds: int | None


class Editors(TypedDict):
    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int
    seconds: int | None


class Stats(TypedDict):

    human_readable_total: str
    human_readable_total_including_other_language: str
    daily_average: float
    daily_average_including_other_language: float
    human_readable_daily_average: str
    human_readable_daily_average_including_other_language: str
    categories: list[Categories] | None
    projects: list[Project] | None
    languages: list[Languages] | None
    editors: list[Editors] | None
    user_id: str
    username: str
