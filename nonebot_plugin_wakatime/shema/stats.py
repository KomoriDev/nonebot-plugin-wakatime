from typing import Any

from pydantic import BaseModel, ConfigDict


class Categories(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int


class Project(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int


class Languages(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int
    seconds: int | None = None


class Editors(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    total_seconds: float
    percent: float
    digital: str
    decimal: str
    text: str
    hours: int
    minutes: int
    seconds: int | None = None


class Stats(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_seconds: float
    total_seconds_including_other_language: float
    human_readable_total: str
    human_readable_total_including_other_language: str
    daily_average: float
    daily_average_including_other_language: float
    human_readable_daily_average: str
    human_readable_daily_average_including_other_language: str
    categories: list[Categories] | None = None
    projects: list[Project] | None = None
    languages: list[Languages] | None = None
    editors: list[Editors] | None = None
    operating_systems: list[dict[str, Any]]
    dependencies: list[dict[str, Any]] | None = None
    machines: list[dict[str, Any]] | None = None
    best_day: dict[str, Any] | None = None
    range: str
    human_readable_range: str
    holidays: int
    days_including_holidays: int
    days_minus_holidays: int
    status: str
    percent_calculated: int
    is_already_updating: bool
    is_coding_activity_visible: bool
    is_other_usage_visible: bool
    is_stuck: bool
    is_including_today: bool
    is_up_to_date: bool
    start: str | None = None
    end: str | None = None
    timezone: str | None = None
    timeout: int
    writes_only: bool
    user_id: str
    username: str
    created_at: str | None = None
    modified_at: str | None = None
