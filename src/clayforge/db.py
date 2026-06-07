"""
ClayForge DB — Clean, optional database connectors for SQLite and Postgres.

Zero boilerplate. Async-friendly. Production-ready. Works beautifully
with or without the [db] extra.

Philosophy (matches ClayForge spirit):
- SQLite "just works" with zero dependencies (stdlib sqlite3) — perfect for
  demos, prototypes, and many production internal tools.
- `pip install "clayforge[db]"` unlocks SQLModel + full async (aiosqlite)
  for both SQLite and Postgres.
- Postgres is first-class: just pass a postgresql+asyncpg:// URL. The same
  Database object + async_session() works transparently.
- Simple, consistent API that feels native: .query(), .execute(), context
  managers, optional ORM sessions. No ceremony.

Zero-boilerplate usage:

    from clayforge import db

    # SQLite (always available, instant)
    database = db.Database()  # defaults to sqlite:///./clayforge.db
    rows = database.query("SELECT * FROM users WHERE active = ?", (True,))

    # Postgres (production)
    # pip install asyncpg   (or let the [db] extra + SQLAlchemy handle driver)
    database = db.Database("postgresql+asyncpg://user:pass@localhost/myapp")

    async with database.async_session() as session:
        # full SQLAlchemy / SQLModel power
        ...

The identical Database instance works from @app.page functions, button
on_click handlers, custom FastAPI routes, and background tasks.
Everything stays optional and opt-in.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from collections.abc import Iterable
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Graceful optional dependencies (matches ClayForge viz/grok pattern)
# ---------------------------------------------------------------------------

_HAS_SQLMODEL = False
_HAS_AIOSQLITE = False
_SQLModel = None  # type: ignore
_AsyncSession = None  # type: ignore
_create_async_engine = None  # type: ignore

try:
    from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession  # type: ignore
    from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine  # type: ignore
    from sqlmodel import SQLModel as _SQLModel  # type: ignore

    _HAS_SQLMODEL = True
except Exception:
    # Users without [db] still get a fully working sync SQLite experience
    pass

try:
    import aiosqlite  # noqa: F401  # just for detection

    _HAS_AIOSQLITE = True
except Exception:
    pass


# ---------------------------------------------------------------------------
# Core: Database facade — pragmatic, high-quality, zero boilerplate
# ---------------------------------------------------------------------------


class Database:
    """
    Unified, delightful database helper for ClayForge apps.

    Supports the full spectrum with zero ceremony:
    - Pure stdlib SQLite (always available — "it just works")
    - SQLModel + async sessions when `pip install "clayforge[db]"` (aiosqlite + asyncpg)
    - Postgres via standard asyncpg driver URL (postgresql+asyncpg://...)

    Common patterns (all work from pages, handlers, or routes):

        database = Database()                                   # SQLite default
        users = database.query("SELECT * FROM users ORDER BY created DESC")

        with database.connect() as conn:
            conn.execute("INSERT INTO ...", params)

        # With [db] extra for modern async + ORM:
        async with database.async_session() as session:
            await session.execute(...)
    """

    def __init__(
        self,
        url: str | None = None,
        *,
        echo: bool = False,
        connect_args: dict[str, Any] | None = None,
    ) -> None:
        self._url = url or os.environ.get("CLAYFORGE_DB_URL") or "sqlite:///./clayforge.db"
        self.echo = echo
        self.connect_args = connect_args or {}

        # Internal
        self._sync_conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()  # for simple thread safety on sync sqlite
        self._async_engine: Any = None
        self._is_sqlite = self._url.startswith("sqlite")

        # Parse a friendly path for pure sqlite3 usage
        self._sqlite_path = self._extract_sqlite_path(self._url)

    # ------------------------------------------------------------------
    # Public convenience properties
    # ------------------------------------------------------------------

    @property
    def url(self) -> str:
        """The database URL being used."""
        return self._url

    @property
    def is_sqlite(self) -> bool:
        return self._is_sqlite

    # ------------------------------------------------------------------
    # Sync SQLite (stdlib — always works, "it just works")
    # ------------------------------------------------------------------

    def _extract_sqlite_path(self, url: str) -> str:
        """Convert sqlite:///... style URL to a filesystem path for sqlite3."""
        if url.startswith("sqlite:///"):
            path = url[10:]
            if path == ":memory:":
                return ":memory:"
            if path.startswith("./"):
                path = path[2:]
            return str(Path(path).resolve())
        if url.startswith("sqlite://"):
            # Handle sqlite:///:memory: etc.
            path = url[10:]
            return ":memory:" if path == "/:memory:" else str(Path(path.lstrip("/")).resolve())
        # Fallback: treat as path
        return str(Path(url).resolve())

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        """Context manager yielding a raw sqlite3 connection (always available)."""
        if not self._is_sqlite:
            raise RuntimeError(
                f"Direct .connect() currently supports SQLite only. "
                f"For Postgres use async patterns or install drivers.\n"
                f"URL: {self._url}"
            )

        with self._lock:
            if self._sqlite_path == ":memory:":
                conn = sqlite3.connect(":memory:", check_same_thread=False)
            else:
                # Ensure directory exists
                Path(self._sqlite_path).parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)

            conn.row_factory = sqlite3.Row  # Makes rows behave like dicts
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def execute(self, sql: str, params: tuple | dict[str, Any] = ()) -> int:
        """Execute a write (INSERT/UPDATE/DELETE). Returns rowcount."""
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            return cur.rowcount

    def query(self, sql: str, params: tuple | dict[str, Any] = ()) -> list[dict[str, Any]]:
        """Execute a SELECT and return list of dict-like rows."""
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def fetchone(self, sql: str, params: tuple | dict[str, Any] = ()) -> dict[str, Any] | None:
        """Return a single row as dict or None."""
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def fetchval(self, sql: str, params: tuple | dict[str, Any] = ()) -> Any:
        """Return the first column of the first row (scalar)."""
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            row = cur.fetchone()
            return row[0] if row else None

    # ------------------------------------------------------------------
    # Async-friendly (enabled by [db] extra)
    # ------------------------------------------------------------------

    def _ensure_async_engine(self) -> Any:
        """Lazily create an async engine when advanced features are used."""
        if not _HAS_SQLMODEL or _create_async_engine is None:
            raise ImportError(
                "Async database features require the optional [db] extra.\n\n"
                "Install with:\n"
                '    pip install "clayforge[db]"\n\n'
                "This gives you SQLModel + aiosqlite (and easy Postgres support)."
            )

        if self._async_engine is None:
            # Convert sync URL to async driver where sensible
            async_url = self._url
            if self._is_sqlite:
                # aiosqlite driver
                if "aiosqlite" not in async_url:
                    async_url = async_url.replace("sqlite:///", "sqlite+aiosqlite:///")
            # For postgres user should use postgresql+asyncpg://...

            self._async_engine = _create_async_engine(
                async_url,
                echo=self.echo,
                connect_args=self.connect_args,
            )
        return self._async_engine

    @contextmanager
    def session(self) -> Iterable[Any]:
        """
        Synchronous session context (SQLModel if available, otherwise falls back
        to raw connection wrapper).

        Recommended for most page renders and simple handlers.
        """
        if _HAS_SQLMODEL and _SQLModel is not None:
            # SQLModel sync engine path (works great with sqlite)
            from sqlmodel import Session as _Session  # type: ignore

            engine = self._get_sync_sqlmodel_engine()
            with _Session(engine) as session:
                yield session
        else:
            # Beautiful fallback: expose the raw sqlite connection
            with self.connect() as conn:
                yield conn

    @asynccontextmanager
    async def async_session(self):
        """
        Proper async context manager for SQLModel/SQLAlchemy async sessions.

        Beautiful DX (requires the [db] extra):

            async with database.async_session() as session:
                result = await session.execute(select(User))
                await session.commit()

        Works for SQLite (via aiosqlite) and Postgres (via asyncpg):

            # Postgres example (install asyncpg or let [db] + URL handle it)
            db = Database("postgresql+asyncpg://user:pass@host:5432/mydb")
            async with db.async_session() as session:
                ...
        """
        if not (_HAS_SQLMODEL and _AsyncSession is not None and _create_async_engine is not None):
            raise ImportError(
                "database.async_session() requires the optional [db] extra.\n\n"
                '    pip install "clayforge[db]"\n\n'
                "Enables full async support with aiosqlite + asyncpg."
            )

        engine = self._ensure_async_engine()
        session = _AsyncSession(engine)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def _get_sync_sqlmodel_engine(self) -> Any:
        """Create (or reuse) a sync SQLModel engine."""
        # We create a lightweight sync engine for the SQLModel path
        from sqlalchemy import create_engine  # type: ignore

        sync_url = self._url
        if self._is_sqlite and "aiosqlite" in sync_url:
            sync_url = sync_url.replace("+aiosqlite", "")

        return create_engine(sync_url, echo=self.echo, connect_args=self.connect_args)

    # ------------------------------------------------------------------
    # Convenience: quick table helpers (great for examples and prototypes)
    # ------------------------------------------------------------------

    def init_sqlite_schema(self, schema_sql: str) -> None:
        """Run a multi-statement schema script (perfect for examples)."""
        if not self._is_sqlite:
            raise RuntimeError("init_sqlite_schema is SQLite-only for simplicity.")

        with self.connect() as conn:
            conn.executescript(schema_sql)

    # ------------------------------------------------------------------
    # Introspection / debugging
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        driver = "sqlite (stdlib)" if self._is_sqlite else "postgres/custom"
        extra = " + SQLModel" if _HAS_SQLMODEL else ""
        return f"<ClayForgeDB url={self._url!r} driver={driver}{extra}>"


# ---------------------------------------------------------------------------
# Module-level default instance for the ultimate zero-boilerplate experience
# Users can do: from clayforge.db import db
# Then db.query(...) immediately.
# ---------------------------------------------------------------------------

_default_db: Database | None = None


def get_default_db() -> Database:
    """Return (and lazily create) the process-wide default Database."""
    global _default_db
    if _default_db is None:
        _default_db = Database()
    return _default_db


# Allow beautiful usage:
#   from clayforge.db import db
#   rows = db.query(...)
db: Database = get_default_db()  # type: ignore  # reassigned at runtime but works for import


# ---------------------------------------------------------------------------
# Optional: easy model base when SQLModel is available
# ---------------------------------------------------------------------------


def get_model_base():
    """Return SQLModel (if installed) so users can define nice ORM models."""
    if _HAS_SQLMODEL and _SQLModel is not None:
        return _SQLModel
    raise ImportError(
        "SQLModel models require the optional dependency.\n"
        'Install with: pip install "clayforge[db]"'
    )


# Re-export a few nice names
__all__ = [
    "Database",
    "db",
    "get_default_db",
    "get_model_base",
    "_HAS_SQLMODEL",
]
