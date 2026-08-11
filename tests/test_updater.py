from product_news.updater import parse_update_payload


def test_parse_update_payload_finds_newer_apple_silicon_dmg() -> None:
    update = parse_update_payload(
        {
            "tag_name": "v0.1.5-demo",
            "html_url": "https://example.com/release",
            "assets": [
                {
                    "name": "product-news-macos-apple-silicon.dmg",
                    "browser_download_url": "https://example.com/app.dmg",
                }
            ],
        },
        "0.1.4-demo",
    )

    assert update is not None
    assert update.tag == "v0.1.5-demo"
    assert update.download_url == "https://example.com/app.dmg"


def test_parse_update_payload_ignores_current_version() -> None:
    update = parse_update_payload(
        {
            "tag_name": "v0.1.4-demo",
            "assets": [
                {
                    "name": "product-news-macos-apple-silicon.dmg",
                    "browser_download_url": "https://example.com/app.dmg",
                }
            ],
        },
        "0.1.4-demo",
    )

    assert update is None
