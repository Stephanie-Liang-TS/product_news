# Architecture

## MVP Boundaries

- Local only, no backend service.
- SQLite stores dedupe state and article history.
- RSS is the first source adapter; sample source keeps the UI runnable before the real source is confirmed.
- PySide6 owns the desktop widget, popup list, and open-link interaction.
- APScheduler handles periodic polling inside the desktop process.

## Data Model

```mermaid
erDiagram
  ARTICLE {
    string id PK
    string source
    string title
    string url
    string published_at
    string summary
    string created_at
    bool notified
  }

  POLL_RUN {
    int id PK
    string source
    string started_at
    string finished_at
    int fetched_count
    int inserted_count
    string status
    string error
  }
```

## Sequence

```mermaid
sequenceDiagram
  participant User
  participant Widget
  participant Poller
  participant Source
  participant Store
  participant Browser

  User->>Widget: Click widget
  Widget->>Poller: refresh_now()
  Poller->>Source: fetch_latest()
  Source-->>Poller: articles
  Poller->>Store: upsert articles
  Store-->>Poller: new articles
  Poller-->>Widget: latest article + new count
  Widget-->>User: show popup
  User->>Widget: Click article
  Widget->>Browser: open original URL
```

## Review / Backup Points

- Source adapter is isolated behind `ArticleSource`, so 2n can swap Wechat2RSS, local WeChat export, or another public source without changing UI code.
- Store dedupe key is stable hash of source + URL/title, so fallback/sample data does not collide with future real feeds.
- UI can run with sample data, which protects tomorrow's demo from source instability.

