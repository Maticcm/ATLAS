"""Tests for atlas.core.events."""

from __future__ import annotations

from datetime import datetime, timezone

from atlas.core.events import Event, WakeEvent


class TestEvent:
    """Base Event should carry a UTC timestamp."""

    def test_has_timestamp(self) -> None:
        event = Event()
        assert isinstance(event.timestamp, datetime)
        assert event.timestamp.tzinfo == timezone.utc

    def test_is_frozen(self) -> None:
        event = Event()
        try:
            event.timestamp = datetime.now(timezone.utc)  # type: ignore[misc]
            raise AssertionError("Expected FrozenInstanceError")
        except AttributeError:
            pass  # correct — frozen


class TestWakeEvent:
    """WakeEvent is a subclass of Event with no extra fields."""

    def test_is_event(self) -> None:
        wake = WakeEvent()
        assert isinstance(wake, Event)

    def test_has_timestamp(self) -> None:
        wake = WakeEvent()
        assert isinstance(wake.timestamp, datetime)
