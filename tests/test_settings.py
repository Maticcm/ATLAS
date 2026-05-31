"""Tests for atlas.config.settings."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from atlas.config.settings import Settings


class TestSettingsDefaults:
    """Settings.load() with no file should return sane defaults."""

    def test_defaults_when_no_path(self) -> None:
        settings = Settings.load(path=None)
        assert settings.app_name == "ATLAS"
        assert settings.version == "0.1.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_defaults_when_path_missing(self, tmp_path: Path) -> None:
        settings = Settings.load(path=tmp_path / "nonexistent.yaml")
        assert settings.app_name == "ATLAS"


class TestSettingsFromFile:
    """Settings.load() should merge file values over defaults."""

    def test_overrides(self, tmp_path: Path) -> None:
        cfg = tmp_path / "test.yaml"
        cfg.write_text(dedent("""\
            app_name: TEST
            debug: true
            log_level: DEBUG
        """))
        settings = Settings.load(path=cfg)
        assert settings.app_name == "TEST"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        # version falls back to default
        assert settings.version == "0.1.0"

    def test_invalid_log_level(self, tmp_path: Path) -> None:
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("log_level: BANANA\n")
        with pytest.raises(ValueError, match="Invalid log_level"):
            Settings.load(path=cfg)
