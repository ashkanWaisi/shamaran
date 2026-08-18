"""Small, allowlisted desktop launcher with explicit confirmation."""

import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from .base import BaseTool, SafetyLevel, ToolResult


DesktopTarget = Literal[
    "computer",
    "home",
    "desktop",
    "documents",
    "downloads",
    "calculator",
    "notepad",
    "settings",
]


class DesktopOpenInput(BaseModel):
    target: DesktopTarget


class DesktopOpenTool(BaseTool):
    name = "desktop.open"
    description = (
        "Open one visible, allowlisted desktop destination or app after confirmation. "
        "Targets: computer (My Computer/This PC), home, desktop, documents, downloads, "
        "calculator, notepad, or settings."
    )
    input_model = DesktopOpenInput
    safety_level = SafetyLevel.CONFIRM

    def __init__(self, confirm: Callable[[str], bool] | None = None) -> None:
        self.confirm = confirm or (lambda _message: False)

    @staticmethod
    def command(target: DesktopTarget, system: str | None = None) -> list[str] | None:
        system = system or platform.system()
        home = Path.home()
        folders = {
            "home": home,
            "desktop": home / "Desktop",
            "documents": home / "Documents",
            "downloads": home / "Downloads",
        }
        if system == "Windows":
            windows = {
                "computer": ["explorer.exe", "shell:MyComputerFolder"],
                "calculator": ["calc.exe"],
                "notepad": ["notepad.exe"],
                "settings": ["explorer.exe", "ms-settings:"],
            }
            return windows.get(target) or ["explorer.exe", str(folders[target])]
        if system == "Darwin":
            apps = {"calculator": "Calculator", "notepad": "TextEdit", "settings": "System Settings"}
            if target in apps:
                return ["open", "-a", apps[target]]
            return ["open", str(home if target == "computer" else folders[target])]
        if target in folders or target == "computer":
            return ["xdg-open", str(home if target == "computer" else folders[target])]
        return None

    def execute(self, arguments: DesktopOpenInput) -> ToolResult:
        command = self.command(arguments.target)
        if command is None:
            return ToolResult(
                ok=False,
                summary=f"{arguments.target} is unavailable on this operating system",
            )
        if not self.confirm(f"Shamaran wants to open {arguments.target}. Continue?"):
            return ToolResult(ok=False, summary="Desktop action was not approved")
        try:
            subprocess.Popen(
                command,
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            return ToolResult(ok=False, summary="Could not open desktop target", error=str(exc))
        return ToolResult(
            ok=True,
            summary=f"Opened {arguments.target}",
            data={"target": arguments.target},
        )
