"""
ClayForge App — The central user-facing object.

Responsibilities:
- Page registry (@app.page)
- Theme + global config (now fully wired — see Theme + set_theme)
- .run() convenience launcher

Theming example:
    app = cf.App(title="Dashboard", theme="light")
    # or
    app = cf.App(theme=cf.Theme(name="corporate", mode="light", css_vars={...}))
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Theming support — applied automatically when you pass theme= to App
from .theme import Theme, set_theme


class App:
    """The main ClayForge application container.

    Theming is now first-class:

        app = cf.App(
            title="My Product",
            theme="light",                    # or "dark"
            # or a rich Theme object / dict of CSS vars:
            # theme=cf.Theme(name="brand", css_vars={"--cf-primary": "#ec4899"})
        )

    The provided theme automatically influences:
    - The initial light/dark class on the <html> element
    - Injection of beautiful CSS custom properties (--cf-*) into every page
    - Any custom components you build (via clayforge.core.theme.get_theme())

    Existing behavior for non-theme arguments is unchanged.
    """

    def __init__(
        self,
        title: str = "ClayForge App",
        description: str = "",
        theme: str | dict[str, Any] | Theme = "default",
        **kwargs: Any,
    ) -> None:
        self.title = title
        self.description = description
        self.config: dict[str, Any] = kwargs
        self._pages: dict[str, Callable] = {}
        # API route registry for the new "expose Python functions as API routes" feature
        # Each entry: (path, methods, handler_fn)
        self._api_routes: list[tuple[str, list[str], Callable]] = []

        # Store + activate the theme. This makes App(theme=...) do the right
        # thing for the entire process (script-style usage). Advanced users
        # who want completely isolated themes per client can inspect
        # self.theme later and implement their own middleware.
        self.theme = theme
        if theme is not None and theme != "default":
            try:
                set_theme(theme)
            except Exception:
                # Never break app construction because of a bad theme value
                self.theme = "default"

    def page(self, path: str = "/") -> Callable[[Callable], Callable]:
        """Decorator to register a page renderer.

        Multi-page is first-class and reliable:
            @app.page("/")
            def home(): ...

            @app.page("/dashboard")
            def dash(user=None): ...   # works with bare `page` too + auth + WS

        Navigation: use normal <a href="/dashboard"> or links; ClayForge serves the
        right page + re-hydrates live elements over WS using the path from ready msg.
        """

        def decorator(fn: Callable) -> Callable:
            self._pages[path] = fn
            return fn

        return decorator

    def api(
        self,
        path: str,
        methods: list[str] | None = None,
    ) -> Callable[[Callable], Callable]:
        """
        Decorator to expose a plain Python function as a real FastAPI JSON API route.

        This delivers the "easy to expose Python functions as API routes" part of the vision
        with zero boilerplate.

        Example:

            @app.api("/api/todos", methods=["GET", "POST"])
            def todos_api(payload: dict = None):
                # Fully normal Python — return JSON-serializable data
                if payload and payload.get("title"):
                    # ... use clayforge.db here, call auth, whatever
                    return {"ok": True, "created": payload}
                return {"todos": [...]}

        The route is automatically mounted when you run the ClayForge app.
        Works beautifully together with auth.require_login (see examples).
        """
        if methods is None:
            methods = ["GET"]

        def decorator(fn: Callable) -> Callable:
            self._api_routes.append((path, [m.upper() for m in methods], fn))
            return fn

        return decorator

    def get_api_routes(self) -> list[tuple[str, list[str], Callable]]:
        """Return registered API routes (used by the server layer)."""
        return list(self._api_routes)

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Convenience launcher that wires this App instance into the live server.

        The user's @app.page functions will now be rendered for real.
        """
        import os

        from .server import set_current_app

        # Make sure the server sees us (works for both direct import and reload)
        set_current_app(self)

        # Also set env var so that if uvicorn re-imports the server module under
        # the reloader the App is still discovered.
        os.environ.setdefault("CLAYFORGE_APP", "__main__:app")

        import uvicorn

        uvicorn.run("clayforge.core.server:app", host=host, port=port, reload=False)

    def __repr__(self) -> str:
        return f"<ClayForgeApp title={self.title!r} pages={len(self._pages)} apis={len(self._api_routes)}>"


# ------------------------------------------------------------------
# Module-level page + default App (now functional, not a stub)
# Supports:
#   from clayforge import page
#   @page("/")
#   def home(): ...
#
# The resulting pages are registered on `default_app`. The run / server
# layers will pick this up automatically when no explicit `app = cf.App()`
# instance is defined in the target module (see cli + server auto-mount).
# ------------------------------------------------------------------

default_app = App(title="ClayForge App")


def page(path: str = "/") -> Callable[[Callable], Callable]:
    """Module-level page decorator (registers on the framework default_app).

    Also works alongside explicit `app = cf.App(); @app.page`.

    Bare usage is fully supported:
        from clayforge import page
        @page("/about")
        def about(): cf.ui.title("About")
    The `clayforge run`, server auto-mount, and WS ready all discover default_app pages.
    """

    def decorator(fn: Callable) -> Callable:
        default_app._pages[path] = fn
        return fn

    return decorator
