"""Workspace-confined filesystem operations."""

import os
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from shamaran.exceptions import WorkspaceSecurityError

from .base import BaseTool, SafetyLevel, ToolResult


ConfirmCallback = Callable[[str], bool]


class FilesystemSandbox:
    """Resolve paths canonically and prevent traversal or symlink escapes."""

    def __init__(self, workspace: Path, project_root: Path | None = None) -> None:
        self.workspace = workspace.expanduser().resolve()
        self.project_root = (project_root or Path.cwd()).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _inside(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def resolve(self, raw: str, *, write: bool = False) -> Path:
        if "\x00" in raw:
            raise WorkspaceSecurityError("NUL bytes are not valid in paths")
        project_scope = raw == "@project" or raw.startswith("@project/")
        if project_scope:
            if write:
                raise WorkspaceSecurityError("Project source is read-only")
            relative = raw.removeprefix("@project").lstrip("/\\")
            root = self.project_root
        else:
            relative = raw
            root = self.workspace

        candidate = Path(relative)
        if candidate.is_absolute():
            candidate = candidate.resolve(strict=False)
        else:
            candidate = (root / candidate).resolve(strict=False)
        if not self._inside(candidate, root):
            raise WorkspaceSecurityError(f"Path escapes allowed root: {raw}")

        # Existing parents are resolved above, which defeats symlink traversal.
        parent = candidate if candidate.exists() and candidate.is_dir() else candidate.parent
        if parent.exists() and not self._inside(parent.resolve(), root):
            raise WorkspaceSecurityError(f"Symlink escapes allowed root: {raw}")
        return candidate


class PathInput(BaseModel):
    path: str = Field(".", description="Workspace-relative path; @project/ is read-only")


class WriteInput(PathInput):
    content: str
    overwrite: bool = False


class ReplaceInput(PathInput):
    old: str
    new: str
    count: int = Field(0, ge=0)


class _FilesystemTool(BaseTool):
    def __init__(self, sandbox: FilesystemSandbox, confirm: ConfirmCallback | None = None):
        self.sandbox = sandbox
        self.confirm = confirm or (lambda _message: False)

    def _approved(self, message: str) -> bool:
        return self.confirm(message)


class ListTool(_FilesystemTool):
    name = "filesystem.list"
    description = "List a directory in the workspace or read-only @project scope."
    input_model = PathInput

    def execute(self, arguments: PathInput) -> ToolResult:
        path = self.sandbox.resolve(arguments.path)
        if not path.is_dir():
            return ToolResult(ok=False, summary="Directory not found", error=str(path))
        entries = [
            {"name": item.name, "type": "directory" if item.is_dir() else "file"}
            for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        ]
        return ToolResult(ok=True, summary=f"Listed {len(entries)} entries", data={"entries": entries})


class ReadTool(_FilesystemTool):
    name = "filesystem.read"
    description = "Read a UTF-8 text file in the workspace or read-only @project scope."
    input_model = PathInput

    def execute(self, arguments: PathInput) -> ToolResult:
        path = self.sandbox.resolve(arguments.path)
        if not path.is_file():
            return ToolResult(ok=False, summary="File not found", error=str(path))
        if path.stat().st_size > 1_000_000:
            return ToolResult(ok=False, summary="File exceeds 1 MB read limit")
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(ok=False, summary="File is not UTF-8 text")
        return ToolResult(ok=True, summary=f"Read {len(content)} characters", data={"content": content})


class WriteTool(_FilesystemTool):
    name = "filesystem.write"
    description = "Write a UTF-8 file inside the workspace. Requires confirmation."
    input_model = WriteInput
    safety_level = SafetyLevel.CONFIRM

    def execute(self, arguments: WriteInput) -> ToolResult:
        path = self.sandbox.resolve(arguments.path, write=True)
        if path.exists() and not arguments.overwrite:
            return ToolResult(ok=False, summary="File exists; set overwrite=true")
        if not self._approved(f"Write file {arguments.path}?"):
            return ToolResult(ok=False, summary="Write was not approved")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(arguments.content, encoding="utf-8")
        return ToolResult(ok=True, summary=f"Wrote {len(arguments.content)} characters")


class ReplaceTool(_FilesystemTool):
    name = "filesystem.replace"
    description = "Replace exact text inside a workspace file. Requires confirmation."
    input_model = ReplaceInput
    safety_level = SafetyLevel.CONFIRM

    def execute(self, arguments: ReplaceInput) -> ToolResult:
        path = self.sandbox.resolve(arguments.path, write=True)
        if not path.is_file():
            return ToolResult(ok=False, summary="File not found")
        content = path.read_text(encoding="utf-8")
        occurrences = content.count(arguments.old)
        if occurrences == 0:
            return ToolResult(ok=False, summary="Target text not found")
        if not self._approved(f"Replace text in {arguments.path}?"):
            return ToolResult(ok=False, summary="Replacement was not approved")
        updated = content.replace(arguments.old, arguments.new, arguments.count)
        path.write_text(updated, encoding="utf-8")
        return ToolResult(ok=True, summary=f"Replaced {occurrences if arguments.count == 0 else min(occurrences, arguments.count)} occurrence(s)")


class MkdirTool(_FilesystemTool):
    name = "filesystem.mkdir"
    description = "Create a directory inside the workspace. Requires confirmation."
    input_model = PathInput
    safety_level = SafetyLevel.CONFIRM

    def execute(self, arguments: PathInput) -> ToolResult:
        path = self.sandbox.resolve(arguments.path, write=True)
        if not self._approved(f"Create directory {arguments.path}?"):
            return ToolResult(ok=False, summary="Directory creation was not approved")
        path.mkdir(parents=True, exist_ok=True)
        return ToolResult(ok=True, summary="Directory created")


def filesystem_tools(sandbox: FilesystemSandbox, confirm: ConfirmCallback | None = None) -> list[BaseTool]:
    return [
        ListTool(sandbox, confirm),
        ReadTool(sandbox, confirm),
        WriteTool(sandbox, confirm),
        ReplaceTool(sandbox, confirm),
        MkdirTool(sandbox, confirm),
    ]
