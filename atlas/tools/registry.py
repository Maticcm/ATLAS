"""Tool registry — maps tool names to definitions and handlers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from atlas.tools.tool_call import PermissionLevel


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Everything ATLAS needs to know about a single tool.

    Attributes:
        name:        Unique identifier (e.g. ``"open_url"``).
        description: One-line human/LLM-readable purpose.
        parameters:  JSON-Schema-style dict describing the arguments.
        handler:     Callable that executes the tool: ``(args) -> str``.
        permission:  Required permission level.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., str]
    permission: PermissionLevel


class ToolRegistry:
    """Central catalogue of available tools.

    Registration is explicit — no decorators, no auto-discovery.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., str],
        permission: PermissionLevel,
        description: str,
        parameters: dict[str, Any],
    ) -> None:
        """Add a tool to the registry.

        Raises:
            ValueError: If *name* is already registered.
        """
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name!r}")
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            permission=permission,
        )

    def get(self, name: str) -> ToolDefinition | None:
        """Look up a tool by name, or return *None*."""
        return self._tools.get(name)

    def definitions(self) -> list[ToolDefinition]:
        """Return all registered tool definitions (stable order)."""
        return list(self._tools.values())
