"""
ClayForge
=========

The next-generation, AI-native Python web framework.

Usage (script-style):
    import clayforge as cf

    app = cf.App(title="My App", theme="light")

    @app.page("/")
    def main():
        cf.ui.title("Hello")
        if cf.ui.button("Click"):
            cf.ui.success("Beautiful, zero boilerplate.")
        cf.ui.select("Priority", ["Low", "High"], "Low")

Theming:
    cf.set_theme("light")
    cf.set_theme(cf.Theme(name="brand", css_vars={"--cf-primary": "#22c55e"}))

State (first-class, simple):
    def handler(data):
        st = cf.get_session_state()
        st["key"] = data.get("value")
    # + element.refresh() after changes; on_change= supported on forms.

Custom components:
    class MyWidget(cf.Element): ...
    cf.register_component(MyWidget, "my_widget")
    # Now works: cf.ui.my_widget(...)  and also direct MyWidget(...)

Public API is intentionally small and stable.
"""

from __future__ import annotations

from typing import Any

__version__ = "0.2.0-alpha"

# Re-export the main user-facing symbols
# Optional but first-class modules: auth + db
# These are always importable (zero boilerplate philosophy).
#   import clayforge as cf
#   from clayforge import auth, db
#   auth = auth.Auth()          # cookie/session auth
#   db = db.Database()          # SQLite + Postgres (async friendly)
from .auth import Auth, auth
from .core.app import App, page
from .core.element import Element  # Base for easy custom components: class MyThing(Element): ...
from .core.theme import (  # Theming foundation (cf.set_theme, App(theme=...))
    Theme,
    get_theme,
    set_theme,
)
from .core.ui import (  # ui.* + custom component API
    get_client,
    get_registered_components,
    get_session_state,
    register_component,
    ui,
)
from .db import Database, db

# Visualization components (optional but first-class — gated behind the "viz" extra)
# Users can do:
#     from clayforge import PlotlyChart, DataTable
#     from clayforge.components.viz import PlotlyChart, DataTable
#
# Both forms work. If the optional "viz" dependencies are missing, importing
# the names succeeds but instantiating them raises a clear, actionable error:
#     ImportError: PlotlyChart requires ... pip install "clayforge[viz]"
#
# This gives an *excellent* import experience: clayforge always imports cleanly,
# while usage fails fast with instructions instead of confusing NoneType errors.
try:
    from .components.viz import DataTable, PlotlyChart  # type: ignore
except Exception:
    # Provide excellent UX stubs instead of None.
    # They raise a helpful error only on *use*, matching the documented contract.
    class _VizComponentUnavailable:
        """Placeholder that produces an actionable error when used without the viz extra."""

        _name: str = "VizComponent"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                f"{self._name} requires optional dependencies.\n\n"
                f"Install with:\n"
                f'    pip install "clayforge[viz]"\n'
                f'    # or for production (recommended): pip install "clayforge[viz,grok]"\n\n'
                f"Then re-run your app. (plotly + pandas + altair for rich visualizations)"
            )

    class PlotlyChart(_VizComponentUnavailable):  # type: ignore
        _name = "PlotlyChart"

    class DataTable(_VizComponentUnavailable):  # type: ignore
        _name = "DataTable"


# Convenience: allow "from clayforge import ui"
# The real implementation lives in core/ui.py (or populated dynamically)
# For the very first milestone we provide a minimal stub that will grow.

# Public version info
__all__ = [
    "App",
    "page",
    "ui",
    "register_component",
    "get_registered_components",
    "Theme",
    "set_theme",
    "get_theme",
    "Element",
    "PlotlyChart",
    "DataTable",
    # New in this milestone: optional but beautifully integrated
    "Auth",
    "auth",
    "Database",
    "db",
    "get_client",
    "get_session_state",
    "__version__",
]

# Note: Full ui.* components are registered at import time from elements.
# This file will be expanded as the component system comes online.
