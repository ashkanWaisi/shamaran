from pathlib import Path

import pytest
from pydantic import ValidationError

from shamaran.config import Settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.provider == "ollama"
    assert settings.max_steps == 8
    assert settings.workspace == Path("workspace")


def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHAMARAN_MAX_STEPS", "5")
    monkeypatch.setenv("OLLAMA_MODEL", "local-model")
    settings = Settings(_env_file=None)
    assert settings.max_steps == 5
    assert settings.ollama_model == "local-model"


def test_dotenv_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SHAMARAN_PROVIDER=OLLAMA\nSHAMARAN_MAX_STEPS=6\nOLLAMA_MODEL=from-file\n",
        encoding="utf-8",
    )
    settings = Settings(_env_file=env_file)
    assert settings.provider == "ollama"
    assert settings.max_steps == 6
    assert settings.ollama_model == "from-file"


def test_invalid_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHAMARAN_MAX_STEPS", "0")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
