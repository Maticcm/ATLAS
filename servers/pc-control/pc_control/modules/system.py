"""System module for PC Control."""

import ctypes
import psutil
from pydantic import BaseModel

from pc_control.registry import tool

@tool(
    name="lock_pc",
    description="Lock the Windows workstation.",
    schema=None
)
def lock_pc() -> str:
    """Lock the PC."""
    ctypes.windll.user32.LockWorkStation()
    return "PC locked"

@tool(
    name="get_system_info",
    description="Get basic system utilization information (CPU, RAM, Disk).",
    schema=None
)
def get_system_info() -> dict[str, str | float]:
    """Get system info."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu,
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "ram_used_gb": round(mem.used / (1024**3), 2),
        "ram_percent": mem.percent,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_percent": disk.percent
    }
