"""Typed event definitions for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Event:
    """Base event — all events carry a UTC timestamp."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class WakeEvent(Event):
    """Emitted when ATLAS receives a wake signal."""
