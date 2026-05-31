"""PC Control MCP Server Core."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest

from pc_control.registry import registry


def create_logger() -> logging.Logger:
    """Setup server-side logging to a file."""
    logger = logging.getLogger("pc-control")
    logger.setLevel(logging.DEBUG)
    
    # We log to a file because stdio is used for the MCP protocol
    fh = logging.FileHandler("pc-control.log", mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = create_logger()

# Create the MCP server
app = Server("pc-control")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Provide the list of tools available from this server."""
    return [
        Tool(
            name=handler.name,
            description=handler.description,
            inputSchema=handler.schema.model_json_schema() if handler.schema else {
                "type": "object",
                "properties": {},
            }
        )
        for handler in registry.tools.values()
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Execute a tool request."""
    handler = registry.tools.get(name)
    if not handler:
        logger.error("Unknown tool requested: %s", name)
        import json
        return [TextContent(type="text", text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}))]
        
    output = handler.execute(arguments or {}, logger)
    return [TextContent(type="text", text=output)]

def start_server() -> None:
    """Start the stdio server loop."""
    # Ensure all modules are loaded before starting so tools are registered
    import pc_control.modules.applications
    import pc_control.modules.windows
    import pc_control.modules.keyboard
    import pc_control.modules.mouse
    import pc_control.modules.screen
    import pc_control.modules.system
    
    logger.info("Starting PC Control MCP Server over stdio")
    from mcp.server.stdio import stdio_server
    import asyncio
    
    async def run():
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())
            
    asyncio.run(run())
