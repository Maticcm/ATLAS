"""Typed data structures for tool calling."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PermissionLevel(Enum):
    """How much trust a tool requires before execution.

    SAFE:      Execute immediately without confirmation.
    CONFIRM:   Ask the user before executing (future).
    DANGEROUS: Refuse unless explicitly overridden (future).
    """

    SAFE = "safe"
    CONFIRM = "confirm"
    DANGEROUS = "dangerous"


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A request from the LLM to execute a specific tool.

    Attributes:
        name:      Registered tool name (e.g. ``"open_url"``).
        arguments: Keyword arguments the LLM wants to pass.
    """

    name: str
    arguments: dict[str, object]


@dataclass(frozen=True, slots=True)
class ToolResult:
    """The outcome of executing a tool.

    Attributes:
        tool_name: Which tool was executed.
        success:   Whether the execution succeeded.
        output:    Human-readable result or error message.
    """

    tool_name: str
    success: bool
    output: str
