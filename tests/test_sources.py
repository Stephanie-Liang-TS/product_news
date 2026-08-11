from product_news.models import Article
from product_news.sources.sample import SampleArticleSource


def test_sample_source_returns_demo_article() -> None:
    articles = SampleArticleSource("海外独角兽").fetch_latest()

    assert len(articles) == 1
    assert articles[0].source == "海外独角兽"
    assert articles[0].url.startswith("https://")


def test_article_stable_id_is_repeatable() -> None:
    article = Article(source="s", title="t", url="https://example.com/a")

    assert article.stable_id() == article.stable_id()

