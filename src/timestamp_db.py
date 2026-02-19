"""
timestamp_db.py
SQLite-backed storage for recipe usage timestamps.

Replaces the hand-rolled .tmstmp flat file. The DB is a single file
(e.g. recipe_time_stamps.db) that is created automatically on first use.

Schema
------
CREATE TABLE IF NOT EXISTS usage (
    recipe_name TEXT NOT NULL,
    used_on     TEXT NOT NULL,   -- ISO-8601 date: YYYY-MM-DD
    PRIMARY KEY (recipe_name, used_on)
);
"""
__author__ = 'Joe'

import datetime
import sqlite3
from pathlib import Path


_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS usage (
    recipe_name TEXT NOT NULL,
    used_on     TEXT NOT NULL,
    PRIMARY KEY (recipe_name, used_on)
);
"""


class TimestampDB:
    """
    Thin wrapper around the SQLite usage database.

    Uses a single persistent connection that is properly closed via
    close() / the context-manager protocol, preventing ResourceWarning
    about unclosed database connections.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        # Accept legacy .tmstmp paths by redirecting to a .db sibling
        if self.db_path.suffix == ".tmstmp":
            self.db_path = self.db_path.with_suffix(".db")
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Context-manager support  (with TimestampDB(...) as db: ...)
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self) -> None:
        """Explicitly close the underlying SQLite connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def record_usage(
        self,
        recipe_name: str,
        date: datetime.date = datetime.date.today(),
    ) -> None:
        """Insert or ignore a (recipe_name, date) usage record."""
        self._conn.execute(
            "INSERT OR IGNORE INTO usage (recipe_name, used_on) VALUES (?, ?)",
            (recipe_name, date.isoformat()),
        )
        self._conn.commit()

    def get_recipes_used_since(self, cutoff: datetime.date) -> set[str]:
        """Return names of recipes used on or after *cutoff*."""
        rows = self._conn.execute(
            "SELECT DISTINCT recipe_name FROM usage WHERE used_on >= ?",
            (cutoff.isoformat(),),
        ).fetchall()
        return {row[0] for row in rows}

    def get_all_usage(self) -> list[tuple[str, datetime.date]]:
        """Return all (recipe_name, date) rows, newest first."""
        rows = self._conn.execute(
            "SELECT recipe_name, used_on FROM usage ORDER BY used_on DESC"
        ).fetchall()
        return [(name, datetime.date.fromisoformat(d)) for name, d in rows]

    def get_last_used(self, recipe_name: str) -> datetime.date | None:
        """Return the most recent date *recipe_name* was used, or None."""
        row = self._conn.execute(
            "SELECT MAX(used_on) FROM usage WHERE recipe_name = ?",
            (recipe_name,),
        ).fetchone()
        return datetime.date.fromisoformat(row[0]) if row and row[0] else None

    # ------------------------------------------------------------------
    # Migration helper
    # ------------------------------------------------------------------
    @classmethod
    def migrate_from_tmstmp(cls, tmstmp_path: str | Path, db_path: str | Path) -> "TimestampDB":
        """
        One-time import of an old .tmstmp flat file into a new SQLite DB.
        File format expected:  <recipe_name>: YYYY-MM-DD
        """
        db = cls(db_path)
        tmstmp_path = Path(tmstmp_path)
        if not tmstmp_path.exists():
            return db

        with tmstmp_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    name_part, date_part = line.split(":", 1)
                    recipe_name = name_part.strip()
                    date        = datetime.date.fromisoformat(date_part.strip())
                    db.record_usage(recipe_name, date)
                except (ValueError, TypeError):
                    print(f"[migrate] Skipping unreadable line: {line!r}")

        print(f"[migrate] Imported {tmstmp_path} → {db.db_path}")
        return db
