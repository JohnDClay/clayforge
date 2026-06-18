"""
ClayForge ASGI Server

This is the heart of every running ClayForge app.
It mounts:
- FastAPI routes for initial page loads
- Native WebSocket endpoint for reactive updates (no extra socketio dep)
- Static assets (when present)
- The user-provided app pages (via registry)

Design goals (aggressive dep minimization):
- Only standard library + FastAPI/Starlette + uvicorn
- Simple but reliable per-client connection manager
- HTML rendered from Python element trees
- JSON protocol over WS for all runtime interaction
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Auth + DB integration (optional features but always import-safe)
from ..auth import auth as _default_auth
from ..auth import set_auth_context
from ..db import db as _default_db  # noqa: F401  (exposed for convenience / advanced users)

# For WS-ready user injection on multi-page + auth flows
try:
    from ..auth import get_auth_user_from_context
    from ..auth import set_auth_context as _set_auth_ctx
except Exception:  # pragma: no cover
    def get_auth_user_from_context():  # type: ignore
        return None

    def _set_auth_ctx(u=None):  # type: ignore
        pass

# Import here (lazy in functions too) to keep startup light
from .app import App
from .client import Client, ClientManager
from .theme import Theme, apply_theme_to_html, get_theme
from .ui import _reset_current_client, _set_current_client, render_page

logger = logging.getLogger("clayforge.server")

# Global singletons (simple for early versions — will be properly scoped in future if multi-app isolation needed)
app = FastAPI(
    title="ClayForge",
    lifespan=None,  # we use a simple startup for now
)
client_manager = ClientManager()

# The currently mounted user application (set by CLI, App.run(), or auto-detection)
_current_app: App | None = None


def set_current_app(user_app: App) -> None:
    """Explicitly mount a ClayForge App so that @app.page functions are served.

    Called by:
    - clayforge run --app path:to_app
    - app.run() inside user scripts
    - env var bootstrap below
    """
    global _current_app
    _current_app = user_app
    # Wire any API routes the user registered with @app.api(...)
    _wire_api_routes(user_app)


def _get_current_app() -> App | None:
    return _current_app


def _get_active_theme() -> Theme:
    """Resolve the theme that should be used for the current shell render.

    Priority:
    1. Theme stored on the mounted user App (most common path)
    2. Global theme set via cf.set_theme(...) or previous App
    3. Sensible dark default
    """
    user_app = _get_current_app()
    if user_app is not None:
        th = getattr(user_app, "theme", None)
        if th is not None:
            if isinstance(th, Theme):
                return th
            if isinstance(th, str):
                mode = "light" if th.lower() == "light" else "dark"
                return Theme(name=th, mode=mode)
            if isinstance(th, dict):
                return Theme(name="app-dict", css_vars=th)
    # Fall back to whatever the user set globally (or default)
    return get_theme()


def _auto_mount_user_app() -> None:
    """Best-effort auto detection so `clayforge run` (and reload) just works.

    Supports:
    - CLAYFORGE_APP=module:attr   (or CF_APP)
    - Presence of ./app.py in cwd (treated as "app:app")
    This runs at import time so that uvicorn --reload also picks it up.
    """
    global _current_app
    spec = os.environ.get("CLAYFORGE_APP") or os.environ.get("CF_APP")

    if not spec and Path("app.py").exists():
        spec = "app:app"

    if not spec:
        return

    try:
        if ":" in spec:
            mod_name, attr = spec.split(":", 1)
        else:
            mod_name, attr = spec, "app"

        import importlib

        mod = importlib.import_module(mod_name)
        candidate = getattr(mod, attr, None)
        if isinstance(candidate, App):
            _current_app = candidate
            logger.info("Auto-mounted ClayForge user App from %s", spec)
        else:
            # Support modules that only use the top-level `page` decorator (no `app = App()` var)
            try:
                from .app import App as _AppT
                from .app import default_app as _def
                if isinstance(_def, _AppT) and getattr(_def, "_pages", None):
                    _current_app = _def
                    logger.info("Auto-mounted default_app (bare @page usage) from %s", spec)
            except Exception:
                pass
    except Exception as exc:  # noqa: BLE001
        logger.debug("Auto-mount skipped for %s (%s)", spec, exc)


# Run auto-mount immediately on server import (covers CLI + uvicorn reload + direct run)
_auto_mount_user_app()


# Mount user static if present (examples, user apps)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass


# ---------------------------------------------------------------------------
# API Route Wiring (the "expose Python functions as API routes" feature)
# Called whenever a user App is mounted.
# ---------------------------------------------------------------------------


def _wire_api_routes(user_app: App) -> None:
    """Mount any @app.api(...) functions as real FastAPI routes on the global app."""
    if not user_app or not hasattr(user_app, "get_api_routes"):
        return

    try:
        routes = user_app.get_api_routes()
    except Exception:
        return

    for path, methods, handler in routes:
        # Support both sync and async handlers naturally (FastAPI handles it)
        app.add_api_route(
            path,
            handler,
            methods=methods,
            name=getattr(handler, "__name__", "api_route"),
        )
        logger.info("Registered API route: %s %s", methods, path)


# Wire routes for any app that was auto-mounted at import time
if _current_app:
    _wire_api_routes(_current_app)


# ---------------------------------------------------------------------------
# Core Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Serve the initial shell for the root page."""
    return await _serve_registered_page(request, "/")


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str) -> HTMLResponse:
    """Support multiple @app.page routes in a user App.

    Allows users to register many pages (e.g. /dashboard, /grok, /agents)
    and navigate between them with real URLs while keeping the beautiful
    shared shell + live WebSocket reactivity.
    """
    normalized = "/" + (full_path or "").strip("/")
    if normalized == "/":
        normalized = "/"
    return await _serve_registered_page(request, normalized)


