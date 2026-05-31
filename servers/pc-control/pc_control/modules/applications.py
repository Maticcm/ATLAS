"""Applications module for PC Control."""

import subprocess
import psutil
from pydantic import BaseModel, Field

from pc_control.registry import tool

class OpenApplicationSchema(BaseModel):
    name: str = Field(description="The name or path of the application to open (e.g., 'notepad', 'calc', 'C:\\Path\\To\\App.exe')")

@tool(
    name="open_application",
    description="Open an application by name or path.",
    schema=OpenApplicationSchema
)
def open_application(name: str) -> str:
    """Launch an application."""
    try:
        # Use subprocess to launch in the background
        subprocess.Popen(name, shell=True)
        return f"Launched {name}"
    except Exception as exc:
        raise RuntimeError(f"Failed to launch {name}: {exc}")

class CloseApplicationSchema(BaseModel):
    name: str = Field(description="The exact executable name of the process to close (e.g., 'notepad.exe')")

@tool(
    name="close_application",
    description="Close an application by its process name.",
    schema=CloseApplicationSchema
)
def close_application(name: str) -> str:
    """Terminate a running process."""
    name_lower = name.lower()
    closed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name_lower:
                proc.terminate()
                closed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if closed == 0:
        return f"No process found with name {name}"
    return f"Closed {closed} instance(s) of {name}"

@tool(
    name="list_running_processes",
    description="List all running processes (names and PIDs).",
    schema=None
)
def list_running_processes() -> list[dict[str, str | int]]:
    """Get a list of all processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name']:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Return unique names to avoid huge lists
    seen = set()
    unique = []
    for p in processes:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
            
    return sorted(unique, key=lambda x: x["name"].lower())
