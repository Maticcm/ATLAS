"""Application settings loaded from YAML configuration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import yaml


_DEFAULTS: dict[str, object] = {
    "app_name": "ATLAS",
    "version": "0.1.0",
    "debug": False,
    "log_level": "INFO",
}


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application configuration."""

    app_name: str
    version: str
    debug: bool
    log_level: str

    @classmethod
    def load(cls, path: Path | None = None) -> Self:
        """Load settings from a YAML file, falling back to defaults.

        Args:
            path: Path to the YAML config file.  When *None* or the
                  file does not exist, built-in defaults are used.
        """
        raw: dict[str, object] = dict(_DEFAULTS)

        if path is not None and path.is_file():
            with path.open("r", encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh)
            if isinstance(loaded, dict):
                raw.update(loaded)

        # Validate log_level early so a typo doesn't surface later.
        level_name = str(raw["log_level"]).upper()
        if not hasattr(logging, level_name):
            raise ValueError(f"Invalid log_level: {raw['log_level']!r}")

        return cls(
            app_name=str(raw["app_name"]),
            version=str(raw["version"]),
            debug=bool(raw["debug"]),
            log_level=level_name,
        )
