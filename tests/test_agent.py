from typing import Any

import pytest
from pydantic import BaseModel

from shamaran.agent import ShamaranAgent
from shamaran.exceptions import ProviderError
from shamaran.providers.base import BaseProvider, ChatMessage, ProviderResponse
from shamaran.tools.base import BaseTool, ToolResult
from shamaran.tools.registry import ToolRegistry


class NoInput(BaseModel):
    pass


class CountingTool(BaseTool):
    name = "test.count"
    description = "Count an invocation."
    input_model = NoInput

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, arguments: NoInput) -> ToolResult:
        self.calls += 1
        return ToolResult(ok=True, summary="counted", data={"count": self.calls})


class SequenceProvider(BaseProvider):
    name = "test"

    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)

    def complete(self, messages: list[ChatMessage], tools: list[dict[str, Any]]) -> ProviderResponse:
        return ProviderResponse(content=next(self.responses))

    def health(self) -> tuple[bool, str]:
        return True, "ready"


def registry_with_tool() -> tuple[ToolRegistry, CountingTool]:
    registry = ToolRegistry()
    tool = CountingTool()
    registry.register(tool)
    return registry, tool


def test_mocked_multi_step_task() -> None:
    registry, tool = registry_with_tool()
    provider = SequenceProvider([
        '{"plan":["Count","Answer"],"action":{"tool":"test.count","arguments":{}}}',
        '{"final":"Count is 1."}',
    ])
    result = ShamaranAgent(provider, registry, max_steps=4).run("count")
    assert result.answer == "Count is 1."
    assert result.steps_used == 2
    assert tool.calls == 1


def test_max_steps() -> None:
    registry, _ = registry_with_tool()
    provider = SequenceProvider([
        '{"action":{"tool":"test.count","arguments":{}}}',
        '{"action":{"tool":"test.count","arguments":{}}}',
    ])
    result = ShamaranAgent(provider, registry, max_steps=2).run("keep going")
    assert result.exhausted
    assert "step limit" in result.answer


def test_invalid_tool_becomes_observation() -> None:
    registry, _ = registry_with_tool()
    provider = SequenceProvider([
        '{"action":{"tool":"missing.tool","arguments":{}}}',
        '{"final":"The tool was unavailable."}',
    ])
    result = ShamaranAgent(provider, registry).run("use missing")
    assert result.answer == "The tool was unavailable."


def test_invalid_response_is_repaired_once() -> None:
    registry, tool = registry_with_tool()
    provider = SequenceProvider([
        '{"action":{"tool":"test.count","arguments":{}}}',
        "Count is 1.",
        '{"final":"Count is 1."}',
    ])
    result = ShamaranAgent(provider, registry).run("count")
    assert result.answer == "Count is 1."
    assert result.steps_used == 2
    assert tool.calls == 1


def test_invalid_response_fails_after_one_repair() -> None:
    registry, _ = registry_with_tool()
    provider = SequenceProvider(["not json", "still not json"])
    with pytest.raises(ProviderError, match="invalid agent response"):
        ShamaranAgent(provider, registry).run("count")


def test_registry_schema() -> None:
    registry, _ = registry_with_tool()
    assert registry.names() == ["test.count"]
    assert registry.descriptions()[0]["input_schema"]["type"] == "object"
