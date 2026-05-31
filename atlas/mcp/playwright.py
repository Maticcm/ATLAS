"""Playwright MCP server integration."""

from __future__ import annotations

import logging

from atlas.mcp.client import MCPClient
from atlas.tools.registry import ToolRegistry
from atlas.tools.tool_call import PermissionLevel


class PlaywrightMCP:
    """Provides web browser tools using the official Playwright MCP server.

    Server package: ``@playwright/mcp``
    Runs as a local Node.js subprocess via ``npx``.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._client = MCPClient(
            command="npx",
            args=[
                "-y", 
                "@playwright/mcp@latest", 
                "--executable-path", 
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            ],
            server_name="playwright",
            logger=logger,
        )

    def connect(self) -> None:
        """Start the Playwright MCP server process."""
        self._client.connect()

    def disconnect(self) -> None:
        """Stop the Playwright MCP server process."""
        self._client.disconnect()

    def register_tools(self, registry: ToolRegistry) -> None:
        """Register Playwright tools with ATLAS."""
        registry.register(
            name="open_url",
            handler=self.open_url,
            permission=PermissionLevel.SAFE,
            description="Open a URL in the browser. Always use absolute URLs (e.g. https://google.com).",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "url": {
                        "type": "STRING",
                        "description": "The absolute URL to navigate to.",
                    }
                },
                "required": ["url"],
            },
        )

        registry.register(
            name="get_page_title",
            handler=self.get_page_title,
            permission=PermissionLevel.SAFE,
            description="Get the title of the current webpage. Useful to check if navigation succeeded.",
            parameters={
                "type": "OBJECT",
                "properties": {},
            },
        )

        registry.register(
            name="get_current_url",
            handler=self.get_current_url,
            permission=PermissionLevel.SAFE,
            description="Get the URL of the current webpage.",
            parameters={
                "type": "OBJECT",
                "properties": {},
            },
        )

    # ------------------------------------------------------------------
    # Tool Handlers (Sync)
    # ------------------------------------------------------------------

    def open_url(self, url: str) -> str:
        # According to standard Playwright MCP naming conventions
        return self._client.call_tool("browser_navigate", {"url": url})

    def get_page_title(self) -> str:
        # A simple JS evaluation to get the title
        return self._client.call_tool("browser_evaluate", {"script": "document.title"})

    def get_current_url(self) -> str:
        return self._client.call_tool("browser_evaluate", {"script": "window.location.href"})
