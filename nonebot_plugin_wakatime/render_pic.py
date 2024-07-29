from datetime import datetime

from nonebot_plugin_htmlrender import template_to_pic

from .shema import WakaTime
from .config import RESOURCES_DIR, TEMPLATES_DIR, config
from .utils import image_to_base64, get_lolicon_image, calc_work_time_percentage


async def render(data: WakaTime) -> bytes:

    data.user.created_at = datetime.strptime(
        data.user.created_at, "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%b %d %Y")

    default_background = RESOURCES_DIR / "images" / "background.png"

    if config.background_source == "default":
        background_image = image_to_base64(default_background)
    elif config.background_source == "LoliApi":
        background_image = "https://www.loliapi.com/acg/pe/"
    else:
        background_image = await get_lolicon_image()

    return await template_to_pic(
        template_path=str(TEMPLATES_DIR),
        template_name="profile.html",
        templates={
            "user": data.user,
            "background_image": background_image,
            "insights": {
                "data": data.stats,
                "last_week": calc_work_time_percentage(data.stats.human_readable_total),
                "daily_average": calc_work_time_percentage(
                    data.stats.human_readable_daily_average, duration="day"
                ),
            },
            "editors": data.stats.editors,
            "languages": data.stats.languages,
            "all_time_since_today": data.all_time_since_today,
        },
        pages={
            "viewport": {"width": 550, "height": 800},
            "base_url": f"file://{TEMPLATES_DIR}",
        },
    )
