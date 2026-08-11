# Product News 桌面小组件安装说明

## Mac 使用方法

1. 下载 `product-news-macos-apple-silicon` 或 `product-news-macos-intel` 压缩包。
2. 如果你的 Mac 是 M1/M2/M3/M4，优先选 Apple Silicon；如果是老款 Intel Mac，选 Intel。
3. 解压后，双击 `Product News.app`。
4. 桌面上出现「产品喵」小组件后，可以拖到顺手的位置。
5. 点「刷新」获取内容，点「打开原文」打开示例文章链接。
6. 不想用了，在菜单或 Dock 里退出应用。

## 现在 demo 会显示什么

当前先用示例内容，不等真实 RSS。

打开后你会看到一个小悬浮窗：

- 左边是产品喵头像。
- 右边是产品喵蹲到的示例情报。
- 底部有「刷新」和「打开原文」两个按钮。
- 内容暂时是示例文章，用来先验桌面形态和交互。

## 配置真实内容源

默认版本会显示示例内容，方便先看界面。

如果已经有 RSS 或 Wechat2RSS 地址：

1. 把 `.env.example` 复制一份，改名为 `.env`。
2. 打开 `.env`，把 `PRODUCT_NEWS_SOURCE` 改成 `rss`。
3. 把 `PRODUCT_NEWS_RSS_URL=` 后面填上真实 RSS 地址。
4. 重新打开 `Product News.app`。

## 如果打不开

- Mac 提示无法打开未知开发者应用：打开「系统设置」->「隐私与安全性」，允许打开 `Product News.app`。
- 双击后没看到窗口：看 Dock 里是否已有 Product News，或者用 Command+Tab 找一下。
- 内容一直是示例：说明还没有配置真实 RSS 地址，或 RSS 地址暂时不可访问。
- 公司电脑拦截应用：需要把压缩包或 app 发给 IT/管理员放行。

## 当前限制

- 当前是 MVP 版本，重点验证桌面展示、刷新、打开原文和 30 分钟定时轮询。
- 当前 demo 先用示例内容，真实「海外独角兽」RSS 后续再接。
- Mac `.app` 需要在 macOS 环境完成最终打包和真机验证。
- 更正式的 `.dmg`、代码签名、公证可以后续再加。
- 开机自启先不默认打开；Mac 真机验证通过后，可以加登录项或 LaunchAgent。

## Windows 备选

如果后续要给 Windows 用户试，可以下载 `product-news-windows`，解压后双击 `product-news.exe`。当前第一验收目标是 Mac。