async def _serve_registered_page(request: Request, path: str) -> HTMLResponse:
    """Core logic to render a registered page or fall back gracefully.

    Now with optional auth support:
    - Reads the session cookie (if present)
    - Sets auth context so @auth.require_login and auth.get_current_user() work inside pages
    """
    user_app = _get_current_app()
    page_title = user_app.title if user_app else "ClayForge"

    page_fn = None
    if user_app:
        # Try exact match, then common variants
        page_fn = (
            user_app._pages.get(path)
            or user_app._pages.get(path.rstrip("/"))
            or user_app._pages.get(path + "/")
        )

    # ------------------------------------------------------------------
    # Auth integration (cookie → contextvar for zero-boilerplate decorators)
    # ------------------------------------------------------------------
    current_user = None
    try:
        current_user = _default_auth.get_user_from_request(request)
        if current_user:
            set_auth_context(user=current_user)
    except Exception:
        # Never let auth problems break page serving
        current_user = None

    page_content_html = ""
    if page_fn:
        try:
            # We pass the user through kwargs so advanced pages can declare (user=...)
            # The require_login decorator will also pick it up via context.
            if current_user is not None:
                try:
                    page_content_html, _ = render_page(lambda: page_fn(user=current_user))
                except TypeError:
                    # Page function doesn't accept the kwarg — fall back to plain call
                    page_content_html, _ = render_page(page_fn)
            else:
                page_content_html, _ = render_page(page_fn)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Page render failed for %s", path)
            page_content_html = f'<div class="p-8 text-red-400">Render error: {exc}</div>'
    elif user_app and path not in ("/", "/app"):
        # Nice 404 for registered apps
        page_content_html = f'''
        <div class="max-w-md mx-auto mt-20 p-8 bg-zinc-900 border border-zinc-800 rounded-3xl text-center">
            <div class="text-6xl mb-4">🧭</div>
            <h1 class="text-2xl font-semibold tracking-tight mb-2">Page not found</h1>
            <p class="text-zinc-400 mb-6">No @app.page("{path}") is registered on this ClayForge app.</p>
            <a href="/" class="inline-flex items-center justify-center px-6 h-10 rounded-2xl bg-white text-zinc-950 font-medium text-sm">Go to home</a>
        </div>
        '''

    if user_app or page_content_html:
        html = _render_shell_with_content(page_content_html, title=page_title, current_path=path)
    else:
        html = _render_beautiful_shell()
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    """The reactive lifeline.

    Protocol (very small JSON surface for minimalism):
    Client -> Server:
        {"type": "event", "element_id": "...", "event": "click", "data": {...}}

    Server -> Client:
        {"type": "update", "element_id": "...", "html": "..."}   # targeted replace
        {"type": "replace", "element_id": "...", "html": "..."}
        {"type": "toast", "message": "...", "level": "success"}
        {"type": "run_js", "code": "..."}

    This design keeps the client.js tiny and the server authoritative.
    """
    await websocket.accept()

    client = await client_manager.connect(client_id, websocket)
    logger.info("Client connected: %s (total: %d)", client_id, client_manager.count())

    # Best-effort: attach authenticated user from cookie so that handlers
    # can do auth.get_current_user(client=client) with zero extra work.
    try:
        token = getattr(websocket, "cookies", {}).get(_default_auth.session_cookie)
        if token:
            user = _default_auth.parse_token(token)
            if user:
                client.session_state["user"] = user
    except Exception:
        pass  # Auth is always optional

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await client.send_error("Invalid JSON")
                continue

            await _handle_client_message(client, msg)

    except WebSocketDisconnect:
        await client_manager.disconnect(client_id)
        logger.info("Client disconnected: %s", client_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("WS error for %s: %s", client_id, exc)
        await client_manager.disconnect(client_id)


async def _handle_client_message(client: Client, msg: dict[str, Any]) -> None:
    """Route incoming events to the right element handler (or global actions)."""
    msg_type = msg.get("type")

    if msg_type == "ready":
        # Client finished loading and established WS. Time to activate the *real*
        # user page with correct element ids + registered handlers.
        # Use path from client (sent on ready) so sub-pages (/foo) don't get stomped by home.
        user_app = _get_current_app()
        if user_app:
            req_path = msg.get("path") or "/"
            normalized = "/" + (req_path or "").strip("/")
            if normalized == "//":
                normalized = "/"
            page_fn = (
                user_app._pages.get(normalized)
                or user_app._pages.get(normalized.rstrip("/"))
                or user_app._pages.get(normalized + "/")
                or user_app._pages.get("/")
                or user_app._pages.get("/app")
            )
            if page_fn:
                try:
                    # Support multi-page + auth protected pages on WS activation:
                    # mirror the http _serve logic + use client session_state["user"] if present.
                    user = client.session_state.get("user") if isinstance(getattr(client, "session_state", None), dict) else None
                    if user:
                        try:
                            _set_auth_ctx(user)
                            set_auth_context(user=user)
                        except Exception:
                            pass
                    # Render, with user= injection for pages that declare it (auth patterns)
                    if user is not None:
                        try:
                            page_html, all_elements = render_page(lambda: page_fn(user=user))
                        except TypeError:
                            page_html, all_elements = render_page(page_fn)
                    else:
                        page_html, all_elements = render_page(page_fn)
                    client.register_elements(all_elements)

                    # Replace the placeholder/snapshot root with the live-wired version.
                    # The JS replace handler will swap the whole container.
                    live_wrapper = (
                        f'<div id="cf-page-root" class="max-w-7xl mx-auto px-6 pt-10 pb-20">'
                        f"{page_html}</div>"
                    )
                    await client.send_replace("cf-page-root", live_wrapper)
                except Exception:  # noqa: BLE001
                    logger.exception("Ready-time page render failed")
                    await client.send_toast("Live UI activation error", level="error")
        # No-op for pure demo mode (old hardcoded buttons still work via inline onclick)

    elif msg_type == "event":
        element_id = msg.get("element_id")
        event_name = msg.get("event")
        data = msg.get("data", {})

        # --- Real element dispatch (the core of button roundtrips) ---
        elem = client.get_element(element_id) if hasattr(client, "get_element") else None
        if elem is not None:
            # Temporarily bind the client so advanced handlers can use elem._client if desired
            prev = getattr(elem, "_client", None)
            elem._client = client
            # Set contextvar so get_client() / get_session_state() work inside user handlers (first-class state)
            ctx_token = _set_current_client(client)
            try:
                # Auto-sync simple form values back onto the live element instance (helps .value reads in some patterns)
                if event_name == "change" and isinstance(data, dict):
                    if hasattr(elem, "value"):
                        elem.value = data.get("value", getattr(elem, "value", ""))
                    if hasattr(elem, "checked"):
                        elem.checked = bool(data.get("checked", False))
                elem.handle_event(event_name, data)
            finally:
                elem._client = prev
                _reset_current_client(ctx_token)

            # Always give positive feedback for the basic milestone
            await client.send_toast("Event handled by Python ✓", level="success")
            return

        # --- Fallback: foundation demo buttons (still fully supported) ---
        if element_id == "demo-button":
            await client.send_update(
                "demo-output",
                '<div id="demo-output" class="text-emerald-400 font-medium mt-3">'
                "Hello from the server! This update arrived via WebSocket with zero page reload."
                "</div>",
            )
            await client.send_toast("Beautiful reactive update ✓", level="success")

        elif element_id == "theme-toggle":
            # Simple demo: tell client to toggle dark class on <html>
            await client.send_run_js(
                "document.documentElement.classList.toggle('dark');"
                "localStorage.setItem('cf-theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');"
            )
    else:
        await client.send_error(f"Unknown message type: {msg_type}")


# ---------------------------------------------------------------------------
# Beautiful Self-Contained Shell + Real Page Injection
# The shell is always gorgeous. When a real user App is mounted, the
# #cf-page-root region receives the rendered element tree from render_page().
# ---------------------------------------------------------------------------


def _render_base_shell(
    title: str,
    main_content: str,
    current_path: str = "/",
    theme: Theme | None = None,
) -> str:
    """Shared production-quality HTML chrome (nav + styles + WS + JS).

    main_content is injected right after the nav. For user apps this is usually
    the wrapper around their cf.ui.* rendered tree.
    `current_path` is available for active navigation state if the shell chrome is used.

    Theming integration:
    - Respects the active Theme (from App or global set_theme)
    - Injects all --cf-* CSS variables into :root
    - Sets the correct initial dark/light class on <html>
    - Adds a few base rules so body/surfaces can use the vars
    """
    active = theme or _get_active_theme()

    # Compute html class + the <style> block containing our theme vars.
    # This is the heart of the new theming system for the shell.
    html_cls, theme_head = apply_theme_to_html("dark" if active.mode == "dark" else "")

    # Extra lightweight base styles so the chrome + any user classes using
    # var(--cf-*) look correct even before Tailwind fully applies.
    theme_base_css = """
        body {
            background-color: var(--cf-bg);
            color: var(--cf-text);
            font-family: var(--font-sans);
        }
        .cf-surface {
            background-color: var(--cf-surface);
            border-color: var(--cf-border);
        }
    """.strip()

    full_theme_styles = theme_head + "\n<style>\n" + theme_base_css + "\n</style>"

    return f"""<!DOCTYPE html>
<html lang="en" class="{html_cls}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    {full_theme_styles}
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Space+Grotesk:wght@500;600&amp;display=swap');
        
        :root {{
            --font-sans: 'Inter', system_ui, sans-serif;
        }}
        
        /* Note: body font-family + colors now also driven by theme vars above */
        
        .font-display {{
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-weight: 600;
            letter-spacing: -0.025em;
        }}

        .clay-card {{
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), 
                       box-shadow 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        .clay-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }}

        .section-header {{
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 600;
            color: rgb(163 163 172);
        }}

        .status-dot {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}

        .demo-button {{
            transition: all 0.1s ease;
        }}
        .demo-button:active {{
            transform: scale(0.985);
        }}
    </style>
</head>
<body class="bg-zinc-950 text-zinc-200">
    <!-- Top Navigation -->
    <nav class="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6">
            <div class="flex h-16 items-center justify-between">
                <div class="flex items-center gap-x-3">
                    <div class="flex items-center gap-x-2.5">
                        <div class="w-9 h-9 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-inner">
                            <i class="fa-solid fa-layer-group text-white text-2xl"></i>
                        </div>
                        <div>
                            <span class="font-display text-2xl tracking-tighter font-semibold">clayforge</span>
                            <span class="text-[10px] font-mono text-zinc-500 ml-1 align-super">v0.2</span>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-x-2">
                    <div class="hidden md:flex items-center gap-x-1.5 text-sm px-3 py-1.5 rounded-2xl bg-zinc-900 border border-zinc-800">
                        <div class="w-2 h-2 bg-emerald-400 rounded-full status-dot"></div>
                        <span class="text-zinc-400 text-xs font-medium">CONNECTED</span>
                    </div>
                    
                    <button onclick="toggleTheme()"
                            id="theme-toggle"
                            class="inline-flex items-center justify-center w-9 h-9 rounded-2xl hover:bg-zinc-900 border border-zinc-800 transition-colors"
                            title="Toggle theme">
                        <i class="fa-solid fa-moon text-zinc-400"></i>
                    </button>
                    
                    <a href="https://github.com/JohnDClay/clayforge" target="_blank"
                       class="inline-flex items-center gap-x-2 text-sm px-4 h-9 rounded-2xl border border-zinc-800 hover:bg-zinc-900 transition-colors">
                        <i class="fa-brands fa-github"></i>
                        <span class="hidden sm:inline text-xs font-medium">GitHub</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Dynamic page content injected here by ClayForge runtime -->
    <div id="cf-page-root">
{main_content}
    </div>

    <!-- No hardcoded footer in shell (avoids duplication with user cf.ui.footer or custom content).
         Users control page-end content inside their @app.page. Nav provides light brand chrome. -->

    <script>
        function initTailwind() {{
            document.documentElement.classList.add('dark');
            const saved = localStorage.getItem('cf-theme');
            if (saved === 'light') document.documentElement.classList.remove('dark');
        }}
        
        function toggleTheme() {{
            const html = document.documentElement;
            html.classList.toggle('dark');
            const isDark = html.classList.contains('dark');
            localStorage.setItem('cf-theme', isDark ? 'dark' : 'light');
            if (window.__cfSocket && window.__cfSocket.readyState === 1) {{
                window.__cfSocket.send(JSON.stringify({{
                    type: "event",
                    element_id: "theme-toggle",
                    event: "click",
                    data: {{ dark: isDark }}
                }}));
            }}
        }}

        let socket;
        let clientId = 'client_' + Date.now() + '_' + Math.random().toString(36).slice(2, 9);

        function connectWebSocket() {{
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${{protocol}}//${{location.host}}/ws/${{clientId}}`;
            
            socket = new WebSocket(wsUrl);
            window.__cfSocket = socket;

            socket.onopen = () => {{
                console.log('%c[ClayForge] WebSocket connected', 'color:#64748b');
                // Tell server we are ready for the *live* element tree + handlers.
                // Include path so server activates the correct @app.page (not always /).
                socket.send(JSON.stringify({{ type: "ready", path: location.pathname }}));
            }};

            socket.onmessage = (event) => {{
                try {{
                    const msg = JSON.parse(event.data);
                    handleServerMessage(msg);
                }} catch (e) {{
                    console.warn('Bad WS message', event.data);
                }}
            }};

            socket.onclose = () => {{
                console.log('%c[ClayForge] WebSocket closed — reconnecting...', 'color:#64748b');
                setTimeout(connectWebSocket, 1400);
            }};
        }}

        function handleServerMessage(msg) {{
            if (msg.type === 'update' || msg.type === 'replace') {{
                const el = document.getElementById(msg.element_id);
                if (el && msg.html) {{
                    el.outerHTML = msg.html;
                }}
            }} else if (msg.type === 'toast') {{
                showToast(msg.message, msg.level || 'info');
            }} else if (msg.type === 'run_js') {{
                try {{ eval(msg.code); }} catch (e) {{ console.error(e); }}
            }} else if (msg.type === 'error') {{
                console.error('[ClayForge Server]', msg.message);
            }}
        }}

        // Event delegation for ALL real ClayForge elements (buttons, inputs, etc.)
        // Works for initial HTML snapshot + any later replace() payloads.
        function wireLiveEventHandlers() {{
            // Click events (primary for Button)
            document.addEventListener('click', (e) => {{
                const target = e.target.closest('[data-event="click"], [data-cf-role="button"]');
                if (target && socket && socket.readyState === 1) {{
                    const element_id = target.id || (target.closest('[id]') ? target.closest('[id]').id : null);
                    if (element_id) {{
                        socket.send(JSON.stringify({{
                            type: "event",
                            element_id: element_id,
                            event: "click",
                            data: {{}}
                        }}));
                    }}
                }}
            }});

            // Change / input for TextInput, Select, Checkbox, TextArea, File etc.
            // Resolves the registered Element id even for composite controls
            // (e.g. <div id=EL> <select data-event> or <label id=EL><input data-event>)
            // by falling back to nearest ancestor id when the emitting tag itself has none.
            document.addEventListener('change', (e) => {{
                const control = e.target.closest('input[data-event], textarea[data-event], select[data-event]');
                if (control && socket && socket.readyState === 1) {{
                    const element_id = control.id || (control.closest('[id]') ? control.closest('[id]').id : null);
                    if (element_id) {{
                        const data = {{ value: control.value }};
                        if (control.type === 'checkbox') {{
                            data.checked = !!control.checked;
                        }}
                        socket.send(JSON.stringify({{
                            type: "event",
                            element_id: element_id,
                            event: "change",
                            data: data
                        }}));
                    }}
                }}
            }});
        }}

        function triggerDemoAction() {{
            if (!socket || socket.readyState !== 1) {{
                alert("WebSocket not connected yet — refresh the page.");
                return;
            }}
            socket.send(JSON.stringify({{
                type: "event",
                element_id: "demo-button",
                event: "click",
                data: {{}}
            }}));
        }}

        function showToast(message, level = 'info') {{
            const colors = {{
                success: 'bg-emerald-600',
                error: 'bg-red-600',
                info: 'bg-zinc-700'
            }};
            const toast = document.createElement('div');
            toast.className = `fixed bottom-6 right-6 ${{colors[level] || colors.info}} text-white px-5 py-3 rounded-2xl shadow-xl text-sm flex items-center gap-x-3 z-[999]`;
            toast.innerHTML = `<div>${{message}}</div><button class="opacity-70 hover:opacity-100">×</button>`;
            document.body.appendChild(toast);
            toast.querySelector('button').onclick = () => toast.remove();
            setTimeout(() => toast.parentNode && toast.parentNode.removeChild(toast), 4200);
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            initTailwind();
            wireLiveEventHandlers();
            connectWebSocket();

            document.addEventListener('keydown', (e) => {{
                if (e.key === '?') showToast("ClayForge — real Python UI with live WS events.", "info");
            }});
        }});

        window.ClayForge = {{ triggerDemoAction, connectWebSocket }};
    </script>
</body>
</html>"""


def _render_shell_with_content(
    page_html: str, title: str = "ClayForge App", current_path: str = "/"
) -> str:
    """Render the live user page inside the beautiful ClayForge chrome.

    `current_path` is passed for future active nav highlighting in the shared shell
    (the showcase app currently uses its own custom chrome).
    """
    # The page_html (from render_page) is placed inside the always-present #cf-page-root
    wrapped = f'<div class="max-w-7xl mx-auto px-6 pt-10 pb-20">{page_html}</div>'
    active_theme = _get_active_theme()
    return _render_base_shell(title, wrapped, current_path=current_path, theme=active_theme)


def _render_beautiful_shell() -> str:
    """Original foundation demo (used when no user App is mounted)."""
    demo = """
        <!-- Hero -->
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-20">
            <div class="max-w-3xl">
                <div class="inline-flex items-center gap-x-2 px-4 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 text-xs font-medium tracking-[0.125em] mb-6">
                    <span class="text-emerald-400">●</span> 
                    FOUNDATION MILESTONE
                </div>
                
                <h1 class="font-display text-6xl tracking-tighter font-semibold leading-[1.05] text-white">
                    Beautiful apps.<br>
                    Pure Python.<br>
                    <span class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Zero friction.</span>
                </h1>
                
                <p class="mt-5 text-xl text-zinc-400 max-w-md">
                    This entire interface is powered by a tiny Python WebSocket server.
                    No full page reloads. No JavaScript framework. Just magic.
                </p>

                <div class="flex items-center gap-x-3 mt-8">
                    <button onclick="triggerDemoAction()"
                            id="demo-button"
                            class="demo-button inline-flex items-center justify-center gap-x-2 bg-white text-zinc-950 font-semibold px-6 h-11 rounded-2xl text-sm active:scale-[0.985] shadow-sm hover:bg-zinc-100 transition-all">
                        <i class="fa-solid fa-bolt-lightning"></i>
                        <span>Trigger Reactive Update</span>
                    </button>
                    
                    <button onclick="document.getElementById('theme-toggle').click()"
                            class="inline-flex items-center justify-center gap-x-2 border border-zinc-700 hover:bg-zinc-900 font-medium px-5 h-11 rounded-2xl text-sm transition-colors">
                        <i class="fa-solid fa-palette"></i>
                        <span>Toggle Theme</span>
                    </button>
                </div>
            </div>

            <!-- Live Demo Card -->
            <div class="mt-12 grid grid-cols-1 lg:grid-cols-5 gap-6">
                <div class="lg:col-span-3">
                    <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
                        <div class="flex items-center gap-x-3 mb-5">
                            <div class="w-8 h-8 rounded-2xl bg-indigo-600/10 flex items-center justify-center">
                                <i class="fa-solid fa-play text-indigo-400"></i>
                            </div>
                            <div>
                                <div class="font-semibold text-lg tracking-tight">Live Reactive Demo</div>
                                <div class="text-xs text-zinc-500">Click the button above — watch the server push DOM updates</div>
                            </div>
                        </div>

                        <div id="demo-output" class="min-h-[92px] flex items-center justify-center border border-dashed border-zinc-800 rounded-2xl text-sm text-zinc-500 bg-zinc-950/50">
                            Server updates will appear here in real time via WebSocket.
                        </div>

                        <div class="mt-6 pt-6 border-t border-zinc-800 flex items-center gap-x-4 text-xs">
                            <div class="flex items-center gap-x-1.5 text-emerald-400">
                                <i class="fa-solid fa-check"></i>
                                <span class="font-medium">Zero page reload</span>
                            </div>
                            <div class="flex items-center gap-x-1.5 text-zinc-400">
                                <i class="fa-solid fa-broadcast-tower"></i>
                                <span>Targeted WebSocket patch</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-2">
                    <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 h-full flex flex-col">
                        <div class="section-header mb-3">What this proves</div>
                        
                        <div class="space-y-3 text-sm flex-1">
                            <div class="flex gap-3">
                                <i class="fa-solid fa-check text-emerald-400 mt-1"></i>
                                <div class="text-zinc-300">Pure Python element tree rendered on the server</div>
                            </div>
                            <div class="flex gap-3">
                                <i class="fa-solid fa-check text-emerald-400 mt-1"></i>
                                <div class="text-zinc-300">Native WebSockets (no extra socketio dependency)</div>
                            </div>
                            <div class="flex gap-3">
                                <i class="fa-solid fa-check text-emerald-400 mt-1"></i>
                                <div class="text-zinc-300">Tailwind via CDN + shadcn/ui aesthetic</div>
                            </div>
                            <div class="flex gap-3">
                                <i class="fa-solid fa-check text-emerald-400 mt-1"></i>
                                <div class="text-zinc-300">Real context-managed layouts + event roundtrips</div>
                            </div>
                        </div>
                        
                        <div class="text-[10px] text-zinc-500 mt-auto pt-4">
                            Next: GrokChat, charts, full reactivity
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tech strip -->
            <div class="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-xs text-zinc-400">
                <div class="flex items-center gap-x-2"><i class="fa-brands fa-python"></i> <span>100% Python API</span></div>
                <div class="flex items-center gap-x-2"><i class="fa-solid fa-bolt"></i> <span>FastAPI + Native WS</span></div>
                <div class="flex items-center gap-x-2"><i class="fa-solid fa-palette"></i> <span>Tailwind + modern defaults</span></div>
                <div class="flex items-center gap-x-2"><i class="fa-solid fa-robot"></i> <span>Built for Grok &amp; agents</span></div>
            </div>
        </div>
    """
    active_theme = _get_active_theme()
    return _render_base_shell("ClayForge • Foundation", demo, theme=active_theme)
