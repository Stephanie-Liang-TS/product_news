# OpenMax Product Desktop Tool

一个轻量 Mac 桌面小组件 MVP：产品喵，一只有个性的产品情报小猫。

## 当前目标

- 桌面展示一个轻量、可拖动的产品喵悬浮组件。
- 点击组件后展示最新文章标题、来源、时间和原文链接。
- 支持手动刷新。
- 支持拖动悬浮窗位置。
- 支持按配置定时轮询，发现新文章后弹出桌面提示。
- 数据源可插拔：demo 阶段先用 sample/fallback，真实 RSS/Wechat2RSS 后续接入。

## 本机运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m product_news
```

当前 demo 默认使用内置 sample 数据，便于先验收组件和交互，不阻塞真实内容源选择。

## 配置

| 变量 | 说明 |
| --- | --- |
| `PRODUCT_NEWS_SOURCE_NAME` | 来源名称，默认 `产品喵` |
| `PRODUCT_NEWS_SOURCE` | `mock` 或 `rss`，默认随 RSS 地址自动判断 |
| `PRODUCT_NEWS_RSS_URL` | RSS/Wechat2RSS 地址，空则使用 sample 源 |
| `PRODUCT_NEWS_FEED_TOKEN` | 可选 feed token，只从环境读取，不写入数据库 |
| `PRODUCT_NEWS_POLL_MINUTES` | 后台轮询间隔，默认 30 分钟 |
| `PRODUCT_NEWS_MAX_ITEMS` | 每次读取文章数量，默认 10 |
| `PRODUCT_NEWS_DB_PATH` | SQLite 数据库路径，留空则写入系统用户数据目录 |
| `PRODUCT_NEWS_OPEN_ON_CLICK` | 点击最新文章时是否打开原文 |

兼容早期变量：`PN_ACCOUNT_NAME`、`PN_SOURCE`、`PN_FEED_URL`、`PN_FEED_TOKEN`、`PN_POLL_MINUTES`、`PN_MAX_ITEMS`。如果同时配置，`PRODUCT_NEWS_*` 优先。

## Mac 打包

```bash
pip install -e ".[build]"
pyinstaller --noconfirm --clean --windowed --collect-all PySide6 --paths src --name "Product News" src/product_news/__main__.py
```

产物在 `dist/Product News.app`。面向普通用户交付时，把 `.app`、`.env.example` 和 `USER_INSTALL.md` 放进同一个 zip 包。

也可以在 GitHub Actions 手动触发 `build-macos` workflow，或推送 `v*` tag 后下载构建产物。构建会分别产出 Intel Mac 和 Apple Silicon Mac 两个 zip。

## 开机自启

MVP 默认不强制开机自启。Mac 真机验证通过后，可以再加一个 LaunchAgent 或登录项安装脚本，让产品喵开机后自动出现。

## Windows 备选打包

```bash
pip install -e ".[build]"
pyinstaller --noconfirm --onefile --windowed --collect-all PySide6 --paths src --name product-news src/product_news/__main__.py
```

产物在 `dist/product-news.exe`。后续可加图标、签名和自动启动配置。

也可以在 GitHub Actions 手动触发 `build-windows` workflow，或推送 `v*` tag 后下载构建产物。Windows 当前是备选路线，不是第一验收目标。

## 验证

```bash
pytest
ruff check src tests
QT_QPA_PLATFORM=offscreen python3 scripts/gui_smoke.py --output /tmp/product_news_smoke.png
```
