from product_news.config import Settings


def test_settings_supports_short_env_aliases(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("PRODUCT_NEWS_RSS_URL", raising=False)
    monkeypatch.delenv("PRODUCT_NEWS_SOURCE", raising=False)
    monkeypatch.delenv("PRODUCT_NEWS_SOURCE_NAME", raising=False)
    monkeypatch.delenv("PRODUCT_NEWS_MAX_ITEMS", raising=False)
    monkeypatch.setenv("PN_SOURCE", "rss")
    monkeypatch.setenv("PN_FEED_URL", "https://example.com/feed.xml")
    monkeypatch.setenv("PN_ACCOUNT_NAME", "海外独角兽")
    monkeypatch.setenv("PN_MAX_ITEMS", "5")

    settings = Settings.from_env(tmp_path / "missing.env")

    assert settings.source == "rss"
    assert settings.rss_url == "https://example.com/feed.xml"
    assert settings.source_name == "海外独角兽"
    assert settings.max_items == 5
