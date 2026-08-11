from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from product_news.config import Settings
from product_news.models import Article
from product_news.notifier import DesktopNotifier
from product_news.scheduler import ProductNewsPoller
from product_news.sources import RssArticleSource, SampleArticleSource
from product_news.store import ArticleStore


def _build_poller(settings: Settings) -> ProductNewsPoller:
    source = (
        RssArticleSource(settings.source_name, settings.rss_url)
        if settings.source == "rss" and settings.rss_url
        else SampleArticleSource(settings.source_name)
    )
    return ProductNewsPoller(
        source=source,
        store=ArticleStore(settings.db_path),
        source_name=settings.source_name,
    )


def main() -> int:
    try:
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QAction, QCursor, QIcon
        from PySide6.QtWidgets import (
            QApplication,
            QDialog,
            QHBoxLayout,
            QLabel,
            QMenu,
            QPushButton,
            QSystemTrayIcon,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        print("PySide6 is required for the desktop widget. Run: pip install -e .", file=sys.stderr)
        raise SystemExit(2) from exc

    settings = Settings.from_env(Path(".env"))
    poller = _build_poller(settings)

    app = QApplication(sys.argv)
    app.setApplicationName("产品喵")

    widget = NewsWidget(
        settings=settings,
        poller=poller,
        qt=Qt,
        widgets={
            "QWidget": QWidget,
            "QDialog": QDialog,
            "QVBoxLayout": QVBoxLayout,
            "QHBoxLayout": QHBoxLayout,
            "QLabel": QLabel,
            "QPushButton": QPushButton,
        },
    )
    widget.show()

    tray = QSystemTrayIcon(QIcon.fromTheme("help-about"), app)
    tray.setToolTip("产品喵")
    notifier = DesktopNotifier(tray)
    menu = QMenu()
    refresh_action = QAction("Refresh now", app)
    refresh_action.triggered.connect(lambda: widget.refresh(notifier))
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(refresh_action)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()

    widget.move(QCursor.pos())
    QTimer.singleShot(0, lambda: widget.refresh(notifier=None))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: widget.refresh(notifier),
        "interval",
        minutes=settings.poll_minutes,
        id="product-news-poll",
        replace_existing=True,
    )
    scheduler.start()
    app.aboutToQuit.connect(scheduler.shutdown)

    return app.exec()


class NewsWidget:
    def __init__(
        self,
        settings: Settings,
        poller: ProductNewsPoller,
        qt: object,
        widgets: dict[str, type],
    ) -> None:
        self.settings = settings
        self.poller = poller
        self.qt = qt
        self.widgets = widgets
        self.latest_article: Article | None = None
        self._drag_offset = None

        QWidget = widgets["QWidget"]
        QVBoxLayout = widgets["QVBoxLayout"]
        QHBoxLayout = widgets["QHBoxLayout"]
        QLabel = widgets["QLabel"]
        QPushButton = widgets["QPushButton"]

        self.window = QWidget()
        self.window.setWindowTitle("产品喵")
        self.window.setWindowFlags(qt.FramelessWindowHint | qt.WindowStaysOnTopHint | qt.Tool)
        self.window.setAttribute(qt.WA_TranslucentBackground, True)
        self.window.setFixedSize(360, 220)
        self.window.setStyleSheet(
            """
            QWidget {
                color: #292524;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }
            QWidget#surface {
                background: #fffaf0;
                border: 1px solid #fed7aa;
                border-radius: 18px;
            }
            QLabel#avatar {
                background: #fb923c;
                color: white;
                border: 3px solid #ffffff;
                border-radius: 30px;
                font-size: 17px;
                font-weight: 800;
            }
            QLabel#bubble {
                background: #ffffff;
                border: 1px solid #e7e5e4;
                border-radius: 12px;
                padding: 8px 10px;
            }
            QLabel#badge {
                color: #9a3412;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#title {
                color: #1c1917;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#meta {
                color: #57534e;
                font-size: 12px;
            }
            QPushButton {
                background: #0f172a;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 700;
            }
            QPushButton#secondary {
                background: #e7e5e4;
                color: #292524;
            }
            """
        )

        surface = QWidget()
        surface.setObjectName("surface")
        surface_layout = QVBoxLayout()
        surface_layout.setContentsMargins(14, 14, 14, 14)
        surface_layout.setSpacing(10)
        surface.setLayout(surface_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(surface)

        top = QHBoxLayout()
        top.setSpacing(10)
        self.avatar = QLabel("喵")
        self.avatar.setObjectName("avatar")
        self.avatar.setFixedSize(66, 66)
        self.avatar.setAlignment(self.qt.AlignCenter)

        bubble = QWidget()
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(4)
        bubble.setLayout(bubble_layout)

        self.badge = QLabel(self.settings.source_name)
        self.badge.setObjectName("badge")
        self.status = QLabel("准备刷新")
        self.status.setObjectName("meta")

        self.title = QLabel("产品喵蹲好了，点刷新看情报")
        self.title.setObjectName("title")
        self.title.setWordWrap(True)
        self.meta = QLabel("每 30 分钟巡逻一次")
        self.meta.setObjectName("meta")
        self.meta.setWordWrap(True)
        bubble_layout.addWidget(self.badge)
        bubble_layout.addWidget(self.title)
        bubble_layout.addWidget(self.meta)
        bubble_layout.addWidget(self.status)
        top.addWidget(self.avatar)
        top.addWidget(bubble, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.refresh_button = QPushButton("刷新")
        self.open_button = QPushButton("打开原文")
        self.open_button.setObjectName("secondary")
        self.refresh_button.clicked.connect(lambda: self.refresh())
        self.open_button.clicked.connect(self.open_latest)
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.open_button)

        surface_layout.addLayout(top)
        surface_layout.addStretch()
        surface_layout.addLayout(buttons)
        self.window.setLayout(layout)
        self.window.mouseDoubleClickEvent = lambda _event: self.open_latest()
        self.window.mousePressEvent = self._mouse_press
        self.window.mouseMoveEvent = self._mouse_move
        self.window.mouseReleaseEvent = self._mouse_release

    def show(self) -> None:
        self.window.show()

    def move(self, pos: object) -> None:
        self.window.move(pos)

    def refresh(self, notifier: DesktopNotifier | None = None) -> None:
        self.status.setText("刷新中")
        result = self.poller.refresh(limit=self.settings.max_items)
        if result.latest:
            self.latest_article = result.latest
            self.title.setText(result.latest.title)
            self.meta.setText(f"{result.latest.source} · {result.latest.display_time}")
            self.status.setText("已更新")
        elif result.error:
            self.status.setText("源异常")
            self.meta.setText(result.error)
        else:
            self.status.setText("暂无内容")
        if notifier and result.new_articles:
            notifier.notify_new_articles(result.new_articles)

    def open_latest(self) -> None:
        if self.latest_article and self.latest_article.url and self.settings.open_on_click:
            webbrowser.open(self.latest_article.url)

    def _mouse_press(self, event: object) -> None:
        if event.button() == self.qt.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            )

    def _mouse_move(self, event: object) -> None:
        if self._drag_offset is not None and event.buttons() & self.qt.LeftButton:
            self.window.move(event.globalPosition().toPoint() - self._drag_offset)

    def _mouse_release(self, _event: object) -> None:
        self._drag_offset = None
