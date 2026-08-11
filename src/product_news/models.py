from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class Article:
    source: str
    title: str
    url: str
    published_at: str | None = None
    summary: str | None = None
    id: str | None = None

    def stable_id(self) -> str:
        if self.id:
            return self.id
        key = f"{self.source}|{self.url or self.title}".encode()
        return hashlib.sha256(key).hexdigest()[:24]

    @property
    def display_time(self) -> str:
        return self.published_at or "时间待确认"
