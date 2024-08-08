from nonebug import App


async def test_bootstrap_and_mount(app: App):
    from nonebot_plugin_wakatime import bootstrap

    assert bootstrap.plugin_enable
    assert bootstrap.mountable
    assert bootstrap.client_id == "client_xxx_id"
    assert bootstrap.client_secret == "client_xxx_secret"
    assert bootstrap.redirect_uri == "https://xxx.com"
    assert bootstrap.driver
