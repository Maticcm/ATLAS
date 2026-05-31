"""Screen module for PC Control."""

import os
import time
from pathlib import Path

import pyautogui
from pydantic import BaseModel

from pc_control.registry import tool

@tool(
    name="get_screen_resolution",
    description="Get the dimensions of the primary monitor.",
    schema=None
)
def get_screen_resolution() -> dict[str, int]:
    """Get screen size."""
    w, h = pyautogui.size()
    return {"width": w, "height": h}

@tool(
    name="screenshot",
    description="Take a screenshot and save it locally.",
    schema=None
)
def screenshot() -> str:
    """Take a screenshot."""
    # Ensure a directory for screenshots
    out_dir = Path("screenshots")
    out_dir.mkdir(exist_ok=True)
    
    filename = out_dir / f"screenshot_{int(time.time())}.png"
    # Take screenshot and save
    pyautogui.screenshot(str(filename))
    
    return f"Screenshot saved to {filename.absolute()}"
