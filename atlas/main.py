"""ATLAS entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from atlas.config.settings import Settings
from atlas.core.application import Application

_DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def main() -> None:
    """Parse arguments, load config, and start the application."""
    parser = argparse.ArgumentParser(description="ATLAS — Autonomous Task, Learning and Assistance System")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=_DEFAULT_CONFIG,
        help="Path to YAML configuration file.",
    )
    args = parser.parse_args()

    settings = Settings.load(args.config)
    app = Application(settings)
    app.run()


if __name__ == "__main__":
    main()
