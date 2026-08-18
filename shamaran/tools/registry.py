"""Central registry and validation boundary for tools."""

from typing import Any

from shamaran.exceptions import ToolValidationError

from .base import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolValidationError(f"Unknown tool: {name}") from exc

    def invoke(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        try:
            return self.get(name).invoke(arguments)
        except ToolValidationError:
            raise
        except Exception as exc:
            raise ToolValidationError(f"Invalid call to {name}: {exc}") from exc

    def descriptions(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    def names(self) -> list[str]:
        return list(self._tools)

    def __len__(self) -> int:
        return len(self._tools)
