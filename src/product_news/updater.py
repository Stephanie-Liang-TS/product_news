from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass

GITHUB_LATEST_RELEASE_URL = (
    "https://api.github.com/repos/Stephanie-Liang-TS/product_news/releases/latest"
)
APPLE_SILICON_DMG = "product-news-macos-apple-silicon.dmg"


@dataclass(frozen=True)
class UpdateInfo:
    tag: str
    download_url: str
    release_url: str


def find_update(current_version: str, timeout: float = 8.0) -> UpdateInfo | None:
    request = urllib.request.Request(
        GITHUB_LATEST_RELEASE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Product-Meow-Updater",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_update_payload(payload, current_version)


def parse_update_payload(payload: dict[str, object], current_version: str) -> UpdateInfo | None:
    tag = str(payload.get("tag_name") or "")
    if not tag or _version_key(tag) <= _version_key(current_version):
        return None

    assets = payload.get("assets")
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if asset.get("name") == APPLE_SILICON_DMG and asset.get("browser_download_url"):
            return UpdateInfo(
                tag=tag,
                download_url=str(asset["browser_download_url"]),
                release_url=str(payload.get("html_url") or ""),
            )
    return None


def _version_key(version: str) -> tuple[int, ...]:
    parts = [int(part) for part in re.findall(r"\d+", version)]
    return tuple(parts or [0])
