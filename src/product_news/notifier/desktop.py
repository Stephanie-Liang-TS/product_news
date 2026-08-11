from __future__ import annotations

from product_news.models import Article


class DesktopNotifier:
    def __init__(self, tray_icon: object | None = None) -> None:
        self.tray_icon = tray_icon

    def notify_new_articles(self, articles: list[Article]) -> None:
        if not articles or self.tray_icon is None:
            return
        latest = articles[0]
        show_message = getattr(self.tray_icon, "showMessage", None)
        if callable(show_message):
            show_message(
                latest.source,
                f"{latest.title}\n要不要一起看看？",
                getattr(self.tray_icon, "Information", 1),
                8000,
            )

