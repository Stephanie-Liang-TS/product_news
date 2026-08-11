from __future__ import annotations

from abc import ABC, abstractmethod

from product_news.models import Article


class SourceError(RuntimeError):
    """Raised when a configured source cannot be read."""


class ArticleSource(ABC):
    @abstractmethod
    def fetch_latest(self, limit: int = 10) -> list[Article]:
        raise NotImplementedError

