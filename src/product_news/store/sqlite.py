from __future__ import annotations

import sqlite3
from pathlib import Path

from product_news.models import Article, utc_now_iso


class ArticleStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT,
                    summary TEXT,
                    created_at TEXT NOT NULL,
                    notified INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS poll_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    fetched_count INTEGER NOT NULL DEFAULT 0,
                    inserted_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    error TEXT
                )
                """
            )

    def upsert_many(self, articles: list[Article]) -> list[Article]:
        inserted: list[Article] = []
        with self._connect() as conn:
            for article in articles:
                article_id = article.stable_id()
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO articles
                    (id, source, title, url, published_at, summary, created_at, notified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        article_id,
                        article.source,
                        article.title,
                        article.url,
                        article.published_at,
                        article.summary,
                        utc_now_iso(),
                    ),
                )
                if cursor.rowcount:
                    inserted.append(
                        Article(
                            id=article_id,
                            source=article.source,
                            title=article.title,
                            url=article.url,
                            published_at=article.published_at,
                            summary=article.summary,
                        )
                    )
        return inserted

    def latest(self, limit: int = 10) -> list[Article]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, source, title, url, published_at, summary
                FROM articles
                ORDER BY COALESCE(published_at, created_at) DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            Article(
                id=row["id"],
                source=row["source"],
                title=row["title"],
                url=row["url"],
                published_at=row["published_at"],
                summary=row["summary"],
            )
            for row in rows
        ]

    def mark_notified(self, article_ids: list[str]) -> None:
        if not article_ids:
            return
        placeholders = ",".join("?" for _ in article_ids)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE articles SET notified = 1 WHERE id IN ({placeholders})",
                article_ids,
            )

    def record_poll_run(
        self,
        source: str,
        started_at: str,
        fetched_count: int,
        inserted_count: int,
        status: str,
        error: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO poll_runs
                (source, started_at, finished_at, fetched_count, inserted_count, status, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (source, started_at, utc_now_iso(), fetched_count, inserted_count, status, error),
            )

