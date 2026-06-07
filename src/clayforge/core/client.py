"""
ClayForge Client Manager + Per-Client Connection

Minimal, dependency-free (besides FastAPI/Starlette WebSocket).

Responsibilities in this foundation:
- Track active connections
- Provide high-level send helpers used by the demo server
- Prepare the ground for the real element registry + outbox pattern
"""

from __future__ import annotations

import asyncio
from typing import Any

from starlette.websockets import WebSocket


class Client:
    """Represents one browser tab / session.

    In addition to the websocket, each Client now holds the live element
    registry for the current page render. This enables O(1) dispatch of
    button clicks and other events back to the exact Python Element + handler
    that the user registered via ui.button(on_click=...) or .on().
    """

    def __init__(self, client_id: str, websocket: WebSocket) -> None:
        self.id = client_id
        self.ws = websocket
        self.session_state: dict = {}
        self.connected_at = asyncio.get_event_loop().time()

        # Live element tree for the page currently served to this client.
        # Populated on WS "ready" (and on future navigation / page switches).
        self._element_registry: dict[
            str, Any
        ] = {}  # id -> Element (use Any to avoid heavy imports)

    async def send_json(self, payload: dict) -> None:
        if self.ws.client_state.name == "CONNECTED":
            await self.ws.send_json(payload)

    async def send_update(self, element_id: str, html: str) -> None:
        await self.send_json({"type": "update", "element_id": element_id, "html": html})

    async def send_replace(self, element_id: str, html: str) -> None:
        await self.send_json({"type": "replace", "element_id": element_id, "html": html})

    async def send_toast(self, message: str, level: str = "info") -> None:
        await self.send_json({"type": "toast", "message": message, "level": level})

    async def send_run_js(self, code: str) -> None:
        await self.send_json({"type": "run_js", "code": code})

    async def send_error(self, message: str) -> None:
        await self.send_json({"type": "error", "message": message})

    # ------------------------------------------------------------------
    # Element registry for real page event routing
    # ------------------------------------------------------------------

    def register_elements(self, elements: list[Any]) -> None:
        """Register every Element produced by render_page().

        Called on every fresh page render (initial + ready handshake).
        Enables the WS event handler to locate the exact object and invoke
        its Python .handle_event / user callbacks.
        """
        for el in elements:
            if hasattr(el, "id"):
                self._element_registry[el.id] = el

    def get_element(self, element_id: str) -> Any | None:
        """Fast lookup used by the server event dispatcher."""
        return self._element_registry.get(element_id)


class ClientManager:
    """Global registry of live clients. Very simple for current version (per-client element registry powers real reactivity)."""

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> Client:
        client = Client(client_id, websocket)
        self._clients[client_id] = client
        return client

    async def disconnect(self, client_id: str) -> None:
        self._clients.pop(client_id, None)

    def get(self, client_id: str) -> Client | None:
        return self._clients.get(client_id)

    def count(self) -> int:
        return len(self._clients)

    async def broadcast(self, payload: dict) -> None:
        """Send to everyone (useful later for multi-user features)."""
        for client in list(self._clients.values()):
            try:
                await client.send_json(payload)
            except Exception:
                pass
