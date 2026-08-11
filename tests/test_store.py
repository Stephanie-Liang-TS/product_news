from product_news.models import Article
from product_news.store import ArticleStore


def test_store_deduplicates_articles(tmp_path) -> None:
    store = ArticleStore(tmp_path / "news.sqlite")
    article = Article(source="海外独角兽", title="A", url="https://example.com/a")

    first = store.upsert_many([article])
    second = store.upsert_many([article])

    assert len(first) == 1
    assert second == []
    assert store.latest()[0].title == "A"

