import respx
import httpx
import yarl


@respx.mock
async def test_user_bind():
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
