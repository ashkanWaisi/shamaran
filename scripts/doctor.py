"""Run Shamaran diagnostics from a source checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shamaran.config import Settings  # noqa: E402
from shamaran.doctor import run_checks  # noqa: E402


def main() -> int:
    print("Shamaran Doctor\n")
    checks = run_checks(Settings())
    for check in checks:
        print(f"{'OK' if check.ok else 'FAIL'} {check.name}: {check.detail}")
    print("\nSystem ready." if all(check.ok for check in checks) else "\nSome checks need attention.")
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
