"""Tool execution adapter that turns failures into observable results."""

import logging

from shamaran.exceptions import ShamaranError, ToolValidationError
from shamaran.tools.base import ToolResult
from shamaran.tools.registry import ToolRegistry


logger = logging.getLogger("shamaran.tools")


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, name: str, arguments: dict[str, object]) -> ToolResult:
        logger.info("tool invocation name=%s", name)
        try:
            result = self.registry.invoke(name, arguments)
        except (ShamaranError, ValueError) as exc:
            logger.warning("tool failure name=%s error=%s", name, exc)
            return ToolResult(ok=False, summary="Tool call failed", error=str(exc))
        logger.info("tool completed name=%s ok=%s", name, result.ok)
        return result
