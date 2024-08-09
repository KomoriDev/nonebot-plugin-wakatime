<!-- markdownlint-disable MD033 MD036 MD041 MD045 -->
<div align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="./docs/NoneBotPlugin.svg" width="300" alt="logo">
  </a>
</div>

<div align="center">

# NoneBot-Plugin-Wakatime

_✨ NoneBot Wakatime 查询插件 ✨_

<a href="">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-wakatime.svg" alt="pypi" />
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fpdm-project%2F.github%2Fbadge.json" alt="pdm-managed">
</a>
<a href="https://github.com/nonebot/plugin-alconna">
  <img src="https://img.shields.io/badge/Alconna-resolved-2564C2" alt="alc-resolved">
</a>

</div>

## 📖 介绍

NoneBot Wakatime 查询插件。将你的代码统计嵌入 Bot 中

## 💿 安装

以下提到的方法任选 **其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 Bot 的根目录下打开命令行, 输入以下指令即可安装

```shell
nb plugin install nonebot-plugin-wakatime
```

</details>
<details>
<summary>使用包管理器安装</summary>

```shell
pip install nonebot-plugin-wakatime
# or, use poetry
poetry add nonebot-plugin-wakatime
# or, use pdm
pdm add nonebot-plugin-wakatime
```

打开 NoneBot 项目根目录下的配置文件, 在 `[plugin]` 部分追加写入

```toml
plugins = ["nonebot_plugin_wakatime"]
```

</details>

## ⚙️ 配置

### 驱动器配置

Wakatime 插件需要项目支持客户端型驱动器，因此需要在配置文件中添加相关配置项。具体的配置方法可以参考[配置驱动器](https://nonebot.dev/docs/advanced/driver#配置驱动器)。

同时，如果项目还支持服务端型驱动器，则插件还可以通过配置项来自动注册用户。具体的配置方法可以参考[启用自动注册](#启用自动注册)。

下面是一个同时支持客户端/服务端型驱动器的配置示例：

```env
DRIVER=~fastapi+~httpx
```

### 插件配置

在项目的配置文件中添加下表中的可选配置

> [!note]
> `client_id` 和 `client_secret` 均从 [WakaTime App](https://wakatime.com/apps) 获取  
> `redirect_uri` 即绑定成功后跳转的页面。需先在 [WakaTime App](https://wakatime.com/apps) 配置才能使用（只配置一个即可）  
> 可使用`https://wakatime.com/oauth/test`或者参考 [启用自动注册](#启用自动注册)

|            配置项             | 必填 |            默认值             |
| :---------------------------: | :--: | :---------------------------: |
|     wakatime\_\_client_id     |  是  |              无               |
|   wakatime\_\_client_secret   |  是  |              无               |
|   wakatime\_\_redirect_uri    |  是  |              无               |
|      wakatime\_\_api_url      |  否  | <https://wakatime.com/api/v1> |
|  wakatime\_\_register_route   |  否  |      /wakatime/register       |
| wakatime\_\_background_source |  否  |            default            |

### 启用自动注册

如果 Nonebot driver 支持服务端型驱动器，可以通过以下配置项启用自动注册

- 假设 bot 所在服务器的域名为 `example.com`
- 假设 bot 的端口为 `8080`，并且已经开放
- 假设`wakatime__register_route` 为 `/wakatime/register`

则你可以在 `WakaTime App` 的 `redirect_uri` 中填写

```text
http://example.com:8080/wakatime/register
```

然后在配置文件中添加以下配置项

```env
wakatime__redirect_uri = https://example.com:8080/wakatime/register
```

> [!note]
> 如果域名支持 HTTPS，将 `http` 替换为 `https`  
> 如果你想直接使用服务器的 IP 地址（不推荐），可以将 `example.com` 替换为服务器的 IP 地址，并确保其为公网 IP

`wakatime__background_source` 为背景图来源，可选值为字面量`default`/`LoliAPI`/`Lolicon` 或者结构 `CustomSource` ，默认为 `default`。

可参见[自定义背景图](#自定义背景图)

## 🎉 使用

> [!note]
> 假设你的命令前缀为 `/`  
> 请检查你的 `COMMAND_START` 以及上述配置项。

### 绑定账号

首次绑定时向 Bot 发送 `/wakatime bind`，跟随链接指引进行绑定，成功后会跳转到 `redirect_uri` 处

- 如果已经[启用自动注册](#启用自动注册)，则无需继续操作，bot 会自动在你访问绑定链接后注册用户并发送绑定成功消息
- 如果未启用自动注册，则需要手动绑定，复制访问后链接或者绑定页面中的 code 参数，发送 `/wakatime bind [code]` 绑定

### 解绑

```shell
/wakatime revoke
```

### 查询信息

```shell
/wakatime [@]
```

## 📸 效果图

默认背景图

<img src="./docs/rendering.png" height="500" alt="rendering"/>

### 自定义背景图

在配置文件中设置 `wakatime__background_source` 为 `CustomSource`结构的字典
  
  ```env
  wakatime__background_source = '{"url": "https://example.com/image.jpg"}'
  ```

其中
- `url` 可为网络图片 API，只要返回的是图片即可
- `url` 也可以为 base64 编码的图片，如 `data:image/png;base64,xxxxxx` ~（一般也没人这么干）~
- `url` 也可以为本地图片路径，如 `imgs/image.jpg`、`/path/to/image.jpg`
- 如果本地图片路径是相对路径，会使用 [`nonebot-plugin-localstore`](https://github.com/nonebot/plugin-localstore) 指定的 data 目录作为根目录
- 如果本地图片路径是目录，会随机选择目录下的一张图片作为背景图

## 📄 许可证

本项目使用 [MIT](./LICENSE) 许可证开源

```text
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
