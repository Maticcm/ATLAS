"""Keyboard module for PC Control."""

import pyautogui
from pydantic import BaseModel, Field

from pc_control.registry import tool

class TypeTextSchema(BaseModel):
    text: str = Field(description="The text to type")

@tool(
    name="type_text",
    description="Type a string of text as if on a keyboard.",
    schema=TypeTextSchema
)
def type_text(text: str) -> str:
    """Type text."""
    pyautogui.write(text, interval=0.01)
    return f"Typed {len(text)} characters"

class PressKeySchema(BaseModel):
    key: str = Field(description="The key to press (e.g., 'enter', 'esc', 'tab', 'a')")

@tool(
    name="press_key",
    description="Press a single key.",
    schema=PressKeySchema
)
def press_key(key: str) -> str:
    """Press a key."""
    pyautogui.press(key)
    return f"Pressed '{key}'"

class HotkeySchema(BaseModel):
    keys: list[str] = Field(description="A list of keys to press together (e.g., ['ctrl', 'c'])")

@tool(
    name="hotkey",
    description="Press a combination of keys together.",
    schema=HotkeySchema
)
def hotkey(keys: list[str]) -> str:
    """Press a hotkey."""
    pyautogui.hotkey(*keys)
    return f"Pressed hotkey: {'+'.join(keys)}"
