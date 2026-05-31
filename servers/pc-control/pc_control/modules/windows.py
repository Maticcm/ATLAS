"""Windows module for PC Control."""

import win32gui
import win32con
from pydantic import BaseModel, Field

from pc_control.registry import tool

def _get_hwnds_by_title(title_substring: str) -> list[int]:
    """Find all HWNDs whose title contains the substring."""
    hwnds = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            text = win32gui.GetWindowText(hwnd)
            if title_substring.lower() in text.lower():
                hwnds.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return hwnds

class WindowTitleSchema(BaseModel):
    title: str = Field(description="A substring of the window title to match (e.g., 'Chrome', 'Notepad')")

@tool(
    name="list_windows",
    description="List all visible windows.",
    schema=None
)
def list_windows() -> list[dict[str, str]]:
    """Return a list of all visible window titles."""
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            text = win32gui.GetWindowText(hwnd)
            if text:
                windows.append({"hwnd": str(hwnd), "title": text})
    win32gui.EnumWindows(callback, None)
    return windows

@tool(
    name="focus_window",
    description="Bring a window to the foreground by its title.",
    schema=WindowTitleSchema
)
def focus_window(title: str) -> str:
    hwnds = _get_hwnds_by_title(title)
    if not hwnds:
        return f"No window found matching '{title}'"
    
    hwnd = hwnds[0]
    # Sometimes windows need to be restored first if minimized
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    return f"Focused window: {win32gui.GetWindowText(hwnd)}"

@tool(
    name="minimize_window",
    description="Minimize a window by its title.",
    schema=WindowTitleSchema
)
def minimize_window(title: str) -> str:
    hwnds = _get_hwnds_by_title(title)
    if not hwnds:
        return f"No window found matching '{title}'"
    
    hwnd = hwnds[0]
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    return f"Minimized window: {win32gui.GetWindowText(hwnd)}"

@tool(
    name="maximize_window",
    description="Maximize a window by its title.",
    schema=WindowTitleSchema
)
def maximize_window(title: str) -> str:
    hwnds = _get_hwnds_by_title(title)
    if not hwnds:
        return f"No window found matching '{title}'"
    
    hwnd = hwnds[0]
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    return f"Maximized window: {win32gui.GetWindowText(hwnd)}"
