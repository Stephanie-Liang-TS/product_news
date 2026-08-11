from __future__ import annotations

from dataclasses import dataclass

from product_news.models import Article, utc_now_iso
from product_news.sources.base import ArticleSource
from product_news.store.sqlite import ArticleStore


@dataclass(frozen=True)
class PollResult:
    articles: list[Article]
    new_articles: list[Article]
    error: str | None = None

    @property
    def latest(self) -> Article | None:
        return self.articles[0] if self.articles else None


class ProductNewsPoller:
    def __init__(self, source: ArticleSource, store: ArticleStore, source_name: str) -> None:
        self.source = source
        self.store = store
        self.source_name = source_name

    def refresh(self, limit: int = 10) -> PollResult:
        started_at = utc_now_iso()
        try:
            articles = self.source.fetch_latest(limit=limit)
            new_articles = self.store.upsert_many(articles)
            self.store.record_poll_run(
                source=self.source_name,
                started_at=started_at,
                fetched_count=len(articles),
                inserted_count=len(new_articles),
                status="ok",
            )
            return PollResult(
                articles=articles or self.store.latest(limit),
                new_articles=new_articles,
            )
        except Exception as exc:  # pragma: no cover - UI boundary
            self.store.record_poll_run(
                source=self.source_name,
                started_at=started_at,
                fetched_count=0,
                inserted_count=0,
                status="error",
                error=str(exc),
            )
            return PollResult(articles=self.store.latest(limit), new_articles=[], error=str(exc))
