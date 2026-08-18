"""Restricted subprocess execution without a command shell."""

import re
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from shamaran.exceptions import CommandBlockedError

from .base import BaseTool, SafetyLevel, ToolResult


class TerminalInput(BaseModel):
    argv: list[str] = Field(min_length=1, max_length=32)
    timeout: float = Field(30.0, gt=0, le=120)


class CommandPolicy:
    allowed = {"python", "python.exe", "python3", "python3.exe", "pytest", "pytest.exe", "git", "git.exe"}
    safe_git = {"status", "diff", "log", "branch", "--version"}
    confirm_git = {"add", "commit"}
    blocked_tokens = re.compile(r"[;&|`<>\n\r]|\$\(|%[A-Za-z_][A-Za-z0-9_]*%")
    blocked_commands = {
        "rm", "del", "rmdir", "sudo", "su", "shutdown", "reboot", "format",
        "diskpart", "mkfs", "curl", "wget", "powershell", "pwsh", "cmd",
    }

    def classify(self, argv: list[str]) -> SafetyLevel:
        if not argv or any(self.blocked_tokens.search(arg) for arg in argv):
            return SafetyLevel.BLOCKED
        command = Path(argv[0]).name.lower()
        if command in self.blocked_commands or command not in self.allowed:
            return SafetyLevel.BLOCKED
        if command in {"git", "git.exe"}:
            if len(argv) < 2:
                return SafetyLevel.BLOCKED
            subcommand = argv[1].lower()
            if subcommand in self.safe_git:
                return SafetyLevel.SAFE
            if subcommand in self.confirm_git:
                return SafetyLevel.CONFIRM
            return SafetyLevel.BLOCKED
        if command in {"python", "python.exe", "python3", "python3.exe"} and argv[1:] not in (["--version"], ["-V"]):
            return SafetyLevel.CONFIRM
        return SafetyLevel.SAFE


class TerminalTool(BaseTool):
    name = "terminal.run"
    description = "Run an allowlisted command as an argument array, without a shell."
    input_model = TerminalInput
    safety_level = SafetyLevel.CONFIRM

    def __init__(
        self,
        cwd: Path,
        confirm: Callable[[str], bool] | None = None,
        output_limit: int = 20_000,
    ) -> None:
        self.cwd = cwd.resolve()
        self.confirm = confirm or (lambda _message: False)
        self.output_limit = output_limit
        self.policy = CommandPolicy()

    def execute(self, arguments: TerminalInput) -> ToolResult:
        level = self.policy.classify(arguments.argv)
        display = " ".join(arguments.argv)
        if level is SafetyLevel.BLOCKED:
            raise CommandBlockedError(f"Command blocked by policy: {display}")
        if level is SafetyLevel.CONFIRM and not self.confirm(
            f"Shamaran wants to execute:\n\n{display}\n\nContinue?"
        ):
            return ToolResult(ok=False, summary="Command was not approved")
        started = time.monotonic()
        try:
            completed = subprocess.run(
                arguments.argv,
                cwd=self.cwd,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=arguments.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - started
            return ToolResult(ok=False, summary="Command timed out", data={"duration": duration}, error=str(exc))
        duration = time.monotonic() - started
        stdout = completed.stdout[: self.output_limit]
        stderr = completed.stderr[: self.output_limit]
        truncated = len(completed.stdout) > self.output_limit or len(completed.stderr) > self.output_limit
        return ToolResult(
            ok=completed.returncode == 0,
            summary=f"Command exited with code {completed.returncode}",
            data={
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": completed.returncode,
                "duration": round(duration, 3),
                "truncated": truncated,
            },
            error=None if completed.returncode == 0 else stderr or stdout,
        )
