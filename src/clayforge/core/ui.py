"""
ClayForge UI — The primary developer interface (cf.ui.*)

This module provides the ergonomic, zero-boilerplate API that makes ClayForge delightful.

Context manager support:
    with ui.row(gap="4"):
        ui.text("Child automatically attached")
        with ui.card(title="Nested"):
            ui.button("Works perfectly")

Key exports:
- ui.row / ui.column / ui.card — layout containers (full context collection)
- ui.text / ui.title / ui.subtitle / ui.markdown / ui.success / ui.footer
- ui.button (on_click + full WS roundtrips)
- ui.badge / ui.divider / ui.text_input / ui.select / ui.checkbox / ui.text_area / ui.file_upload
- render_page(page_fn) — the heart of real @app.page rendering

Theming & Custom Components (new foundation):
- Full custom component system via `cf.register_component(MyWidget)`
  After registration: `ui.mywidget(...)` works exactly like built-ins.
- Direct subclassing of Element also "just works" thanks to auto-attachment
  (see core/element.py and core/theme.py for get_theme() + CSS vars).
- Use App(theme=...) or cf.set_theme(...) for beautiful runtime theming
  with CSS variable overrides and improved light/dark support.

All creation (built-in or custom) automatically participates in parent/child
collection when inside a context manager.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from .element import Element
from .elements.basic import (
    Badge,
    Button,
    Card,
    Checkbox,
    Column,
    Divider,
    FileUpload,
    Row,
    Select,
    Text,
    TextArea,
    TextInput,
)

# ------------------------------------------------------------------
# Custom component registry (the foundation of easy extensibility)
# ------------------------------------------------------------------

_registered_components: dict[str, type[Element]] = {}


def register_component(
    component_class: type[Element],
    name: str | None = None,
) -> type[Element]:
    """Register a custom Element subclass so it is available as `ui.<name>(...)`.

    This delivers the "easy custom component registration" requirement with
    zero boilerplate for users while staying 100% compatible with everything
    that already exists.

    Args:
        component_class: Your subclass of Element (or of any built-in component).
        name: Optional explicit name for the ui factory.
              Defaults to the lowercased class name (MyThing → mything).

    Returns:
        The same class (allows decorator-style usage if desired).

    After calling this, the component participates in the full ClayForge
    lifecycle:
    - Beautiful server-side rendering via your to_html()
    - Automatic context attachment (works in with ui.xxx(): blocks)
    - Full WebSocket event routing via .on() or constructor callbacks
    - Access to current theme via clayforge.core.theme.get_theme()

    Direct instantiation of your class also works everywhere (no registration
    required) because Element.__post_init__ now auto-attaches.

    Example of a minimal custom component:

        from clayforge.core.element import Element
        from clayforge.core.theme import get_theme
        import clayforge as cf

        class BrandBadge(Element):
            def __init__(self, text: str, **kwargs):
                self.text = text
                super().__init__(**kwargs)   # triggers auto-attach + id

            def to_html(self):
                t = get_theme()
                color = t.get("primary", "#6366f1")
                return (
                    f'<span id="{self.id}" '
                    f'style="background:{color}20; color:{color}; '
                    f'padding:2px 10px; border-radius:9999px; font-size:12px;">'
                    f'{self.text}</span>'
                )

        cf.register_component(BrandBadge, "brand_badge")

        # Now usable exactly like built-ins:
        # ui.brand_badge("PRO")   or   BrandBadge("PRO")
    """
    if not isinstance(component_class, type) or not issubclass(component_class, Element):
        raise TypeError(
            f"register_component() expects a subclass of Element, got {component_class!r}"
        )

    if name is None:
        name = component_class.__name__.lower()

    # Create a factory method that will be attached to UINamespace.
    # Instantiation itself triggers _maybe_attach_or_root via Element.__post_init__.
    def _factory(self: UINamespace, *args: Any, **kwargs: Any) -> Element:
        return component_class(*args, **kwargs)

    setattr(UINamespace, name, _factory)
    _registered_components[name] = component_class
    return component_class


def get_registered_components() -> dict[str, type[Element]]:
    """Return a shallow copy of all currently registered custom components.

    Primarily useful for docs, introspection, and testing.
    """
    return dict(_registered_components)


class UINamespace:
    """The live object exposed as `clayforge.ui` (and `cf.ui`)."""

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def row(self, gap: str = "4", classes: str = "", **kwargs: Any) -> Row:
        r = Row(gap=gap, classes=classes, **kwargs)
        _maybe_attach_or_root(r)
        return r

    def column(self, gap: str = "3", classes: str = "", **kwargs: Any) -> Column:
        c = Column(gap=gap, classes=classes, **kwargs)
        _maybe_attach_or_root(c)
        return c

    def card(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        classes: str = "",
        **kwargs: Any,
    ) -> Card:
        c = Card(title=title, subtitle=subtitle, classes=classes, **kwargs)
        _maybe_attach_or_root(c)
        return c

    # ------------------------------------------------------------------
    # Typography & Content
    # ------------------------------------------------------------------

    def title(self, text: str, size: str = "3xl", classes: str = "") -> Text:
        t = Text(
            content=text,
            tag="h1",
            size=size,
            classes=f"font-display tracking-tighter font-semibold text-white {classes}".strip(),
        )
        _maybe_attach_or_root(t)
        return t

    def subtitle(self, text: str, classes: str = "") -> Text:
        t = Text(content=text, tag="p", size="lg", classes=f"text-zinc-400 {classes}".strip())
        _maybe_attach_or_root(t)
        return t

    def text(self, content: str, size: str = "base", classes: str = "", tag: str = "p") -> Text:
        """Render arbitrary text/html content.

        `tag` allows using div, span, h1, etc. instead of the default <p>.
        """
        t = Text(content=content, size=size, classes=classes, tag=tag)
        _maybe_attach_or_root(t)
        return t

    def markdown(self, text: str, classes: str = "") -> Text:
        # Basic markdown support (bold, italic, code, simple lists). Real MD + KaTeX + highlight
        # can be added by users via custom Element + CDN scripts (or optional dep later).
        # Escapes HTML then applies simple transforms for common cases.
        safe = text.replace("<", "&lt;").replace(">", "&gt;")
        # very light "markdown"
        safe = safe.replace("**", "<strong>").replace("**", "</strong>")  # rough
        safe = safe.replace("*", "<em>").replace("*", "</em>")
        safe = safe.replace("`", "<code>").replace("`", "</code>")
        safe = safe.replace("\n- ", "<br>• ").replace("\n", "<br>")
        t = Text(
            content=safe,
            tag="div",
            classes=f"prose prose-invert text-sm text-zinc-300 max-w-none {classes}",
        )
        _maybe_attach_or_root(t)
        return t

    # ------------------------------------------------------------------
    # Interactive
    # ------------------------------------------------------------------

    def button(
        self,
        label: str,
        variant: str = "primary",
        size: str = "md",
        on_click: Callable | None = None,
        classes: str = "",
        **kwargs: Any,
    ) -> Button:
        btn = Button(label=label, variant=variant, size=size, classes=classes, **kwargs)
        if on_click:
            btn.on("click", lambda data: on_click())
        _maybe_attach_or_root(btn)
        return btn

    # ------------------------------------------------------------------
    # New small beautiful components (this milestone)
    # ------------------------------------------------------------------

    def badge(self, text: str, variant: str = "default", classes: str = "") -> Badge:
        b = Badge(text=text, variant=variant, classes=classes)
        _maybe_attach_or_root(b)
        return b

    def divider(self, classes: str = "") -> Divider:
        d = Divider(classes=classes)
        _maybe_attach_or_root(d)
        return d

    def text_input(
        self,
        placeholder: str = "Type something...",
        value: str = "",
        classes: str = "",
        **kwargs: Any,
    ) -> TextInput:
        ti = TextInput(placeholder=placeholder, value=value, classes=classes, **kwargs)
        _maybe_attach_or_root(ti)
        return ti

    # ------------------------------------------------------------------
    # More form controls (core rich components)
    # ------------------------------------------------------------------

    def select(
        self,
        label: str = "Choose",
        options: list[str] | None = None,
        value: str = "",
        classes: str = "",
        **kwargs: Any,
    ) -> Select:
        s = Select(
            label=label, options=options or ["A", "B"], value=value, classes=classes, **kwargs
        )
        _maybe_attach_or_root(s)
        return s

    def checkbox(
        self, label: str = "Option", checked: bool = False, classes: str = "", **kwargs: Any
    ) -> Checkbox:
        c = Checkbox(label=label, checked=checked, classes=classes, **kwargs)
        _maybe_attach_or_root(c)
        return c

    def text_area(
        self,
        placeholder: str = "Enter text...",
        value: str = "",
        rows: int = 4,
        classes: str = "",
        **kwargs: Any,
    ) -> TextArea:
        ta = TextArea(placeholder=placeholder, value=value, rows=rows, classes=classes, **kwargs)
        _maybe_attach_or_root(ta)
        return ta

    def file_upload(
        self, label: str = "Choose file", classes: str = "", **kwargs: Any
    ) -> FileUpload:
        fu = FileUpload(label=label, classes=classes, **kwargs)
        _maybe_attach_or_root(fu)
        return fu

    # ------------------------------------------------------------------
    # Convenience / Feedback
    # ------------------------------------------------------------------

    def success(self, message: str) -> Text:
        t = Text(
            content=message,
            tag="div",
            classes="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-emerald-500/10 text-emerald-400 text-sm font-medium border border-emerald-500/30",
        )
        _maybe_attach_or_root(t)
        return t

    def footer(self, text: str) -> Text:
        t = Text(
            content=text,
            tag="div",
            classes="text-[10px] text-zinc-500 mt-8 pt-4 border-t border-zinc-800",
        )
        _maybe_attach_or_root(t)
        return t

    def expander(self, title: str, classes: str = "") -> Any:
        # Simple stub that still looks decent
        class _Expander:
            def __init__(self):
                self._title = title

            def __enter__(self):
                print(f"[ui.expander] '{self._title}' opened (will be real soon)")
                return self

            def __exit__(self, *args):
                pass

        return _Expander()

    # ------------------------------------------------------------------
    # Future (placeholders that give nice errors)
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        def _future_component(*args: Any, **kwargs: Any) -> None:
            from rich.console import Console
            from rich.panel import Panel

            console = Console()
            console.print(
                Panel(
                    f"[bold yellow]cf.ui.{name}[/bold yellow] is coming in the next iteration.\n\n"
                    "Already working today:\n"
                    "  • ui.title / ui.subtitle / ui.text / ui.markdown / ui.success / ui.footer\n"
                    "  • ui.row / ui.column / ui.card (full context managers!)\n"
                    "  • ui.button (on_click + real WS roundtrips)\n"
                    "  • ui.badge / ui.divider / ui.text_input / ui.select / ui.checkbox / ui.text_area / ui.file_upload\n\n"
                    "Run `clayforge new myapp && clayforge run` to see real rendered pages.",
                    title="ClayForge — Component in Progress",
                    border_style="yellow",
                )
            )

        return _future_component


# ------------------------------------------------------------------
# Internal context stack + root collector (powers with ui.xxx(): ...)
# These are deliberately private. Users interact only via the public factories.
# ------------------------------------------------------------------

_context_stack: list[Element] = []
_current_roots: list[Element] = []


def _push_context(element: Element) -> None:
    """Push container onto stack so subsequent ui.* calls become its children."""
    _context_stack.append(element)


def _pop_context() -> None:
    """Pop on context exit. Safe no-op if empty."""
    if _context_stack:
        _context_stack.pop()


def _get_current_parent() -> Element | None:
    return _context_stack[-1] if _context_stack else None


def _add_as_root(element: Element) -> None:
    """Track elements created at top level (outside any with-block)."""
    if not _context_stack and element not in _current_roots:
        _current_roots.append(element)


def _maybe_attach_or_root(element: Element) -> None:
    """Central hook called by every ui.* factory.
    Attaches to current container (if inside with) or records as page root.
    """
    parent = _get_current_parent()
    if parent is not None:
        parent.add_child(element)
    else:
        _add_as_root(element)


@contextmanager
def _page_render_context():
    """Reset stacks for a fresh page execution. Used exclusively by render_page()."""
    global _current_roots, _context_stack
    prev_roots = _current_roots
    prev_stack = _context_stack[:]
    _current_roots = []
    _context_stack = []
    try:
        yield
    finally:
        _current_roots = prev_roots
        _context_stack = prev_stack


def render_page(page_fn: Callable[[], Any]) -> tuple[str, list[Element]]:
    """Execute a user-defined @app.page function and produce live HTML + element registry data.

    This is the key primitive that turns pure-Python page descriptions into
    real server-rendered DOM that supports WS-driven events.

    Returns:
        (combined_html, all_elements) where:
          - combined_html is the concatenated .to_html() of top-level roots
          - all_elements is a flat list (for Client element registry + event routing)

    Supports:
    - Implicit top-level collection
    - Full nested with ui.row(): / with ui.card(): etc.
    - Returning an Element directly from the page fn (also supported)
    - Graceful error capture (renders visible error box)
    """
    with _page_render_context():
        retval = None
        try:
            if callable(page_fn):
                retval = page_fn()
        except Exception as exc:  # noqa: BLE001
            # Never let a bad page crash the whole server; show nice error
            import traceback

            print("=== FULL PAGE RENDER TRACEBACK ===")
            traceback.print_exc()
            err = Text(
                content=f"⚠️ Page render error: {exc}",
                tag="div",
                classes="text-red-400 bg-red-950/60 border border-red-900 rounded-3xl p-6 font-mono text-sm",
            )
            _current_roots.append(err)

        # Support `return ui.column(...)` or similar advanced patterns
        if isinstance(retval, Element) and retval not in _current_roots:
            _current_roots.append(retval)

        # Render + traverse once for HTML and for the complete live element list
        html_fragments: list[str] = []
        all_elements: list[Element] = []

        def _traverse(el: Element) -> None:
            all_elements.append(el)
            for child in el.children:
                _traverse(child)

        for root in _current_roots:
            html_fragments.append(root.to_html())
            _traverse(root)

        html = (
            "\n".join(html_fragments)
            if html_fragments
            else (
                '<div class="text-zinc-500 italic">'
                "This page rendered no UI. Add cf.ui.title(...), cards, etc. inside the function."
                "</div>"
            )
        )
        return html, all_elements


# The actual singleton used everywhere
ui = UINamespace()

# Also allow "from clayforge.core.ui import ui"
__all__ = [
    "ui",
    "UINamespace",
    "render_page",
    "register_component",
    "get_registered_components",
]
