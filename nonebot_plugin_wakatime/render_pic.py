from datetime import datetime

from nonebot_plugin_htmlrender import template_to_pic, template_to_html

from .schema import WakaTime
from .config import TEMPLATES_DIR
from .utils import calc_work_time_percentage


async def render(data: WakaTime) -> bytes:

    data["user"]["created_at"] = datetime.strptime(
        data["user"]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%b %d %Y")

    return await template_to_pic(
        template_path=str(TEMPLATES_DIR),
        template_name="profile.html",
        templates={
            "user": data["user"],
            "background_image": data["background_image"],
            "insights": {
                "data": data["stats"],
                "last_week": calc_work_time_percentage(
                    data["stats"]["human_readable_total"]
                ),
                "daily_average": calc_work_time_percentage(
                    data["stats"]["human_readable_daily_average"], duration="day"
                ),
            },
            "operating_systems": data["stats"]["operating_systems"],
            "editors": data["stats"]["editors"],
            "languages": data["stats"]["languages"],
            "all_time_since_today": data["all_time_since_today"],
        },
        pages={
            "viewport": {"width": 550, "height": 10},
            "base_url": f"file://{TEMPLATES_DIR}",
        },
    )


async def render_bind_result(status_code: int, content: str) -> str:

    result = "success" if status_code == 200 else "error"

    return await template_to_html(
        template_path=str(TEMPLATES_DIR),
        template_name=f"{result}.html.jinja2",
        status_code=status_code,
        content=content,
    )
