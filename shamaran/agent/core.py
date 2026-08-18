"""Bounded observe-act loop with a transparent public plan."""

import json
from collections.abc import Callable

from shamaran.exceptions import ProviderError
from shamaran.providers.base import BaseProvider, ChatMessage
from shamaran.tools.registry import ToolRegistry

from .executor import ToolExecutor
from .models import AgentResult
from .planner import parse_envelope
from .prompts import SYSTEM_PROMPT


PlanCallback = Callable[[list[str]], None]
ToolCallback = Callable[[str, bool, str], None]

FORMAT_REPAIR_PROMPT = """Your previous response did not match the required protocol.
Return the same intended response again as exactly one JSON object. Use either
{"action":{"tool":"tool.name","arguments":{}}} or {"final":"answer"}.
Do not use Markdown fences, prose outside JSON, or both action and final."""


class ShamaranAgent:
    def __init__(
        self,
        provider: BaseProvider,
        tools: ToolRegistry,
        max_steps: int = 8,
        on_plan: PlanCallback | None = None,
        on_tool: ToolCallback | None = None,
    ) -> None:
        self.provider = provider
        self.tools = tools
        self.max_steps = max_steps
        self.executor = ToolExecutor(tools)
        self.on_plan = on_plan or (lambda _plan: None)
        self.on_tool = on_tool or (lambda _name, _ok, _summary: None)

    def run(self, request: str, memory_context: str = "") -> AgentResult:
        user_content = request
        if memory_context:
            user_content += f"\n\n{memory_context}"
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="system", content="Registered tools:\n" + json.dumps(self.tools.descriptions())),
            ChatMessage(role="user", content=user_content),
        ]
        completed: list[str] = []
        plan_shown = False
        for step in range(1, self.max_steps + 1):
            response = self.provider.complete(messages, self.tools.descriptions())
            try:
                envelope = parse_envelope(response.content)
            except ProviderError as first_error:
                messages.append(ChatMessage(role="assistant", content=response.content))
                messages.append(ChatMessage(role="system", content=FORMAT_REPAIR_PROMPT))
                repaired = self.provider.complete(messages, self.tools.descriptions())
                try:
                    envelope = parse_envelope(repaired.content)
                except ProviderError:
                    raise first_error
                response = repaired
            if envelope.plan and not plan_shown:
                self.on_plan(envelope.plan)
                plan_shown = True
            if envelope.final is not None:
                return AgentResult(answer=envelope.final, steps_used=step, completed=completed)

            action = envelope.action
            assert action is not None
            result = self.executor.execute(action.tool, action.arguments)
            completed.append(f"{action.tool}: {result.summary}")
            self.on_tool(action.tool, result.ok, result.summary)
            messages.append(ChatMessage(role="assistant", content=response.content))
            messages.append(
                ChatMessage(role="tool", content=json.dumps(result.model_dump(), default=str))
            )

        return AgentResult(
            answer=(
                "Shamaran reached the configured step limit.\n\nCompleted:\n"
                + ("\n".join(f"- {item}" for item in completed) or "- No tool actions completed")
                + "\n\nRemaining:\n- Continue in a new request if more work is needed."
            ),
            steps_used=self.max_steps,
            exhausted=True,
            completed=completed,
        )
