from __future__ import annotations

import argparse
import os
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from product_news.app.main import NewsWidget, _build_poller
from product_news.config import Settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the desktop widget to a screenshot.")
    parser.add_argument("--output", default="/tmp/product_news_smoke.png")
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication([])
    settings = Settings.from_env(Path(".env"))
    widget = NewsWidget(
        settings=settings,
        poller=_build_poller(settings),
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
    widget.refresh(notifier=None)
    app.processEvents()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    saved = widget.window.grab().save(str(output))
    print(
        {
            "screenshot": str(output),
            "saved": saved,
            "size": (widget.window.width(), widget.window.height()),
            "title": widget.title.text(),
            "status": widget.status.text(),
        }
    )
    QTimer.singleShot(0, app.quit)
    app.exec()
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
