from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ModelResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any | None = None


def dedupe_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    """Drop exact duplicate calls before execution, preserving model order.

    Providers occasionally emit the same structured call twice. Executing an
    identical action twice is both noisy for research and unsafe for write tools.
    Calls with different arguments remain distinct.
    """
    unique: list[ToolCall] = []
    seen: set[tuple[str, str]] = set()
    for call in calls:
        key = (call.name, json.dumps(call.args, ensure_ascii=False, sort_keys=True, default=str))
        if key in seen:
            continue
        seen.add(key)
        unique.append(call)
    return unique


class Provider(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        """Return normalized text/tool calls regardless of vendor API shape."""
