"""Lightweight pre-commit secret scan. Not a replacement for a dedicated scanner."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", "work", "outputs"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer token": re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "OpenAI-style key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
}


def candidates() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        return [ROOT / line for line in result.stdout.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        return [
            path for path in ROOT.rglob("*")
            if path.is_file() and not SKIP_PARTS.intersection(path.relative_to(ROOT).parts)
        ]


def main() -> int:
    findings: list[str] = []
    for path in candidates():
        relative = path.relative_to(ROOT)
        if relative == Path("scripts/check_secrets.py"):
            continue
        if path.name == ".env":
            findings.append(f"{relative}: local .env file is included in scan scope")
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}: possible {label}")
    if findings:
        print("Shamaran secret check found suspicious content:")
        for finding in findings:
            print(f"- {finding}")
        print("Review these files before committing. No secret values were printed.")
        return 1
    print("Shamaran secret check: no obvious secrets found.")
    print("This lightweight scan does not replace a professional secret scanner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
