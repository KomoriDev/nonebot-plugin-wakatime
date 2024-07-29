<!-- markdownlint-disable MD033 MD036 MD041 MD045 -->
<div align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="./docs/NoneBotPlugin.svg" width="300" alt="logo">
  </a>
</div>

<div align="center">

# NoneBot-Plugin-Wakatime

_✨ NoneBot Wakatime 查询插件✨_

<a href="">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-wakatime.svg" alt="pypi"
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

在项目的配置文件中添加下表中的可选配置

> [!note]
> `client_id` 和 `client_secret` 均从 [WakaTime App](https://wakatime.com/apps) 获取

|             配置项             | 必填 |             默认值             |
|:---------------------------:|:--:|:---------------------------:|
|     wakatime__client_id     | 是  |              无              |
|   wakatime__client_secret   | 是  |              无              |
|      wakatime__api_url      | 否  | <https://wakatime.com/api/v1> |
| wakatime__background_source | 否  |           default           |

## 🎉 使用

> [!note]
> 请注意你的 `COMMAND_START` 以及上述配置项。

### 绑定账号

```shell
/wakatime -b|--bind|bind [code]
```

### 查询信息

```shell
/wakatime [@]
```

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
