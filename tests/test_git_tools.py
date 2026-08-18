import subprocess
from pathlib import Path

from shamaran.tools.git_tools import (
    GitAddTool,
    GitBranchTool,
    GitCommitTool,
    GitDiffTool,
    GitLogTool,
    GitStatusTool,
)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_git_status_and_confirmed_mutations(tmp_path: Path) -> None:
    git(tmp_path, "init")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    assert GitStatusTool(tmp_path).invoke({}).ok
    assert GitAddTool(tmp_path, lambda _message: True).invoke({"paths": ["note.txt"]}).ok
    assert GitCommitTool(tmp_path, lambda _message: True).invoke({"message": "Add note"}).ok
    assert GitDiffTool(tmp_path).invoke({}).ok
    assert GitLogTool(tmp_path).invoke({"limit": 1}).ok
    assert GitBranchTool(tmp_path).invoke({}).ok


def test_git_mutation_rejected_without_confirmation(tmp_path: Path) -> None:
    git(tmp_path, "init")
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    result = GitAddTool(tmp_path).invoke({"paths": ["note.txt"]})
    assert not result.ok
