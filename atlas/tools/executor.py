"""Tool executor — checks permissions and dispatches tool calls."""

from __future__ import annotations

import logging

from atlas.tools.registry import ToolRegistry
from atlas.tools.tool_call import PermissionLevel, ToolCall, ToolResult


class ToolExecutor:
    """Executes tool calls after verifying permissions.

    The executor never skips the permission check, even for SAFE tools.
    This ensures the permission system is always in the code path.

    Args:
        registry: The tool registry to look up handlers.
        logger:   Logger for auditing tool execution.
    """

    def __init__(self, registry: ToolRegistry, logger: logging.Logger) -> None:
        self._registry = registry
        self._logger = logger

    def execute(self, call: ToolCall) -> ToolResult:
        """Execute a tool call and return the result.

        This method never raises — errors are captured in the returned
        :class:`ToolResult` so the caller can always send a result back
        to the LLM.
        """
        self._logger.info("Tool requested: %s(%r)", call.name, call.arguments)

        definition = self._registry.get(call.name)
        if definition is None:
            self._logger.warning("Unknown tool: %s", call.name)
            return ToolResult(
                tool_name=call.name,
                success=False,
                output=f"Unknown tool: {call.name}",
            )

        # Permission gate
        if not self._check_permission(call, definition.permission):
            self._logger.warning(
                "Permission denied for tool %s (level=%s)",
                call.name,
                definition.permission.name,
            )
            return ToolResult(
                tool_name=call.name,
                success=False,
                output=f"Permission denied: {call.name} requires {definition.permission.value}",
            )

        # Execute
        try:
            self._logger.info("Executing tool: %s", call.name)
            output = definition.handler(**call.arguments)
            self._logger.info("Tool result: %s → %s", call.name, output)
            return ToolResult(tool_name=call.name, success=True, output=output)
        except Exception as exc:
            self._logger.error("Tool error: %s → %s", call.name, exc)
            return ToolResult(
                tool_name=call.name,
                success=False,
                output=f"Error: {exc}",
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_permission(self, call: ToolCall, level: PermissionLevel) -> bool:
        """Return whether execution is allowed for the given level.

        SAFE: Auto-approved.
        CONFIRM/DANGEROUS: Asks the user "y/n" in the CLI with exact formatting.
        """
        if level == PermissionLevel.SAFE:
            return True
            
        # Format arguments nicely (e.g. key="value", key2=123)
        args_str = ", ".join(f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}" for k, v in call.arguments.items())
        
        print("\nATLAS wants to execute:\n")
        print(f"{call.name}({args_str})\n")
        print(f"Permission Level: {level.name}\n")
        
        prompt = "Approve? (y/n): "
            
        try:
            choice = input(prompt).strip().lower()
            if choice in ('y', 'yes'):
                return True
        except (EOFError, KeyboardInterrupt):
            pass
            
        print("\nExecution blocked by user.")
        return False
