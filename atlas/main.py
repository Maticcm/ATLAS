"""ATLAS entry point."""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

# Suppress noisy library warnings for a cleaner CLI experience
warnings.filterwarnings("ignore", category=UserWarning, module="perth")
warnings.filterwarnings("ignore", category=FutureWarning, module="diffusers")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

# Prevent Fortran runtime from aggressively aborting the process on Ctrl+C
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"
# Suppress HF Hub token warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

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
