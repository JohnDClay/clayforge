"""
ClayForge Element Base Class

This is the foundation of the entire component system.

Every visible thing on screen (Text, Button, Row, GrokChat, AgentCanvas, etc.)
is an Element. Elements:
- Know how to render themselves to HTML (server-side initial payload)
- Know how to produce efficient update payloads for the WS
- Can register event handlers that the server will call
- Support context-manager usage for ergonomic layout (with ui.row(): ...)

Design principles:
- Minimal magic
- Extremely fast .to_html()
- Clear ownership (each element belongs to exactly one Client at runtime)
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Element:
    """Base class for all UI elements."""

    id: str = field(default_factory=lambda: f"el_{uuid.uuid4().hex[:10]}")
    classes: str = ""
    style: str = ""
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Element] = field(default_factory=list)

    # Event handlers (populated by .on() or during construction)
    _event_handlers: dict[str, Callable] = field(default_factory=dict, repr=False)

    # Back-reference to owning client (set by the runtime when mounted)
    _client: Any | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # Normalize classes
        if self.classes and not isinstance(self.classes, str):
            self.classes = " ".join(self.classes)

        # ------------------------------------------------------------------
        # Auto-attachment for zero-boilerplate custom components.
        #
        # Any subclass of Element (built-in or user-defined) now "just works"
        # when instantiated inside a @app.page function — whether at top level,
        # inside `with ui.card():`, or returned directly.
        #
        # This centralizes the pattern previously duplicated in GrokChat and
        # makes the custom component story delightful:
        #
        #     class MyFancyWidget(Element):
        #         def to_html(self):
        #             t = get_theme()  # or just use classes/style
        #             ...
        #
        #     # Later:
        #     MyFancyWidget(...)          # works everywhere
        #     cf.register_component(MyFancyWidget, "fancy")
        #     ui.fancy(...)               # also available on the ui namespace
        #
        # The try/except keeps everything robust even if called at import time
        # or outside an active render context.
        # ------------------------------------------------------------------
        try:
            from .ui import _maybe_attach_or_root

            _maybe_attach_or_root(self)
        except Exception:
            # Silent — attachment is a pure DX convenience.
            # Manual .add_child() and direct root returns still work.
            pass

    # ------------------------------------------------------------------
    # Public fluent API (beautiful DX)
    # ------------------------------------------------------------------

    def on(self, event: str, handler: Callable) -> Element:
        """Register an event handler (click, change, submit, etc.)."""
        self._event_handlers[event] = handler
        return self

    def add_class(self, *cls: str) -> Element:
        existing = (self.classes or "").split()
        for c in cls:
            if c not in existing:
                existing.append(c)
        self.classes = " ".join(existing)
        return self

    def add_child(self, child: Element) -> Element:
        self.children.append(child)
        return self

    # Context manager support: with ui.row(): ui.text("hi")
    # The actual push/pop is implemented in ui.py to avoid import cycles.
    # These methods use lazy imports so Element can be imported first.
    def __enter__(self) -> Element:
        """Enter context — registers this element as the current parent for child collection."""
        from .ui import _push_context

        _push_context(self)
        return self

    def __exit__(self, *exc: Any) -> None:
        """Exit context — pops from the active container stack."""
        from .ui import _pop_context

        _pop_context()
        # Do not swallow exceptions — let them propagate naturally.

    # ------------------------------------------------------------------
    # Rendering (the heart of ClayForge)
    # ------------------------------------------------------------------

    def to_html(self) -> str:
        """Return the initial server-rendered HTML for this element.

        Subclasses MUST override. This default gives a visible box so
        people can see something is working during development.
        """
        inner = "".join(c.to_html() for c in self.children) or self._default_inner_html()
        cls = f" {self.classes}" if self.classes else ""
        style = f' style="{self.style}"' if self.style else ""
        extra = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        extra = f" {extra}" if extra else ""

        tag = self._html_tag()
        return f'<{tag} id="{self.id}" class="cf-element{cls}"{style}{extra}>{inner}</{tag}>'

    def to_update_payload(self) -> dict[str, Any]:
        """Return the minimal dict the WS client will use to patch the DOM."""
        return {
            "id": self.id,
            "html": self.to_html(),
        }

    def _html_tag(self) -> str:
        return "div"

    def _default_inner_html(self) -> str:
        return ""

    # ------------------------------------------------------------------
    # Event dispatch (called by the server layer)
    # ------------------------------------------------------------------

    def handle_event(self, event_name: str, data: dict[str, Any]) -> Any:
        """Invoke the registered handler if present. Return value can be used for responses."""
        handler = self._event_handlers.get(event_name)
        if handler:
            return handler(data)
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} children={len(self.children)}>"
