"""
ClayForge Example 01 — Hello Beautiful

The simplest possible beautiful app that demonstrates:
- Modern defaults (Tailwind + shadcn aesthetic)
- Reactive WebSocket updates (no page reloads)
- Script-style pure Python API
- Theming (cf.set_theme + App(theme=...) + CSS vars)
- Easy custom component registration (register_component + auto-attach)

Run:
    python examples/01_hello_beautiful.py
    # or
    clayforge run --app examples.01_hello_beautiful:app
"""

from typing import Any

import clayforge as cf
from clayforge.core.element import Element
from clayforge.core.theme import get_theme

# ------------------------------------------------------------------
# SMALL EXAMPLE: Custom component + theming (new foundation features)
# ------------------------------------------------------------------
# This demonstrates both deliverables in one tiny, self-contained block.
# Everything continues to work exactly as before for all other code.


class ThemedPill(Element):
    """A tiny custom component that respects the active ClayForge theme.

    Shows how easy it is to build your own beautiful components that
    automatically get CSS variable access + zero-boilerplate attachment.
    """

    def __init__(self, text: str, variant: str = "primary", **kwargs: Any):
        self.text = text
        self.variant = variant
        super().__init__(**kwargs)  # triggers auto-attach magic

    def to_html(self) -> str:
        t = get_theme()
        # Read from the live theme (set via App(theme=...) or cf.set_theme)
        primary = t.get("primary", "#6366f1")
        if self.variant == "accent":
            bg = f"{primary}15"
            fg = primary
        else:
            bg = "var(--cf-surface-2)"
            fg = "var(--cf-text-muted)"

        return (
            f'<span id="{self.id}" '
            f'style="display:inline-flex; align-items:center; '
            f"background:{bg}; color:{fg}; font-size:11px; "
            f"padding:1px 9px; border-radius:9999px; "
            f'border:1px solid var(--cf-border); font-weight:500;">'
            f"{self.text}</span>"
        )


# Register it — now ui.themed_pill(...) works everywhere exactly like ui.badge
cf.register_component(ThemedPill, "themed_pill")


app = cf.App(title="ClayForge • Hello Beautiful", theme="dark")


@app.page("/")
def hello():
    cf.ui.title("Hello, ClayForge")
    cf.ui.subtitle("The most beautiful Python web apps you've ever written — in minutes.")

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="What you get for free", subtitle="No design work required"):
            cf.ui.text("• Stunning Tailwind + zinc/indigo design system")
            cf.ui.text("• Instant WebSocket reactivity")
            cf.ui.text("• Dark mode + perfect typography")
            cf.ui.text("• Production FastAPI backend")

            # NEW: Using our registered custom component (respects current theme vars)
            cf.ui.themed_pill("THEME-AWARE", variant="primary")
            cf.ui.themed_pill("CUSTOM", variant="accent", classes="ml-2")

            def on_demo_click():
                print("[Example] Primary button clicked on server side! (real roundtrip)")

            cf.ui.button(
                "Click me — server roundtrip",
                variant="primary",
                classes="mt-4",
                on_click=on_demo_click,
            )

        with cf.ui.card(title="Next Steps", subtitle="You're 3 minutes in"):
            cf.ui.markdown(
                "1. Edit this file<br>"
                "2. Add more `cf.ui.*` calls<br>"
                '3. `pip install "clayforge[grok]"`<br>'
                "4. Add `GrokChat(...)` for instant AI"
            )

    cf.ui.footer("Example 01 • Theming + custom components now built-in • Pure Python • 2026")


if __name__ == "__main__":
    app.run()
