from typing import Any

from pydantic import BaseModel, ConfigDict


class Users(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    has_premium_features: bool
    display_name: str
    full_name: str
    email: str
    photo: str
    is_email_public: bool
    is_email_confirmed: bool
    public_email: str | None
    photo_public: bool
    timezone: str
    last_heartbeat_at: str
    last_plugin: str
    last_plugin_name: str
    last_project: str
    last_branch: str
    plan: str
    username: str
    website: str
    human_readable_website: str
    wonderfuldev_username: str | None
    github_username: str
    twitter_username: str
    linkedin_username: str
    city: dict[str, Any]
    logged_time_public: bool
    languages_used_public: bool
    is_hireable: bool
    created_at: str
    modified_at: str
