from pathlib import Path

import pytest

from shamaran.exceptions import MemoryStoreError
from shamaran.memory import SQLiteMemory


def test_memory_lifecycle(tmp_path: Path) -> None:
    memory = SQLiteMemory(tmp_path / "memory.db")
    first = memory.remember("Uses PostgreSQL", "decision", "demo")
    memory.remember("Prefer readable Python", "preference")
    assert memory.search("PostgreSQL")[0].id == first.id
    assert len(memory.list_recent()) == 2
    assert memory.forget(first.id)
    assert memory.clear() == 1
    assert memory.list_recent() == []


def test_rejects_secrets(tmp_path: Path) -> None:
    memory = SQLiteMemory(tmp_path / "memory.db")
    with pytest.raises(MemoryStoreError):
        memory.remember("api_key=super-secret-value")
