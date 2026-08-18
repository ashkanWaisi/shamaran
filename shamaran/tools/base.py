"""Typed foundations shared by every tool."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SafetyLevel(str, Enum):
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCKED = "blocked"


class ToolResult(BaseModel):
    ok: bool
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str
    input_model: type[BaseModel]
    safety_level: SafetyLevel = SafetyLevel.SAFE

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "safety_level": self.safety_level.value,
            "input_schema": self.input_model.model_json_schema(),
        }

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        validated = self.input_model.model_validate(arguments)
        return self.execute(validated)

    @abstractmethod
    def execute(self, arguments: BaseModel) -> ToolResult:
        raise NotImplementedError
