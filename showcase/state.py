"""
Showcase Demo State

Centralized in-memory demo state for the ClayForge Showcase.
Used for initial render values in dashboard, etc.
Client-side JS demos may mutate DOM directly for interactivity (preserves original behavior).
"""

from typing import Any

STATE: dict[str, Any] = {
    "users": 1248,
    "revenue": 48290,
}

__all__ = ["STATE"]
