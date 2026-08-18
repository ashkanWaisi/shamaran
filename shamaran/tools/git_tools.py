"""Purpose-built Git wrappers; push and destructive operations are absent."""

import subprocess
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from shamaran.exceptions import GitToolError

from .base import BaseTool, SafetyLevel, ToolResult


class EmptyInput(BaseModel):
    pass


class DiffInput(BaseModel):
    staged: bool = False


class LogInput(BaseModel):
    limit: int = Field(10, ge=1, le=50)


class AddInput(BaseModel):
    paths: list[str] = Field(min_length=1, max_length=50)


class CommitInput(BaseModel):
    message: str = Field(min_length=1, max_length=200)


class _GitTool(BaseTool):
    def __init__(self, repo: Path, confirm: Callable[[str], bool] | None = None) -> None:
        self.repo = repo.resolve()
        self.confirm = confirm or (lambda _message: False)

    def run(self, args: list[str]) -> ToolResult:
        try:
            completed = subprocess.run(
                ["git", *args], cwd=self.repo, shell=False, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitToolError(f"Git could not run: {exc}") from exc
        output = (completed.stdout + completed.stderr)[:20_000]
        return ToolResult(
            ok=completed.returncode == 0,
            summary=f"git {args[0]} exited with code {completed.returncode}",
            data={"output": output, "exit_code": completed.returncode},
            error=None if completed.returncode == 0 else output,
        )


class GitStatusTool(_GitTool):
    name = "git.status"
    description = "Show concise repository status."
    input_model = EmptyInput

    def execute(self, arguments: EmptyInput) -> ToolResult:
        return self.run(["status", "--short", "--branch"])


class GitDiffTool(_GitTool):
    name = "git.diff"
    description = "Show working-tree or staged changes."
    input_model = DiffInput

    def execute(self, arguments: DiffInput) -> ToolResult:
        return self.run(["diff", *(["--staged"] if arguments.staged else [])])


class GitLogTool(_GitTool):
    name = "git.log"
    description = "Show recent commit history."
    input_model = LogInput

    def execute(self, arguments: LogInput) -> ToolResult:
        return self.run(["log", "--oneline", f"-{arguments.limit}"])


class GitBranchTool(_GitTool):
    name = "git.branch"
    description = "Show local branches without modifying them."
    input_model = EmptyInput

    def execute(self, arguments: EmptyInput) -> ToolResult:
        return self.run(["branch", "--list"])


class GitAddTool(_GitTool):
    name = "git.add"
    description = "Stage explicit repository-relative paths after confirmation."
    input_model = AddInput
    safety_level = SafetyLevel.CONFIRM

    def execute(self, arguments: AddInput) -> ToolResult:
        if any(path.startswith(("/", "\\")) or ".." in Path(path).parts for path in arguments.paths):
            raise GitToolError("Git paths must stay within the repository")
        if not self.confirm(f"Stage with git add: {', '.join(arguments.paths)}?"):
            return ToolResult(ok=False, summary="Git add was not approved")
        return self.run(["add", "--", *arguments.paths])


class GitCommitTool(_GitTool):
    name = "git.commit"
    description = "Create a local commit after confirmation. Never pushes."
    input_model = CommitInput
    safety_level = SafetyLevel.CONFIRM

    def execute(self, arguments: CommitInput) -> ToolResult:
        if not self.confirm(
            f'Shamaran wants to create a local commit:\n\n{arguments.message}\n\nContinue?'
        ):
            return ToolResult(ok=False, summary="Git commit was not approved")
        return self.run(["commit", "-m", arguments.message])


def git_tools(repo: Path, confirm: Callable[[str], bool] | None = None) -> list[BaseTool]:
    return [
        GitStatusTool(repo, confirm), GitDiffTool(repo, confirm),
        GitLogTool(repo, confirm), GitBranchTool(repo, confirm),
        GitAddTool(repo, confirm), GitCommitTool(repo, confirm),
    ]
