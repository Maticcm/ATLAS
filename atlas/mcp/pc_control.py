"""PC Control MCP server integration."""

from __future__ import annotations

import sys
import logging

from atlas.mcp.client import MCPClient
from atlas.tools.registry import ToolRegistry
from atlas.tools.tool_call import PermissionLevel


class PcControlMCP:
    """Provides local Windows PC control tools using the custom pc-control MCP server.
    
    Runs as a local Python subprocess.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        # Spawn using the current python executable to ensure dependencies are found
        self._client = MCPClient(
            command=sys.executable,
            args=["-m", "pc_control"],
            server_name="pc_control",
            logger=logger,
        )

    def connect(self) -> None:
        """Start the PC Control MCP server process."""
        self._client.connect()

    def disconnect(self) -> None:
        """Stop the PC Control MCP server process."""
        self._client.disconnect()

    def register_tools(self, registry: ToolRegistry) -> None:
        """Register PC Control tools with ATLAS."""
        
        # ------------------------------------------------------------------
        # SAFE tools
        # ------------------------------------------------------------------
        
        registry.register(
            name="get_system_info",
            handler=lambda: self._client.call_tool("get_system_info", {}),
            permission=PermissionLevel.SAFE,
            description="Get basic system utilization information (CPU, RAM, Disk).",
            parameters={"type": "OBJECT", "properties": {}},
        )

        registry.register(
            name="list_windows",
            handler=lambda: self._client.call_tool("list_windows", {}),
            permission=PermissionLevel.SAFE,
            description="List all visible windows.",
            parameters={"type": "OBJECT", "properties": {}},
        )

        registry.register(
            name="screenshot",
            handler=lambda: self._client.call_tool("screenshot", {}),
            permission=PermissionLevel.SAFE,
            description="Take a screenshot and save it locally.",
            parameters={"type": "OBJECT", "properties": {}},
        )

        registry.register(
            name="list_running_processes",
            handler=lambda: self._client.call_tool("list_running_processes", {}),
            permission=PermissionLevel.SAFE,
            description="List all running processes (names and PIDs).",
            parameters={"type": "OBJECT", "properties": {}},
        )

        registry.register(
            name="get_screen_resolution",
            handler=lambda: self._client.call_tool("get_screen_resolution", {}),
            permission=PermissionLevel.SAFE,
            description="Get the dimensions of the primary monitor.",
            parameters={"type": "OBJECT", "properties": {}},
        )

        # ------------------------------------------------------------------
        # CONFIRM tools
        # ------------------------------------------------------------------

        registry.register(
            name="open_application",
            handler=lambda name: self._client.call_tool("open_application", {"name": name}),
            permission=PermissionLevel.CONFIRM,
            description="Open an application by name or path.",
            parameters={
                "type": "OBJECT",
                "properties": {"name": {"type": "STRING", "description": "The name or path of the application"}},
                "required": ["name"]
            },
        )

        registry.register(
            name="focus_window",
            handler=lambda title: self._client.call_tool("focus_window", {"title": title}),
            permission=PermissionLevel.CONFIRM,
            description="Bring a window to the foreground by its title.",
            parameters={
                "type": "OBJECT",
                "properties": {"title": {"type": "STRING", "description": "Substring of window title"}},
                "required": ["title"]
            },
        )
        
        registry.register(
            name="minimize_window",
            handler=lambda title: self._client.call_tool("minimize_window", {"title": title}),
            permission=PermissionLevel.CONFIRM,
            description="Minimize a window by its title.",
            parameters={
                "type": "OBJECT",
                "properties": {"title": {"type": "STRING", "description": "Substring of window title"}},
                "required": ["title"]
            },
        )
        
        registry.register(
            name="maximize_window",
            handler=lambda title: self._client.call_tool("maximize_window", {"title": title}),
            permission=PermissionLevel.CONFIRM,
            description="Maximize a window by its title.",
            parameters={
                "type": "OBJECT",
                "properties": {"title": {"type": "STRING", "description": "Substring of window title"}},
                "required": ["title"]
            },
        )

        registry.register(
            name="type_text",
            handler=lambda text: self._client.call_tool("type_text", {"text": text}),
            permission=PermissionLevel.CONFIRM,
            description="Type a string of text as if on a keyboard.",
            parameters={
                "type": "OBJECT",
                "properties": {"text": {"type": "STRING"}},
                "required": ["text"]
            },
        )

        registry.register(
            name="press_key",
            handler=lambda key: self._client.call_tool("press_key", {"key": key}),
            permission=PermissionLevel.CONFIRM,
            description="Press a single key (e.g. 'enter', 'esc').",
            parameters={
                "type": "OBJECT",
                "properties": {"key": {"type": "STRING"}},
                "required": ["key"]
            },
        )

        registry.register(
            name="hotkey",
            handler=lambda keys: self._client.call_tool("hotkey", {"keys": keys}),
            permission=PermissionLevel.CONFIRM,
            description="Press a combination of keys together (e.g. ['ctrl', 'c']).",
            parameters={
                "type": "OBJECT",
                "properties": {"keys": {"type": "ARRAY", "items": {"type": "STRING"}}},
                "required": ["keys"]
            },
        )

        # ------------------------------------------------------------------
        # DANGEROUS tools
        # ------------------------------------------------------------------

        registry.register(
            name="close_application",
            handler=lambda name: self._client.call_tool("close_application", {"name": name}),
            permission=PermissionLevel.DANGEROUS,
            description="Close an application by its process name.",
            parameters={
                "type": "OBJECT",
                "properties": {"name": {"type": "STRING", "description": "Exact executable name (e.g. notepad.exe)"}},
                "required": ["name"]
            },
        )

        registry.register(
            name="lock_pc",
            handler=lambda: self._client.call_tool("lock_pc", {}),
            permission=PermissionLevel.DANGEROUS,
            description="Lock the Windows workstation.",
            parameters={"type": "OBJECT", "properties": {}},
        )

        registry.register(
            name="move_mouse",
            handler=lambda x, y: self._client.call_tool("move_mouse", {"x": x, "y": y}),
            permission=PermissionLevel.DANGEROUS,
            description="Move the mouse cursor to absolute coordinates.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"}
                },
                "required": ["x", "y"]
            },
        )

        registry.register(
            name="click",
            handler=lambda button="left": self._client.call_tool("click", {"button": button}),
            permission=PermissionLevel.DANGEROUS,
            description="Click the mouse at the current position.",
            parameters={
                "type": "OBJECT",
                "properties": {"button": {"type": "STRING", "description": "left, middle, or right"}},
            },
        )

        registry.register(
            name="double_click",
            handler=lambda button="left": self._client.call_tool("double_click", {"button": button}),
            permission=PermissionLevel.DANGEROUS,
            description="Double-click the mouse at the current position.",
            parameters={
                "type": "OBJECT",
                "properties": {"button": {"type": "STRING", "description": "left, middle, or right"}},
            },
        )

        registry.register(
            name="right_click",
            handler=lambda: self._client.call_tool("right_click", {}),
            permission=PermissionLevel.DANGEROUS,
            description="Right-click the mouse at the current position.",
            parameters={"type": "OBJECT", "properties": {}},
        )
