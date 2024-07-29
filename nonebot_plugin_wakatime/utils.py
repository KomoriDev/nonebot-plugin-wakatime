import base64
from pathlib import Path
from typing import Literal

import httpx


def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read())
        base64_message = base64_encoded_data.decode("utf-8")
    return "data:image/png;base64," + base64_message


async def get_lolicon_image() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.lolicon.app/setu/v2")
    return response.json()["data"][0]["urls"]["original"]


def calc_work_time_percentage(
    work_time: str, *, duration: Literal["day", "week", "month"] = "week"
):
    if duration == "day":
        total_minutes = 24 * 60
    elif duration == "week":
        total_minutes = 7 * 24 * 60
    else:
        total_minutes = 30 * 24 * 60

    parts = work_time.split()
    hours = int(parts[0])
    minutes = int(parts[2])

    total_work_minutes = hours * 60 + minutes

    percentage = (total_work_minutes / total_minutes) * 100

    return percentage
