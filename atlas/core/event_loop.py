"""Synchronous event loop — reads stdin and yields typed events."""

from __future__ import annotations

import logging
from collections.abc import Generator

from atlas.core.events import Event, WakeEvent


class EventLoop:
    """Simple stdin-based event loop.

    Reads lines from the terminal and converts recognised commands
    into typed :class:`Event` objects.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def listen(self) -> Generator[Event, None, None]:
        """Block on stdin and yield events until the user quits.

        Recognised commands:
            ``wake``  → :class:`WakeEvent`
            ``quit``  → stops the loop

        Any other input is logged and ignored.
        """
        while True:
            try:
                raw = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                self._logger.info("Input stream closed — shutting down.")
                return

            if raw == "quit":
                self._logger.info("Quit command received.")
                return

            if raw == "wake":
                yield WakeEvent()
                continue

            if raw:
                self._logger.debug("Unknown command: %r", raw)
