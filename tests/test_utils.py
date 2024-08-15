import json
import base64
from pathlib import Path

import httpx
import respx
import pytest
from pytest_mock import MockerFixture


def test_image_to_base64():
    from nonebot_plugin_wakatime.utils import image_to_base64

    test_image_path = Path(__file__).parent / "test_image.jpg"

    result = image_to_base64(test_image_path)

    with open(test_image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read())
        expected_base64_message = base64_encoded_data.decode("utf-8")

    expected_result = "data:image/png;base64," + expected_base64_message

    assert result == expected_result


@respx.mock
async def test_get_lolicon_image():
    from nonebot_plugin_wakatime.utils import get_lolicon_image

    with (Path(__file__).parent / "lolicon.json").open("r", encoding="utf8") as f:
        test_lolicon = json.load(f)

    route = respx.get("https://api.lolicon.app/setu/v2").mock(
        return_value=httpx.Response(200, json=test_lolicon)
    )

    lolicon_image = await get_lolicon_image()
    assert route.called
    assert (
        lolicon_image
        == "https: //i.pixiv.re/img-original/img/2022/05/14/13/17/34/98332818_p0.png"
    )  # noqa: E501

    request = route.calls.last.request

    assert request.method == "GET"
    assert request.url == "https://api.lolicon.app/setu/v2"


def test_parse_time():
    from nonebot_plugin_wakatime.utils import parse_time

    assert parse_time("2 hrs 30 mins 15 secs") == 2 * 3600 + 30 * 60 + 15

    assert parse_time("4 hrs") == 4 * 3600

    assert parse_time("45 mins") == 45 * 60

    assert parse_time("120 secs") == 120

    assert parse_time("10 mins 30 secs") == 10 * 60 + 30

    assert parse_time("") == 0

    assert parse_time("abc") == 0


def test_calc_work_time_percentage():
    from nonebot_plugin_wakatime.utils import calc_work_time_percentage

    assert (
        pytest.approx(calc_work_time_percentage("8 hrs", duration="day"), 0.01) == 33.33
    )  # noqa: E501

    assert (
        pytest.approx(calc_work_time_percentage("40 hrs", duration="week"), 0.01) == 23.81
    )  # noqa: E501

    assert (
        pytest.approx(calc_work_time_percentage("160 hrs", duration="month"), 0.01)
        == 22.22
    )  # noqa: E501

    assert pytest.approx(calc_work_time_percentage("40 hrs"), 0.01) == 23.81

    assert calc_work_time_percentage("0 hrs", duration="week") == 0.0


async def test_get_default_background_image(mocker: MockerFixture):
    from nonebot_plugin_wakatime.config import config
    from nonebot_plugin_wakatime.utils import get_background_image

    mocker.patch.object(config, "background_source", "default")

    assert config.background_source == "default"

    mocked_background = mocker.patch(
        "nonebot_plugin_wakatime.utils.image_to_base64",
        return_value="data:image/png;base64,xxxxxx",
    )

    background = await get_background_image()

    assert background == "data:image/png;base64,xxxxxx"

    mocked_background.assert_called_once()


async def test_get_loliapi_background_image(mocker: MockerFixture):
    from nonebot_plugin_wakatime.config import config
    from nonebot_plugin_wakatime.utils import get_background_image

    mocker.patch.object(config, "background_source", "LoliAPI")

    assert config.background_source == "LoliAPI"

    background = await get_background_image()

    assert background == "https://www.loliapi.com/acg/pe/"


async def test_get_lolicon_background_image(mocker: MockerFixture):
    from nonebot_plugin_wakatime.config import config
    from nonebot_plugin_wakatime.utils import get_background_image

    mocker.patch.object(config, "background_source", "Lolicon")

    assert config.background_source == "Lolicon"

    mocker.patch(
        "nonebot_plugin_wakatime.utils.get_lolicon_image",
        return_value="https: //i.pixiv.re/img-original/img/2022/05/14/13/17/34/1.png",
    )

    background = await get_background_image()

    assert (
        background == "https: //i.pixiv.re/img-original/img/2022/05/14/13/17/34/1.png"
    )  # noqa: E501
