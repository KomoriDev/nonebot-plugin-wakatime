import re
import base64
from pathlib import Path
from typing import Literal
from datetime import datetime, timedelta

import httpx

from .models import SubscriptionType
from .config import RESOURCES_DIR, CustomSource, config


def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read())
        base64_message = base64_encoded_data.decode("utf-8")
    return "data:image/png;base64," + base64_message


async def get_lolicon_image() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.lolicon.app/setu/v2")
    return response.json()["data"][0]["urls"]["original"]


async def get_background_image() -> str | Path:
    default_background = RESOURCES_DIR / "images" / "background.png"

    match config.background_source:
        case "default":
            background_image = default_background
        case "LoliAPI":
            background_image = "https://www.loliapi.com/acg/pe/"
        case "Lolicon":
            background_image = await get_lolicon_image()
        case CustomSource() as cs:
            background_image = cs.get()
            if not isinstance(background_image, Path):
                background_image = str(background_image)
        case _:
            background_image = default_background

    return background_image


def parse_time(work_time: str):
    patterns = {
        "hrs": r"(\d+)\s*hrs?",
        "mins": r"(\d+)\s*mins?",
        "secs": r"(\d+)\s*secs?",
    }

    hours = minutes = seconds = 0

    for key, pattern in patterns.items():
        match = re.search(pattern, work_time)
        if match:
            if key == "hrs":
                hours = int(match.group(1))
            elif key == "mins":
                minutes = int(match.group(1))
            elif key == "secs":
                seconds = int(match.group(1))

    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def calc_work_time_percentage(
    work_time: str, *, duration: Literal["day", "week", "month"] = "week"
):
    if duration == "day":
        total_minutes = 24 * 60
    elif duration == "week":
        total_minutes = 7 * 24 * 60
    else:
        total_minutes = 30 * 24 * 60

    total_work_seconds = parse_time(work_time)
    total_work_minutes = total_work_seconds / 60

    percentage = (total_work_minutes / total_minutes) * 100

    return percentage


def get_date_range(type: SubscriptionType) -> tuple[str, str]:
    today = datetime.now().date()

    if type == "weekly":
        last_week_end = today - timedelta(days=today.weekday() + 1)
        last_week_start = last_week_end - timedelta(days=6)
        start_date = last_week_start
        end_date = last_week_end

    elif type == "monthly":
        first_day_of_current_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        start_date = first_day_of_last_month
        end_date = last_day_of_last_month

    elif type == "yearly":
        first_day_of_current_year = today.replace(month=1, day=1)
        last_day_of_last_year = first_day_of_current_year - timedelta(days=1)
        first_day_of_last_year = last_day_of_last_year.replace(month=1, day=1)
        start_date = first_day_of_last_year
        end_date = last_day_of_last_year

    else:
        return "Unknown", "Unknown"

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
