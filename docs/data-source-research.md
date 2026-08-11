# Data Source Research

## Current Conclusion

There is no confirmed free public feed covering the WeChat Official Account `海外独角兽`.

Recommended path for a real feed:

| Option | Cost | Dependency | Delay | Assessment |
| --- | --- | --- | --- | --- |
| Self-hosted Wechat2RSS with paid authorization | About RMB 150-200/year | Linux/Docker, no WeChat login | About 6h, no more than 24h | Preferred |
| Self-hosted we-mp-rss | Free | Docker plus WeChat QR login; account risk | Configurable | Fallback |
| Read local WeChat PC database | Free | Windows plus running WeChat; fragile key extraction | Near real time | Not recommended |

RSSHub's native WeChat routes are broadly unreliable, and WeWe-RSS is archived as of May 2026.

## MVP Decision

The desktop widget must not be blocked by real-source uncertainty:

- `PRODUCT_NEWS_SOURCE=mock` keeps click, popup, storage, and notification flow runnable with no network.
- `PRODUCT_NEWS_SOURCE=rss` plus `PRODUCT_NEWS_RSS_URL=<feed>` enables real RSS/Wechat2RSS with no code change.
- Compatibility aliases `PN_ACCOUNT_NAME`, `PN_SOURCE`, `PN_FEED_URL`, `PN_FEED_TOKEN`, `PN_POLL_MINUTES`, and `PN_MAX_ITEMS` are supported.
- SQLite defaults to the user's app data directory via `platformdirs`, so local article state does not live inside the repository or get bundled into releases.

## Open Decision

Stephanie needs to choose the real-source path:

- Prefer paid Wechat2RSS if the goal is low-maintenance and no personal WeChat login.
- Use we-mp-rss only if avoiding paid service is more important than account/login risk.
