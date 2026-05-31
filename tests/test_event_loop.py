"""Tests for atlas.core.event_loop."""

from __future__ import annotations

import logging
from unittest.mock import patch

from atlas.core.event_loop import EventLoop
from atlas.core.events import WakeEvent


def _make_loop() -> EventLoop:
    """Create an EventLoop with a null logger."""
    logger = logging.getLogger("test_event_loop")
    logger.addHandler(logging.NullHandler())
    return EventLoop(logger=logger)


class TestEventLoop:
    """EventLoop should convert stdin commands to typed events."""

    def test_wake_yields_wake_event(self) -> None:
        loop = _make_loop()
        with patch("builtins.input", side_effect=["wake", "quit"]):
            events = list(loop.listen())
        assert len(events) == 1
        assert isinstance(events[0], WakeEvent)

    def test_quit_stops_loop(self) -> None:
        loop = _make_loop()
        with patch("builtins.input", side_effect=["quit"]):
            events = list(loop.listen())
        assert events == []

    def test_unknown_input_is_ignored(self) -> None:
        loop = _make_loop()
        with patch("builtins.input", side_effect=["hello", "wake", "quit"]):
            events = list(loop.listen())
        assert len(events) == 1
        assert isinstance(events[0], WakeEvent)

    def test_eof_stops_loop(self) -> None:
        loop = _make_loop()
        with patch("builtins.input", side_effect=EOFError):
            events = list(loop.listen())
        assert events == []

    def test_keyboard_interrupt_stops_loop(self) -> None:
        loop = _make_loop()
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            events = list(loop.listen())
        assert events == []
