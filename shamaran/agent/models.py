from typing import Any

from pydantic import BaseModel, Field, model_validator


class Action(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentEnvelope(BaseModel):
    plan: list[str] | None = None
    action: Action | None = None
    final: str | None = None

    @model_validator(mode="after")
    def exactly_one_outcome(self) -> "AgentEnvelope":
        if (self.action is None) == (self.final is None):
            raise ValueError("response must contain exactly one of action or final")
        return self


class AgentResult(BaseModel):
    answer: str
    steps_used: int
    exhausted: bool = False
    completed: list[str] = Field(default_factory=list)
