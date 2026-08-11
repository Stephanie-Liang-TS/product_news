from __future__ import annotations

from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from product_news.models import Article
from product_news.sources.base import ArticleSource, SourceError


class RssArticleSource(ArticleSource):
    def __init__(self, source_name: str, rss_url: str, timeout_seconds: int = 15) -> None:
        self.source_name = source_name
        self.rss_url = rss_url
        self.timeout_seconds = timeout_seconds

    def fetch_latest(self, limit: int = 10) -> list[Article]:
        if not self.rss_url:
            return []
        try:
            return self._fetch_with_feedparser(limit)
        except ImportError:
            return self._fetch_with_stdlib(limit)
        except Exception as exc:  # pragma: no cover - defensive boundary for remote feeds
            raise SourceError(f"Failed to fetch RSS source: {exc}") from exc

    def _fetch_with_feedparser(self, limit: int) -> list[Article]:
        import feedparser

        parsed = feedparser.parse(self.rss_url)
        if parsed.bozo and getattr(parsed, "bozo_exception", None):
            raise SourceError(str(parsed.bozo_exception))
        articles: list[Article] = []
        for entry in parsed.entries[:limit]:
            articles.append(
                Article(
                    source=self.source_name,
                    title=_read_attr(entry, "title", "Untitled"),
                    url=_read_attr(entry, "link", ""),
                    published_at=_read_attr(entry, "published", None)
                    or _read_attr(entry, "updated", None),
                    summary=_read_attr(entry, "summary", None),
                    id=_read_attr(entry, "id", None),
                )
            )
        return articles

    def _fetch_with_stdlib(self, limit: int) -> list[Article]:
        request = Request(self.rss_url, headers={"User-Agent": "OpenMaxProductNews/0.1"})
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read()
        except URLError as exc:
            raise SourceError(f"Failed to fetch RSS source: {exc}") from exc

        root = ElementTree.fromstring(payload)
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        articles: list[Article] = []
        for item in items[:limit]:
            title = _find_text(item, "title") or "Untitled"
            url = _find_text(item, "link") or _find_attr(item, "link", "href") or ""
            published = _find_text(item, "pubDate") or _find_text(item, "updated")
            articles.append(
                Article(
                    source=self.source_name,
                    title=title,
                    url=url,
                    published_at=_normalize_rss_time(published),
                    summary=_find_text(item, "description") or _find_text(item, "summary"),
                    id=_find_text(item, "guid") or url,
                )
            )
        return articles


def _read_attr(entry: Any, key: str, default: str | None) -> str | None:
    if isinstance(entry, dict):
        return entry.get(key, default)
    return getattr(entry, key, default)


def _find_text(node: ElementTree.Element, name: str) -> str | None:
    for child in node.iter():
        if child.tag.split("}")[-1] == name and child.text:
            return child.text.strip()
    return None


def _find_attr(node: ElementTree.Element, name: str, attr: str) -> str | None:
    for child in node.iter():
        if child.tag.split("}")[-1] == name:
            value = child.attrib.get(attr)
            if value:
                return value
    return None


def _normalize_rss_time(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value

