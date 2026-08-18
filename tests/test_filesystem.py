from pathlib import Path

import pytest

from shamaran.exceptions import WorkspaceSecurityError
from shamaran.tools.filesystem import (
    FilesystemSandbox,
    ListTool,
    MkdirTool,
    ReadTool,
    ReplaceTool,
    WriteTool,
)


@pytest.fixture()
def sandbox(tmp_path: Path) -> FilesystemSandbox:
    return FilesystemSandbox(tmp_path / "workspace", tmp_path / "project")


def test_write_read_replace_and_list(sandbox: FilesystemSandbox) -> None:
    approve = lambda _message: True
    assert MkdirTool(sandbox, approve).invoke({"path": "notes"}).ok
    assert WriteTool(sandbox, approve).invoke(
        {"path": "notes/a.txt", "content": "hello", "overwrite": False}
    ).ok
    read = ReadTool(sandbox).invoke({"path": "notes/a.txt"})
    assert read.data["content"] == "hello"
    assert ReplaceTool(sandbox, approve).invoke(
        {"path": "notes/a.txt", "old": "hello", "new": "Shamaran"}
    ).ok
    assert ListTool(sandbox).invoke({"path": "notes"}).data["entries"][0]["name"] == "a.txt"


@pytest.mark.parametrize("path", ["../escape.txt", "a/../../escape.txt"])
def test_traversal_blocked(sandbox: FilesystemSandbox, path: str) -> None:
    with pytest.raises(WorkspaceSecurityError):
        sandbox.resolve(path, write=True)


def test_absolute_escape_blocked(sandbox: FilesystemSandbox, tmp_path: Path) -> None:
    with pytest.raises(WorkspaceSecurityError):
        sandbox.resolve(str(tmp_path / "outside.txt"), write=True)


def test_project_scope_is_read_only(sandbox: FilesystemSandbox) -> None:
    with pytest.raises(WorkspaceSecurityError):
        sandbox.resolve("@project/source.py", write=True)


def test_mutation_fails_closed_without_confirmation(sandbox: FilesystemSandbox) -> None:
    result = WriteTool(sandbox).invoke({"path": "denied.txt", "content": "no"})
    assert not result.ok
    assert not (sandbox.workspace / "denied.txt").exists()


def test_symlink_escape_blocked(sandbox: FilesystemSandbox, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    link = sandbox.workspace / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation is unavailable")
    with pytest.raises(WorkspaceSecurityError):
        sandbox.resolve("link/secret.txt", write=True)
