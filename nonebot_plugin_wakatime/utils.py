import re
import base64
from pathlib import Path
from typing import Literal

import httpx
from pydantic import AnyUrl as Url

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


async def get_background_image() -> str | Url:

    default_background = RESOURCES_DIR / "images" / "background.png"

    match config.background_source:
        case "default":
            background_image = image_to_base64(default_background)
        case "LoliAPI":
            background_image = "https://www.loliapi.com/acg/pe/"
        case "Lolicon":
            background_image = await get_lolicon_image()
        case CustomSource() as cs:
            background_image = cs.to_uri()
        case _:
            background_image = image_to_base64(default_background)

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
