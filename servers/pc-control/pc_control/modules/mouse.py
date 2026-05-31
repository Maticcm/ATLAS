"""Mouse module for PC Control."""

import pyautogui
from pydantic import BaseModel, Field

from pc_control.registry import tool

class MoveMouseSchema(BaseModel):
    x: int = Field(description="The X coordinate to move to")
    y: int = Field(description="The Y coordinate to move to")

@tool(
    name="move_mouse",
    description="Move the mouse cursor to absolute coordinates.",
    schema=MoveMouseSchema
)
def move_mouse(x: int, y: int) -> str:
    """Move the mouse."""
    pyautogui.moveTo(x, y, duration=0.2)
    return f"Mouse moved to ({x}, {y})"

class ClickSchema(BaseModel):
    button: str = Field(default="left", description="The mouse button to click ('left', 'middle', 'right')")

@tool(
    name="click",
    description="Click the mouse at the current position.",
    schema=ClickSchema
)
def click(button: str = "left") -> str:
    """Click the mouse."""
    pyautogui.click(button=button)
    return f"Clicked '{button}' button"

@tool(
    name="double_click",
    description="Double-click the mouse at the current position.",
    schema=ClickSchema
)
def double_click(button: str = "left") -> str:
    """Double-click the mouse."""
    pyautogui.doubleClick(button=button)
    return f"Double-clicked '{button}' button"

@tool(
    name="right_click",
    description="Right-click the mouse at the current position.",
    schema=None
)
def right_click() -> str:
    """Right-click the mouse."""
    pyautogui.rightClick()
    return "Right-clicked"
