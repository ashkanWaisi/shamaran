"""Central, environment-driven configuration."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_CONFIG_DIR = Path(
    os.environ.get("SHAMARAN_HOME", Path.home() / ".shamaran")
).expanduser()
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(DEFAULT_CONFIG_FILE, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field("ollama", validation_alias="SHAMARAN_PROVIDER")
    workspace: Path = Field(Path("workspace"), validation_alias="SHAMARAN_WORKSPACE")
    max_steps: int = Field(8, ge=1, le=32, validation_alias="SHAMARAN_MAX_STEPS")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO", validation_alias="SHAMARAN_LOG_LEVEL"
    )
    confirm_mutations: bool = Field(True, validation_alias="SHAMARAN_CONFIRM_MUTATIONS")
    ollama_base_url: str = Field(
        "http://localhost:11434", validation_alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field("", validation_alias="OLLAMA_MODEL")
    ollama_timeout: float = Field(60.0, gt=0, le=600, validation_alias="OLLAMA_TIMEOUT")
    compatible_base_url: str = Field(
        "http://localhost:1234/v1", validation_alias="SHAMARAN_COMPATIBLE_BASE_URL"
    )
    compatible_model: str = Field("", validation_alias="SHAMARAN_COMPATIBLE_MODEL")
    compatible_api_key: str = Field("", validation_alias="SHAMARAN_COMPATIBLE_API_KEY")
    compatible_timeout: float = Field(
        60.0, gt=0, le=600, validation_alias="SHAMARAN_COMPATIBLE_TIMEOUT"
    )
    memory_db: Path = Field(
        Path("data/shamaran_memory.db"), validation_alias="SHAMARAN_MEMORY_DB"
    )

    @field_validator("provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("provider cannot be empty")
        return value

    @field_validator("ollama_base_url", "compatible_base_url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("Model endpoint must be an HTTP(S) URL")
        return value.rstrip("/")

    def ensure_directories(self) -> None:
        self.workspace.expanduser().resolve().mkdir(parents=True, exist_ok=True)
        self.memory_db.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        Path("logs").resolve().mkdir(parents=True, exist_ok=True)
