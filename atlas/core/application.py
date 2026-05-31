"""ATLAS application orchestrator."""

from __future__ import annotations

import sys

from atlas.config.settings import Settings
from atlas.core.event_loop import EventLoop
from atlas.core.events import WakeEvent
from atlas.core.logger import create_logger


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
            for event in loop.listen():
                self._handle(event)
        except KeyboardInterrupt:
            pass

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
        print("\nATLAS ONLINE\n")
