from __future__ import annotations

from product_news.models import Article, utc_now_iso
from product_news.sources.base import ArticleSource


class SampleArticleSource(ArticleSource):
    def __init__(self, source_name: str = "产品喵") -> None:
        self.source_name = source_name

    def fetch_latest(self, limit: int = 10) -> list[Article]:
        article = Article(
            source=self.source_name,
            title="产品喵今日蹲点：海外独角兽情报待接入",
            url="https://mp.weixin.qq.com/",
            published_at=utc_now_iso(),
            summary="真实 RSS 接入前，产品喵先用这条示例内容演示桌面提醒。",
            id="sample-overseas-unicorn-latest",
        )
        return [article][:limit]
