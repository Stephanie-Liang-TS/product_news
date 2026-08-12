from product_news.models import Article
from product_news.sources.multi import FeedDefinition, MultiFeedArticleSource, parse_feed_list
from product_news.sources.sample import SampleArticleSource


def test_sample_source_returns_demo_article() -> None:
    articles = SampleArticleSource("海外独角兽").fetch_latest()

    assert len(articles) == 1
    assert articles[0].source == "海外独角兽"
    assert articles[0].url.startswith("https://")


def test_article_stable_id_is_repeatable() -> None:
    article = Article(source="s", title="t", url="https://example.com/a")

    assert article.stable_id() == article.stable_id()


def test_parse_feed_list_supports_named_urls() -> None:
    feeds = parse_feed_list("OpenAI|https://example.com/rss.xml,https://example.com/plain.xml")

    assert feeds == (
        FeedDefinition("OpenAI", "https://example.com/rss.xml"),
        FeedDefinition("Feed 2", "https://example.com/plain.xml"),
    )


def test_multi_feed_interleaves_sources(monkeypatch) -> None:
    def fake_fetch(self, limit: int = 10) -> list[Article]:
        return [
            Article(
                source=self.source_name,
                title=f"{self.source_name} 1",
                url=f"{self.rss_url}/1",
            ),
            Article(
                source=self.source_name,
                title=f"{self.source_name} 2",
                url=f"{self.rss_url}/2",
            ),
        ]

    monkeypatch.setattr("product_news.sources.multi.RssArticleSource.fetch_latest", fake_fetch)
    source = MultiFeedArticleSource(
        (
            FeedDefinition("A", "https://example.com/a.xml"),
            FeedDefinition("B", "https://example.com/b.xml"),
        )
    )

    articles = source.fetch_latest(limit=10)

    assert [article.source for article in articles] == ["A", "B", "A", "B"]
