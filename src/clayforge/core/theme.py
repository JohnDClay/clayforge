"""
ClayForge Theming System — Foundation for easy, beautiful theming.

This module provides a simple yet powerful theming API that aligns with
ClayForge's "zero boilerplate + stunning by default" philosophy.

Core ideas:
- Theme objects carry CSS custom properties (vars) + mode (light/dark).
- Global `set_theme()` / `get_theme()` for script-style and runtime control.
- `App(theme=...)` automatically respects your theme for the entire shell.
- Custom components (and future built-ins) can read `get_theme().css_vars`
  to drive colors, or simply use Tailwind + the provided `--cf-*` vars
  in `style=` or arbitrary classes.
- Full backward compatibility: existing hard-coded components continue
  to render exactly as before.

Quick usage (theming):

    import clayforge as cf

    # 1. Simple string mode
    cf.set_theme("light")

    # 2. Full control with CSS var overrides
    cf.set_theme(cf.Theme(
        name="brand",
        mode="dark",
        css_vars={
            "--cf-primary": "#22c55e",      # emerald accent
            "--cf-surface": "#111113",
            "--cf-border": "#27272a",
        }
    ))

    app = cf.App(title="My App", theme="light")  # also works here

    # 3. Inside a custom component
    from clayforge.core.theme import get_theme
    t = get_theme()
    primary = t.css_vars.get("--cf-primary", "#6366f1")

Elegant defaults ship with beautiful zinc + indigo tokens that match
the rest of the design system.

Light/dark improvements:
- Theme.mode controls the initial `class="dark"` on <html>
- CSS vars are always injected so custom UIs and user `classes`/`style`
  can adapt instantly.
- The existing theme-toggle button continues to work (client-side flip
  + persistence). Server-side full theme switching can be added later
  via a small WS handler if desired.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Theme:
    """A first-class, serializable theme configuration.

    This is the central object for ClayForge theming.

    Attributes:
        name: Human identifier ("default", "light", "ocean", "brand-dark"...)
        mode: "dark" | "light" — controls <html> class and default tokens
        css_vars: Mapping of CSS custom properties injected into :root
        tokens: Optional higher-level semantic tokens (future expansion).
                Current built-ins ignore this; use for your own components.

    The generated CSS vars are the primary extension point:
        --cf-bg, --cf-surface, --cf-border, --cf-text, --cf-text-muted,
        --cf-primary, --cf-primary-foreground, etc.

    All values are plain strings (colors, sizes, anything valid in CSS).
    """

    name: str = "default"
    mode: str = "dark"
    css_vars: dict[str, str] = field(default_factory=dict)
    tokens: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        defaults = self._default_css_vars()
        if self.css_vars:
            # Merge: user-provided overrides win, missing keys keep beautiful defaults.
            # This makes partial custom Themes delightful (get() on unset keys still works).
            merged = dict(defaults)
            for k, v in self.css_vars.items():
                kk = k if k.startswith("--") else f"--{k}"
                merged[kk] = v
            self.css_vars = merged
        else:
            self.css_vars = defaults

        # Normalize mode
        self.mode = "light" if str(self.mode).lower() == "light" else "dark"

    def _default_css_vars(self) -> dict[str, str]:
        """Return the production defaults matching ClayForge zinc/indigo aesthetic."""
        if self.mode == "light":
            # Clean, modern light theme (improvement over previous hard-dark only)
            return {
                "--cf-bg": "#fafafa",
                "--cf-surface": "#ffffff",
                "--cf-surface-2": "#f4f4f5",
                "--cf-border": "#e4e4e7",
                "--cf-text": "#18181b",
                "--cf-text-muted": "#52525b",
                "--cf-primary": "#4f46e5",  # indigo-600
                "--cf-primary-foreground": "#ffffff",
                "--cf-accent": "#0ea47a",  # nice emerald-ish
                "--cf-danger": "#dc2626",
                "--cf-success": "#16a34a",
                "--cf-warning": "#ca8a04",
            }
        else:
            # The signature beautiful dark palette (zinc + indigo)
            return {
                "--cf-bg": "#0a0a0a",  # zinc-950
                "--cf-surface": "#18181b",  # zinc-900
                "--cf-surface-2": "#27272a",  # zinc-800
                "--cf-border": "#3f3f46",  # zinc-700-ish
                "--cf-text": "#e4e4e7",  # zinc-200
                "--cf-text-muted": "#a1a1aa",  # zinc-400
                "--cf-primary": "#6366f1",  # indigo-500
                "--cf-primary-foreground": "#0a0a0a",
                "--cf-accent": "#10b981",  # emerald-500
                "--cf-danger": "#ef4444",
                "--cf-success": "#22c55e",
                "--cf-warning": "#eab308",
            }

    def to_style_block(self) -> str:
        """Return a self-contained <style> tag injecting the theme vars.

        Safe to include multiple times; later blocks win for same vars.
        """
        if not self.css_vars:
            return ""
        declarations = "\n".join(f"    {k}: {v};" for k, v in self.css_vars.items())
        return f'<style id="cf-theme-{self.name}">\n:root {{\n{declarations}\n}}\n</style>'

    def get(self, key: str, default: str | None = None) -> str | None:
        """Convenience accessor for a CSS var (with or without leading -- or cf-)."""
        k = key.strip()
        if not k.startswith("--"):
            if k.startswith("cf-"):
                k = f"--{k}"
            else:
                k = f"--cf-{k}"
        return self.css_vars.get(k, default)

    def __repr__(self) -> str:
        return f"<Theme name={self.name!r} mode={self.mode!r} vars={len(self.css_vars)}>"


# ------------------------------------------------------------------
# Global theme state (simple, effective, zero boilerplate)
# ------------------------------------------------------------------

_current_theme: Theme | None = None


def set_theme(theme: Theme | str | dict[str, Any] | None = None) -> Theme:
    """Set (or create) the active global ClayForge theme.

    This is the primary developer entry point for theming.

    Args:
        theme:
            - None / "default" → beautiful dark zinc/indigo defaults
            - "light"          → clean modern light defaults
            - "dark"           → explicit dark defaults
            - Theme instance   → used as-is
            - dict             → treated as css_vars for a custom Theme

    Returns:
        The resulting Theme instance (also stored globally).

    Side effects:
        - Subsequent page renders (new clients or WS ready handshakes)
          will use the theme for <html> class + CSS var injection.
        - Safe to call anytime, including inside page functions.

    Examples:
        cf.set_theme("light")
        cf.set_theme({"--cf-primary": "#f43f5e"})
        cf.set_theme(cf.Theme(name="midnight", mode="dark", css_vars={...}))
    """
    global _current_theme

    if theme is None or theme == "default":
        _current_theme = Theme(name="default", mode="dark")
    elif isinstance(theme, str):
        mode = "light" if theme.lower() == "light" else "dark"
        _current_theme = Theme(name=theme, mode=mode)
    elif isinstance(theme, dict):
        _current_theme = Theme(name="custom", mode="dark", css_vars=theme)
    elif isinstance(theme, Theme):
        _current_theme = theme
    else:
        # Fallback to safe default
        _current_theme = Theme(name="default", mode="dark")

    return _current_theme


def get_theme() -> Theme:
    """Return the currently active theme.

    Always returns a valid Theme (creates the default dark one on first call).
    """
    global _current_theme
    if _current_theme is None:
        _current_theme = Theme(name="default", mode="dark")
    return _current_theme


def apply_theme_to_html(html_class: str = "", extra_style: str = "") -> tuple[str, str]:
    """Helper for shell rendering.

    Returns (final_html_class, additional_head_html)
    where additional_head_html contains the theme's <style> block.
    """
    t = get_theme()
    cls = (html_class or "").strip()
    if t.mode == "dark":
        if "dark" not in cls:
            cls = (cls + " dark").strip()
    else:
        cls = cls.replace("dark", "").strip()

    head_html = t.to_style_block()
    if extra_style:
        head_html += f"\n<style>{extra_style}</style>"
    return cls, head_html


# Public re-exports for nice imports
__all__ = ["Theme", "set_theme", "get_theme", "apply_theme_to_html"]
