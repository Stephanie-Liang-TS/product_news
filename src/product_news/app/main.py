from __future__ import annotations

import sys
import webbrowser
from importlib import resources
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
        from PySide6.QtGui import QAction, QGuiApplication, QIcon
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
    app.setQuitOnLastWindowClosed(False)
    icon = QIcon(_asset_path("product_meow_icon.png"))
    app.setWindowIcon(icon)

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

    tray = QSystemTrayIcon(icon, app)
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

    screen = QGuiApplication.primaryScreen()
    if screen:
        available = screen.availableGeometry()
        widget.move_to(
            available.right() - widget.width() - 28,
            available.top() + 86,
        )
    QTimer.singleShot(0, lambda: widget.refresh(notifier=None))
    keep_top_timer = QTimer()
    keep_top_timer.timeout.connect(widget.keep_on_top)
    keep_top_timer.start(3000)

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


def _asset_path(name: str) -> str:
    return str(resources.files("product_news.assets").joinpath(name))


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
        self.window.setWindowFlags(
            qt.FramelessWindowHint
            | qt.WindowStaysOnTopHint
            | qt.Tool
            | qt.NoDropShadowWindowHint
        )
        self.window.setAttribute(qt.WA_TranslucentBackground, True)
        self.window.setFixedSize(388, 246)
        self.window.setStyleSheet(
            """
            QWidget {
                color: #f8ead2;
                font-family: "Songti SC", "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
            }
            QWidget#surface {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff7de, stop:0.38 #552216, stop:1 #140908);
                border: 1px solid #d6a64e;
                border-radius: 22px;
            }
            QWidget#ornament {
                background: rgba(255, 244, 207, 0.10);
                border: 1px solid rgba(247, 211, 110, 0.42);
                border-radius: 18px;
            }
            QLabel#avatar {
                background: qradialgradient(cx:0.45, cy:0.32, radius:0.88,
                    fx:0.34, fy:0.24, stop:0 #fff4c8, stop:0.45 #d69435, stop:1 #42150f);
                color: #fff7df;
                border: 2px solid #f7d36e;
                border-radius: 38px;
                font-size: 24px;
                font-weight: 900;
            }
            QLabel#crest {
                color: #f7d36e;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0px;
            }
            QLabel#badge {
                color: #7a1d11;
                font-size: 12px;
                font-weight: 800;
            }
            QLabel#title {
                color: #fff8e7;
                font-size: 17px;
                font-weight: 900;
            }
            QLabel#meta {
                color: #f0d7ac;
                font-size: 12px;
            }
            QLabel#status {
                color: #a66f2b;
                background: rgba(255, 248, 231, 0.88);
                border: 1px solid rgba(247, 211, 110, 0.50);
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f7d36e, stop:1 #9f5a1d);
                color: #261109;
                border: none;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 900;
            }
            QPushButton#secondary {
                background: rgba(255, 248, 231, 0.88);
                color: #4a1d12;
                border: 1px solid rgba(247, 211, 110, 0.52);
            }
            """
        )

        surface = QWidget()
        surface.setObjectName("surface")
        surface_layout = QVBoxLayout()
        surface_layout.setContentsMargins(15, 14, 15, 15)
        surface_layout.setSpacing(12)
        surface.setLayout(surface_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(surface)

        top = QHBoxLayout()
        top.setSpacing(12)
        self.avatar = QLabel("喵")
        self.avatar.setObjectName("avatar")
        self.avatar.setFixedSize(78, 78)
        self.avatar.setAlignment(self.qt.AlignCenter)

        bubble = QWidget()
        bubble.setObjectName("ornament")
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(12, 10, 12, 10)
        bubble_layout.setSpacing(5)
        bubble.setLayout(bubble_layout)

        self.crest = QLabel("PRODUCT MEOW")
        self.crest.setObjectName("crest")
        self.badge = QLabel(self.settings.source_name)
        self.badge.setObjectName("badge")
        self.status = QLabel("准备刷新")
        self.status.setObjectName("status")

        self.title = QLabel("产品喵蹲好了，点刷新看情报")
        self.title.setObjectName("title")
        self.title.setWordWrap(True)
        self.meta = QLabel("每 30 分钟巡逻一次")
        self.meta.setObjectName("meta")
        self.meta.setWordWrap(True)
        bubble_layout.addWidget(self.crest)
        bubble_layout.addWidget(self.title)
        bubble_layout.addWidget(self.meta)
        bubble_layout.addWidget(self.status, alignment=self.qt.AlignLeft)
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
        self.keep_on_top()

    def move(self, pos: object) -> None:
        self.window.move(pos)

    def move_to(self, x: int, y: int) -> None:
        self.window.move(x, y)

    def width(self) -> int:
        return self.window.width()

    def keep_on_top(self) -> None:
        if self.window.isVisible():
            self.window.raise_()

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
