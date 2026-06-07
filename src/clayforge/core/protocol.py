"""
ClayForge Minimal WebSocket Protocol (JSON)

Kept deliberately tiny to minimize complexity and attack surface.
This will evolve into proper Pydantic models once the component system is richer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class ServerMessage:
    """Messages the server pushes to a connected client."""

    type: Literal["update", "replace", "toast", "run_js", "error", "ping"]
    element_id: str | None = None
    html: str | None = None
    message: str | None = None
    level: str | None = None
    code: str | None = None


@dataclass
class ClientMessage:
    """Messages coming from the browser."""

    type: Literal["event", "ping", "ready"]
    element_id: str | None = None
    event: str | None = None
    data: dict[str, Any] | None = None
