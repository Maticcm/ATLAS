"""ATLAS application orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

from atlas.brain.llm import Brain
from atlas.config.settings import Settings
from atlas.core.event_loop import EventLoop
from atlas.core.events import WakeEvent
from atlas.core.logger import create_logger
from atlas.voice.speech import SpeechEngine

from atlas.tools.registry import ToolRegistry
from atlas.tools.executor import ToolExecutor
from atlas.mcp.playwright import PlaywrightMCP
from atlas.mcp.pc_control import PcControlMCP
from atlas.tools.tool_call import ToolCall, ToolResult

_SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "brain" / "system_prompt.txt"


class Application:
    """Top-level application — wires dependencies and runs the main loop.

    Args:
        settings: Loaded application configuration.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = create_logger(
            name=settings.app_name,
            level=settings.log_level,
        )
        system_prompt = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self._brain = Brain(system_prompt=system_prompt)
        self._speech = SpeechEngine(logger=self._logger)

        # Initialize tool and MCP layers
        self._tool_registry = ToolRegistry()
        
        self._playwright_mcp = PlaywrightMCP(logger=self._logger)
        self._playwright_mcp.register_tools(self._tool_registry)
        
        self._pc_control_mcp = PcControlMCP(logger=self._logger)
        self._pc_control_mcp.register_tools(self._tool_registry)
        
        self._tool_executor = ToolExecutor(
            registry=self._tool_registry,
            logger=self._logger,
        )

    def run(self) -> None:
        """Start ATLAS, listen for events, and handle them."""
        print(f"{self._settings.app_name} starting...\n")
        self._logger.info(
            "v%s | debug=%s",
            self._settings.version,
            self._settings.debug,
        )

        loop = EventLoop(logger=self._logger)

        try:
            self._playwright_mcp.connect()
            self._pc_control_mcp.connect()
            for event in loop.listen():
                self._handle(event)
        except KeyboardInterrupt:
            pass
        finally:
            self._playwright_mcp.disconnect()
            self._pc_control_mcp.disconnect()

        print(f"\n{self._settings.app_name} shutting down.")
        sys.exit(0)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle(self, event: object) -> None:
        """Dispatch a single event to the appropriate handler."""
        match event:
            case WakeEvent():
                self._on_wake(event)
            case _:
                self._logger.warning("Unhandled event: %r", event)

    def _on_wake(self, event: WakeEvent) -> None:
        self._logger.debug("Wake event at %s", event.timestamp)
        self._respond("ATLAS ONLINE")
        self._conversation_loop()

    def _conversation_loop(self) -> None:
        """Inner REPL — owns history, passes it to Brain on every turn."""
        history: list[dict[str, str]] = []

        while True:
            try:
                message = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return

            if not message:
                continue

            if message.lower() == "exit":
                print()
                return

            # Multi-turn tool execution loop
            tool_results: list[ToolResult] = []
            
            while True:
                try:
                    reply = self._brain.chat_with_tools(
                        history=history,
                        message=message,
                        tools=self._tool_registry.definitions(),
                        tool_results=tool_results,
                    )
                except Exception as exc:
                    self._logger.error("Brain error: %s", exc)
                    print("ATLAS: I encountered an error, sir.")
                    break

                if isinstance(reply, ToolCall):
                    # Execute the requested tool and loop back to the LLM
                    result = self._tool_executor.execute(reply)
                    tool_results.append(result)
                else:
                    # Final text reply received
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": reply})
                    self._respond(reply)
                    break

    def _respond(self, text: str) -> None:
        """Print a response and speak it aloud."""
        print(f"\nATLAS: {text}\n")
        try:
            self._speech.speak(text)
        except Exception as exc:
            self._logger.error("Speech error: %s", exc)
