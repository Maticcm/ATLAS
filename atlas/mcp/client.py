"""Generic MCP client — synchronous wrapper around the async mcp SDK."""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import threading
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Manages a long-lived connection to an MCP server over stdio.

    The ``mcp`` SDK is async-only.  This class contains the async
    boundary so the rest of ATLAS stays synchronous. It runs a dedicated
    background thread for the asyncio event loop.

    Typical lifecycle::

        client = MCPClient(...)
        client.connect()       # spawns the server subprocess
        result = client.call_tool("tool_name", {"arg": "val"})
        client.disconnect()    # kills the subprocess

    Args:
        command:     Executable to spawn (e.g. ``"npx"``).
        args:        Arguments for the command.
        server_name: Human-readable label for logging.
        logger:      Logger instance.
    """

    def __init__(
        self,
        command: str,
        args: list[str],
        server_name: str,
        logger: logging.Logger,
    ) -> None:
        self._server_params = StdioServerParameters(
            command=command,
            args=args,
        )
        self._server_name = server_name
        self._logger = logger

        # Threading & Async internals
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._session: ClientSession | None = None
        self._stop_event: asyncio.Event | None = None

    def connect(self) -> None:
        """Spawn the MCP server and establish a session."""
        self._logger.info("MCP connecting: %s", self._server_name)
        
        ready_future: concurrent.futures.Future[None] = concurrent.futures.Future()
        
        self._thread = threading.Thread(
            target=self._run_loop_in_thread,
            args=(ready_future,),
            daemon=True,
            name=f"mcp-{self._server_name}",
        )
        self._thread.start()
        
        # Wait for the background thread to establish the connection
        try:
            ready_future.result(timeout=30.0)
        except Exception as exc:
            self._logger.error("Failed to connect to MCP: %s", exc)
            raise RuntimeError(f"MCP connection failed: {exc}") from exc
            
        self._logger.info("MCP connected: %s", self._server_name)

    def disconnect(self) -> None:
        """Tear down the session and kill the server process."""
        if self._loop is not None and self._stop_event is not None:
            self._logger.info("MCP disconnecting: %s", self._server_name)
            self._loop.call_soon_threadsafe(self._stop_event.set)
            if self._thread is not None:
                self._thread.join(timeout=10.0)
            self._loop = None
            self._thread = None
            self._session = None
            self._stop_event = None
            self._logger.info("MCP disconnected: %s", self._server_name)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on the MCP server (synchronous).

        Args:
            name:      Tool name as registered by the server.
            arguments: Tool arguments.

        Returns:
            The server's text response.

        Raises:
            RuntimeError: If not connected.
        """
        if self._loop is None or self._session is None:
            raise RuntimeError(f"MCP client not connected: {self._server_name}")

        self._logger.info("MCP call: %s.%s(%r)", self._server_name, name, arguments)
        
        # Schedule the call on the background event loop and wait for it
        future = asyncio.run_coroutine_threadsafe(
            self._session.call_tool(name, arguments=arguments),
            self._loop
        )
        
        try:
            result = future.result(timeout=60.0)
        except Exception as exc:
            self._logger.error("MCP call failed: %s.%s → %s", self._server_name, name, exc)
            return f"### Error\n{exc}"

        # Extract text from the result content list
        output_parts: list[str] = []
        for block in result.content:
            if hasattr(block, "text"):
                output_parts.append(block.text)
        output = "\n".join(output_parts) if output_parts else str(result)

        self._logger.info("MCP result: %s.%s → %s", self._server_name, name, output[:200])
        return output

    # ------------------------------------------------------------------
    # Async internals (run entirely in the background thread)
    # ------------------------------------------------------------------

    def _run_loop_in_thread(self, ready_future: concurrent.futures.Future[None]) -> None:
        """Entry point for the background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._server_loop(ready_future))
        except Exception as exc:
            if not ready_future.done():
                ready_future.set_exception(exc)
            self._logger.error("MCP thread error: %s", exc)
        finally:
            self._loop.close()

    async def _server_loop(self, ready_future: concurrent.futures.Future[None]) -> None:
        """The main async routine that maintains the context managers."""
        self._stop_event = asyncio.Event()
        
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self._session = session
                    await session.initialize()
                    
                    # Signal that connection is established
                    ready_future.set_result(None)
                    
                    # Wait here until disconnect() is called
                    await self._stop_event.wait()
        except Exception as exc:
            if not ready_future.done():
                ready_future.set_exception(exc)
            raise
