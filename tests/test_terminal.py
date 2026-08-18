import sys
from pathlib import Path

import pytest

from shamaran.exceptions import CommandBlockedError
from shamaran.tools.base import SafetyLevel
from shamaran.tools.terminal import CommandPolicy, TerminalTool


def test_allowlisted_command(tmp_path: Path) -> None:
    result = TerminalTool(tmp_path).invoke({"argv": ["git", "--version"]})
    assert result.ok
    assert result.data["exit_code"] == 0


@pytest.mark.parametrize("argv", [["rm", "-rf", "x"], ["git", "reset", "--hard"]])
def test_blocked_command(tmp_path: Path, argv: list[str]) -> None:
    with pytest.raises(CommandBlockedError):
        TerminalTool(tmp_path).invoke({"argv": argv})


@pytest.mark.parametrize("argv", [["git", "status", "&&", "whoami"], ["pytest", "|", "more"]])
def test_shell_bypass_blocked(argv: list[str]) -> None:
    assert CommandPolicy().classify(argv) is SafetyLevel.BLOCKED


def test_timeout(tmp_path: Path) -> None:
    script = tmp_path / "slow.py"
    script.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")
    result = TerminalTool(tmp_path, confirm=lambda _message: True).invoke(
        {"argv": [sys.executable, "slow.py"], "timeout": 0.05}
    )
    assert not result.ok
    assert "timed out" in result.summary


def test_exit_code_capture(tmp_path: Path) -> None:
    script = tmp_path / "fail.py"
    script.write_text("raise SystemExit(7)\n", encoding="utf-8")
    result = TerminalTool(tmp_path, confirm=lambda _message: True).invoke(
        {"argv": [sys.executable, "fail.py"]}
    )
    assert result.data["exit_code"] == 7
