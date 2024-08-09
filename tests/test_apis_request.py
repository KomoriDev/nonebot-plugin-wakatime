import yarl
import httpx
import respx
from nonebug import App
from pytest_mock import MockerFixture


@respx.mock
async def test_user_bind(app: App):
    from nonebot_plugin_wakatime.apis import API

    api_route = respx.post("https://wakatime.com/oauth/token").mock(
        httpx.Response(200, content="access_token=access_xxx_token")
    )

    partial_user = await API.bind_user("code_xxx")
    assert api_route.called
    assert partial_user(id=1).access_token == "access_xxx_token"

    request = api_route.calls.last.request

    assert request.method == "POST"
    assert request.url == "https://wakatime.com/oauth/token"
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"

    content = yarl.URL.build(
        query={
            "client_id": "client_xxx_id",
            "client_secret": "client_xxx_secret",
            "redirect_uri": "https%3A%2F%2Fxxx.com",
            "grant_type": "authorization_code",
            "code": "code_xxx",
        }
    ).query_string

    assert request.content == content.encode()


@respx.mock
async def test_revoke_token(app: App, mocker: MockerFixture):
    from nonebot_plugin_wakatime.apis import API

    mocker.patch(
        "nonebot_plugin_wakatime.API._access_token_cache",
        return_value={1: "access_xxx_token"},
    )

    mocker.patch(
        "nonebot_plugin_wakatime.API.get_access_token",
        return_value="access_xxx_token",
    )

    api_route = respx.post("https://wakatime.com/oauth/revoke").mock(
        httpx.Response(200, content="success=True")
    )

    await API.revoke_user_token(1)
    assert api_route.called

    request = api_route.calls.last.request

    assert request.method == "POST"
    assert request.url == "https://wakatime.com/oauth/revoke"
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"

    content = yarl.URL.build(
        query={
            "client_id": "client_xxx_id",
            "client_secret": "client_xxx_secret",
            "token": "access_xxx_token",
        }
    ).query_string

    assert request.content == content.encode()
