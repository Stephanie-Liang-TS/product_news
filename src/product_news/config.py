from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from platformdirs import user_data_dir
except ImportError:  # pragma: no cover - only used before package installation

    def user_data_dir(appname: str, appauthor: str | None = None) -> str:
        return str(Path.home() / ".local" / "share" / appname)


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    source_name: str = "产品喵"
    source: str = "mock"
    rss_url: str | None = None
    feed_token: str | None = None
    poll_minutes: int = 30
    max_items: int = 10
    db_path: Path = Path(user_data_dir("OpenMaxProductNews", "OpenMax")) / "articles.db"
    open_on_click: bool = True

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> Settings:
        _load_dotenv(env_file or Path(".env"))
        rss_url = (
            os.getenv("PRODUCT_NEWS_RSS_URL", "").strip()
            or os.getenv("PN_FEED_URL", "").strip()
            or None
        )
        feed_token = (
            os.getenv("PRODUCT_NEWS_FEED_TOKEN", "").strip()
            or os.getenv("PN_FEED_TOKEN", "").strip()
            or None
        )
        source = (
            os.getenv("PRODUCT_NEWS_SOURCE", "").strip()
            or os.getenv("PN_SOURCE", "").strip()
            or ("rss" if rss_url else "mock")
        ).lower()
        source_name = (
            os.getenv("PRODUCT_NEWS_SOURCE_NAME", "").strip()
            or os.getenv("PN_ACCOUNT_NAME", "").strip()
            or "产品喵"
        )
        poll_minutes = int(
            os.getenv("PRODUCT_NEWS_POLL_MINUTES", "").strip()
            or os.getenv("PN_POLL_MINUTES", "").strip()
            or "30"
        )
        max_items = int(
            os.getenv("PRODUCT_NEWS_MAX_ITEMS", "").strip()
            or os.getenv("PN_MAX_ITEMS", "").strip()
            or "10"
        )
        return cls(
            source_name=source_name,
            source=source,
            rss_url=rss_url,
            feed_token=feed_token,
            poll_minutes=max(1, poll_minutes),
            max_items=max(1, max_items),
            db_path=Path(
                os.getenv("PRODUCT_NEWS_DB_PATH", "").strip()
                or Path(user_data_dir("OpenMaxProductNews", "OpenMax")) / "articles.db"
            ),
            open_on_click=_bool_env("PRODUCT_NEWS_OPEN_ON_CLICK", True),
        )
