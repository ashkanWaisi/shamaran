"""Small local SQLite memory store with explicit secret rejection."""

import re
import sqlite3
from pathlib import Path

from shamaran.exceptions import MemoryStoreError

from .models import MemoryRecord


_SENSITIVE = re.compile(
    r"(?i)(password\s*[:=]|api[_-]?key\s*[:=]|bearer\s+[a-z0-9._-]+|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-[a-z0-9_-]{16,})"
)


class SQLiteMemory:
    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    project TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )"""
                )
                connection.execute("CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project)")
        except sqlite3.Error as exc:
            raise MemoryStoreError(f"Could not initialize memory: {exc}") from exc

    @staticmethod
    def _record(row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord.model_validate(dict(row))

    def remember(self, content: str, category: str = "general", project: str | None = None) -> MemoryRecord:
        if _SENSITIVE.search(content):
            raise MemoryStoreError("Refusing to store content that looks like a credential")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO memories(category, content, project) VALUES (?, ?, ?)",
                (category, content, project),
            )
            row = connection.execute("SELECT * FROM memories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return self._record(row)

    def search(self, query: str, project: str | None = None, limit: int = 20) -> list[MemoryRecord]:
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        params: list[object] = [f"%{query}%"]
        if project is not None:
            sql += " AND project = ?"
            params.append(project)
        sql += " ORDER BY updated_at DESC, id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as connection:
            return [self._record(row) for row in connection.execute(sql, params).fetchall()]

    def list_recent(self, limit: int = 20) -> list[MemoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM memories ORDER BY updated_at DESC, id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._record(row) for row in rows]

    def forget(self, memory_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        return cursor.rowcount > 0

    def clear(self) -> int:
        with self._connect() as connection:
            count = connection.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            connection.execute("DELETE FROM memories")
        return int(count)

    def healthy(self) -> bool:
        try:
            with self._connect() as connection:
                return connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        except sqlite3.Error:
            return False
