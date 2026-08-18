from unittest.mock import Mock

from shamaran.tools.desktop import DesktopOpenTool


def test_windows_my_computer_command() -> None:
    assert DesktopOpenTool.command("computer", "Windows") == [
        "explorer.exe",
        "shell:MyComputerFolder",
    ]


def test_desktop_action_requires_confirmation(monkeypatch) -> None:
    launch = Mock()
    monkeypatch.setattr("shamaran.tools.desktop.subprocess.Popen", launch)
    result = DesktopOpenTool(confirm=lambda _message: False).invoke({"target": "computer"})
    assert not result.ok
    launch.assert_not_called()


def test_approved_desktop_action_launches_without_shell(monkeypatch) -> None:
    launch = Mock()
    monkeypatch.setattr("shamaran.tools.desktop.platform.system", lambda: "Windows")
    monkeypatch.setattr("shamaran.tools.desktop.subprocess.Popen", launch)
    result = DesktopOpenTool(confirm=lambda _message: True).invoke({"target": "computer"})
    assert result.ok
    assert result.summary == "Opened computer"
    assert launch.call_args.args[0] == ["explorer.exe", "shell:MyComputerFolder"]
    assert launch.call_args.kwargs["shell"] is False
