"""Reusable local installation diagnostics."""

import shutil
import sqlite3
import sys
from dataclasses import dataclass

from .config import Settings
from .providers.registry import default_provider_registry


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_checks(settings: Settings, check_ollama: bool = True) -> list[Check]:
    checks: list[Check] = []
    checks.append(Check("Python", sys.version_info >= (3, 11), sys.version.split()[0]))
    try:
        settings.ensure_directories()
        workspace = settings.workspace.resolve()
        probe = workspace / ".shamaran-doctor.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append(Check("Workspace", True, f"writable at {workspace}"))
    except OSError as exc:
        checks.append(Check("Workspace", False, str(exc)))
    checks.append(Check("SQLite", bool(sqlite3.sqlite_version), sqlite3.sqlite_version))
    git = shutil.which("git")
    checks.append(Check("Git", git is not None, git or "not found on PATH"))
    checks.append(Check("Directories", settings.memory_db.parent.exists(), "data and logs available"))
    if check_ollama:
        try:
            provider = default_provider_registry().create(settings)
            ok, detail = provider.health()
        except Exception as exc:
            ok, detail = False, str(exc)
        checks.append(Check("Ollama", ok, detail))
    return checks
