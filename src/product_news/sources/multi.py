from __future__ import annotations

from dataclasses import dataclass

from product_news.models import Article
from product_news.sources.base import ArticleSource, SourceError
from product_news.sources.rss import RssArticleSource


@dataclass(frozen=True)
class FeedDefinition:
    name: str
    url: str


DEFAULT_PUBLIC_FEEDS: tuple[FeedDefinition, ...] = (
    FeedDefinition("OpenAI News", "https://openai.com/news/rss.xml"),
    FeedDefinition("Product Hunt", "https://www.producthunt.com/feed"),
    FeedDefinition("Hacker News AI", "https://hnrss.org/newest?q=AI"),
    FeedDefinition("arXiv cs.AI", "https://export.arxiv.org/rss/cs.AI"),
    FeedDefinition("arXiv cs.CL", "https://export.arxiv.org/rss/cs.CL"),
)


class MultiFeedArticleSource(ArticleSource):
    def __init__(
        self,
        feeds: tuple[FeedDefinition, ...] = DEFAULT_PUBLIC_FEEDS,
        timeout_seconds: int = 15,
    ) -> None:
        self.feeds = feeds
        self.timeout_seconds = timeout_seconds

    def fetch_latest(self, limit: int = 10) -> list[Article]:
        feed_articles: list[list[Article]] = []
        errors: list[str] = []
        per_feed_limit = max(1, limit)

        for feed in self.feeds:
            try:
                source = RssArticleSource(feed.name, feed.url, self.timeout_seconds)
                feed_articles.append(source.fetch_latest(limit=per_feed_limit))
            except Exception as exc:
                errors.append(f"{feed.name}: {exc}")

        articles = _round_robin(feed_articles)
        if not articles and errors:
            raise SourceError("; ".join(errors))

        return _dedupe_articles(articles)[:limit]


def parse_feed_list(raw_value: str | None) -> tuple[FeedDefinition, ...]:
    if not raw_value:
        return DEFAULT_PUBLIC_FEEDS

    feeds: list[FeedDefinition] = []
    for index, raw_item in enumerate(raw_value.split(","), start=1):
        item = raw_item.strip()
        if not item:
            continue
        if "|" in item:
            name, url = item.split("|", 1)
        else:
            name, url = f"Feed {index}", item
        name = name.strip()
        url = url.strip()
        if name and url:
            feeds.append(FeedDefinition(name, url))
    return tuple(feeds) or DEFAULT_PUBLIC_FEEDS


def _dedupe_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    result: list[Article] = []
    for article in articles:
        key = article.stable_id()
        if key in seen:
            continue
        seen.add(key)
        result.append(article)
    return result


def _round_robin(article_groups: list[list[Article]]) -> list[Article]:
    result: list[Article] = []
    max_len = max((len(group) for group in article_groups), default=0)
    for index in range(max_len):
        for group in article_groups:
            if index < len(group):
                result.append(group[index])
    return result
