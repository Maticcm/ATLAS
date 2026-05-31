"""Tool registry for the PC Control MCP server."""

from __future__ import annotations

import functools
import inspect
import logging
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class ToolHandler:
    """Wrapper around a tool function to handle execution and logging."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        schema: type[BaseModel] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.func = func
        self.schema = schema

    def execute(self, arguments: dict[str, Any], logger: logging.Logger) -> str:
        logger.info("Tool request: %s(%r)", self.name, arguments)
        start_time = time.time()
        try:
            if self.schema:
                # Validate arguments against Pydantic schema
                kwargs = self.schema(**arguments).model_dump()
            else:
                kwargs = arguments

            result = self.func(**kwargs)
            
            # Format result
            import json
            if result is None:
                output = json.dumps({"success": True})
            else:
                output = json.dumps({"success": True, "data": result})

        except Exception as exc:
            logger.error("Tool execution failed: %s", exc)
            import json
            output = json.dumps({"success": False, "error": str(exc)})

        duration = time.time() - start_time
        logger.info("Tool %s finished in %.3fs. Result: %s", self.name, duration, output[:200])
        return output


class Registry:
    """Singleton registry for all server tools."""
    
    def __init__(self) -> None:
        self.tools: dict[str, ToolHandler] = {}

    def register(self, name: str, description: str, schema: type[BaseModel] | None = None) -> Callable:
        """Decorator to register a function as a tool."""
        def decorator(func: Callable) -> Callable:
            if name in self.tools:
                raise ValueError(f"Tool {name} already registered")
            self.tools[name] = ToolHandler(name, description, func, schema)
            return func
        return decorator

# Global registry instance
registry = Registry()

def tool(name: str, description: str, schema: type[BaseModel] | None = None) -> Callable:
    """Exported decorator to register tools."""
    return registry.register(name, description, schema)
