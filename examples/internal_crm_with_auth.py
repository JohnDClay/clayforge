"""
ClayForge Example 09 — Internal CRM with One-Click Auth + Database

A realistic, production-style internal tool that demonstrates the full
"one-click authentication + database connectors" vision:

- Cookie-based secure sessions via clayforge.auth (signed cookies)
- SQLite via clayforge.db (always available, zero deps) + easy schema
- Password hashing (secure with [auth] extra, solid fallback otherwise)
- Protected pages that feel natural (`auth.get_current_user()` just works)
- Beautiful login experience using real HTML <form> + ClayForge UI
- Live DB-backed customer list + notes (add / view activity)
- Logout that clears the session cookie cleanly
- Optional Postgres path shown in comments (swap the URL — everything else identical)

This is exactly the kind of internal RevOps / support / admin tool teams
build every week. With ClayForge + the new auth + db helpers it takes
minutes instead of days, with gorgeous defaults and zero boilerplate.

Run (recommended):
    python examples/internal_crm_with_auth.py

Or via the CLI (great for iteration):
    clayforge run --app examples.internal_crm_with_auth:app

Install the optional extras for the best experience:
    pip install "clayforge[auth,db]"

    # For real Postgres in production instead of SQLite:
    # pip install asyncpg
    # Then use: database = Database("postgresql+asyncpg://...")

The example seeds an admin user on first run:
    username: admin
    password: demo123   (change in real use!)

Cross-integration: These auth+db patterns drop directly into viz dashboards (05/06/08) or agent workbenches (07). GrokChat/AgentCanvas work inside @require_login pages. `clayforge showcase` uses dedicated tabs (GrokChat only in "GrokChat" tab, AgentCanvas only in "Agent Vision" tab — nice titles + prose first, full interactive, zero leakage). See `clayforge gallery` Command Center + playground for live auth+db + viz/grok cross-mutation demos.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import clayforge as cf

# ------------------------------------------------------------------
# The two heroes of this example
# ------------------------------------------------------------------
from clayforge import Auth, Database
from clayforge.core.server import app as fastapi_app  # for custom login route

# ------------------------------------------------------------------
# Configuration — override via environment in real deployments
# ------------------------------------------------------------------
SECRET = os.getenv("CLAYFORGE_AUTH_SECRET", "change-this-to-a-long-random-string-in-prod")
DATABASE_URL = os.getenv("CLAYFORGE_DB_URL", "sqlite:///./clayforge_crm.db")

# Singletons (the zero-boilerplate experience)
auth_manager = Auth(secret_key=SECRET, cookie_name="cf_crm_session", max_age=86400 * 30)
database = Database(DATABASE_URL)

app = cf.App(
    title="ClayForge • Internal CRM",
    description="Secure customer operations workbench with auth + real database",
    theme="dark",
)

# ------------------------------------------------------------------
# Database schema (runs safely on startup / first use)
# ------------------------------------------------------------------
CRM_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'agent',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    email TEXT,
    status TEXT DEFAULT 'Active',
    value INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    author TEXT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);
"""


def _ensure_schema_and_seed():
    """Idempotent setup. Safe to call on every start."""
    try:
        database.init_sqlite_schema(CRM_SCHEMA)
    except Exception as e:
        # In case of very first run edge cases
        print(f"[CRM] Schema init note: {e}")

    # Seed a default admin user if none exists
    user = database.fetchone("SELECT * FROM users WHERE username = ?", ("admin",))
    if not user:
        pw_hash = Auth.hash_password("demo123")
        database.execute(
            "INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
            ("admin", pw_hash, "Alex Rivera", "admin"),
        )
        print("[CRM] Seeded default admin user (admin / demo123)")

    # Seed a few realistic customers
    count = database.fetchval("SELECT COUNT(*) FROM customers") or 0
    if count == 0:
        customers = [
            ("Acme Corp", "Acme", "ops@acme.io", "Active", 125000),
            ("Vertex Labs", "Vertex", "founders@vertex.ai", "Active", 89000),
            ("Helix Dynamics", "Helix", "support@helix.co", "Churn Risk", 42000),
            ("Pinnacle AI", "Pinnacle", "team@pinnacle.ai", "Active", 210000),
        ]
        for name, company, email, status, value in customers:
            database.execute(
                "INSERT INTO customers (name, company, email, status, value) VALUES (?, ?, ?, ?, ?)",
                (name, company, email, status, value),
            )
        print("[CRM] Seeded sample customers")


_ensure_schema_and_seed()


# ------------------------------------------------------------------
# Helper: current user (works inside pages + handlers thanks to server context)
# ------------------------------------------------------------------
def get_current_user() -> dict[str, Any] | None:
    """Convenience wrapper. Works magically inside @app.page functions."""
    return auth_manager.get_current_user()


# ------------------------------------------------------------------
# Login route — real HTML form POST + secure cookie setting
# This is the recommended pattern for authentication flows.
# ------------------------------------------------------------------
@fastapi_app.post("/auth/login", response_class=HTMLResponse)
async def login_handler(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handles the login form submission."""
    user_row = database.fetchone(
        "SELECT id, username, password_hash, name, role FROM users WHERE username = ?",
        (username.strip(),),
    )

    if user_row and Auth.verify_password(password, user_row["password_hash"]):
        # Create clean user payload for the session cookie (never store hash!)
        safe_user = {
            "id": user_row["id"],
            "username": user_row["username"],
            "name": user_row.get("name") or user_row["username"],
            "role": user_row.get("role", "agent"),
            "logged_in_at": datetime.utcnow().isoformat(),
        }

        # Redirect + attach the signed session cookie
        resp = RedirectResponse(url="/dashboard", status_code=303)
        auth_manager.login_user(resp, safe_user, remember=True)
        return resp

    # Failed login — return a clean standalone error page (the shell chrome is still gorgeous)
    error_content = """
    <div class="max-w-md mx-auto mt-16">
        <div class="clay-card bg-zinc-900 border border-red-900/60 rounded-3xl p-8">
            <div class="text-red-400 font-semibold mb-2">Login failed</div>
            <p class="text-zinc-400 text-sm">Invalid username or password. Try <span class="font-mono">admin / demo123</span>.</p>
            <a href="/login" class="mt-6 inline-block text-sm text-white hover:underline">Back to login →</a>
        </div>
    </div>
    """
    # Use the public render path by creating a tiny page and letting the normal shell wrap it
    # (simplest reliable approach without reaching into private symbols)
    return HTMLResponse(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Login Failed</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>body{{background:#18181b;color:#e4e4e7}}</style>
        </head><body class="p-8">{error_content}</body></html>"""
    )


@fastapi_app.post("/auth/logout", response_class=HTMLResponse)
async def logout_handler():
    resp = RedirectResponse(url="/login", status_code=303)
    auth_manager.logout_user(resp)
    return resp


# ------------------------------------------------------------------
# Public pages
# ------------------------------------------------------------------


@app.page("/login")
def login_page():
    """Beautiful login experience."""
    user = get_current_user()
    if user:
        # Already logged in — send them to the app
        cf.ui.text("You are already logged in. Redirecting…")
        # A tiny bit of client-side help (real apps can use better nav)
        return

    cf.ui.title("Sign in to Internal CRM")
    cf.ui.subtitle("Secure operations workbench • Powered by ClayForge")

    with cf.ui.card(title="Welcome back", subtitle="Use the seeded admin account for the demo"):
        # Real HTML form — posts to our FastAPI route above
        # This is pure HTML inside the rendered page (zero magic needed)
        form_html = """
        <form method="post" action="/auth/login" class="space-y-4 mt-2">
            <div>
                <label class="block text-xs uppercase tracking-widest text-zinc-500 mb-1.5">Username</label>
                <input name="username" type="text" value="admin"
                       class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl px-4 py-3 text-sm focus:border-indigo-500 outline-none">
            </div>
            <div>
                <label class="block text-xs uppercase tracking-widest text-zinc-500 mb-1.5">Password</label>
                <input name="password" type="password" value="demo123"
                       class="w-full bg-zinc-950 border border-zinc-800 rounded-2xl px-4 py-3 text-sm focus:border-indigo-500 outline-none">
            </div>

            <button type="submit"
                    class="mt-2 w-full inline-flex items-center justify-center gap-2 bg-white text-zinc-950 font-semibold h-11 rounded-2xl active:scale-[0.985] transition">
                <i class="fa-solid fa-right-to-bracket"></i>
                <span>Sign in securely</span>
            </button>
        </form>

        <div class="mt-6 pt-6 border-t border-zinc-800 text-[12px] text-zinc-500">
            Demo credentials: <span class="font-mono text-emerald-400">admin / demo123</span><br>
            In production use a strong <span class="font-mono">CLAYFORGE_AUTH_SECRET</span> env var.
        </div>
        """
        # Inject the form as raw HTML (safe here because we control it)
        # For pure cf.ui.* version you could use TextInput + on_click that calls a helper route,
        # but the native form + cookie pattern is the most robust and "just works".
        from clayforge.core.element import Element

        class RawForm(Element):
            def __init__(self, html: str):
                self.html = html
                super().__init__()

            def to_html(self) -> str:
                return self.html

        RawForm(form_html)  # auto-attaches via Element magic


@app.page("/dashboard")
def dashboard():
    """Main protected internal CRM workspace."""
    user = get_current_user()
    if not user:
        # Friendly gate instead of hard redirect (works great with the shell)
        cf.ui.title("Authentication required")
        cf.ui.subtitle("Please sign in to access the CRM.")

        with cf.ui.card():
            cf.ui.text("You are not logged in or your session expired.")
            cf.ui.button("Go to login", on_click=lambda: None)  # visual only — user can click nav
            # Real apps can use cf.ui.text with a link or JS
        return

    # --- Authenticated CRM surface ---
    cf.ui.title(f"Welcome back, {user.get('name', user['username'])}")
    cf.ui.subtitle("Internal customer operations • Live database-backed")

    # Header bar with user + logout
    with cf.ui.row(gap="3", classes="mb-6"):
        cf.ui.badge(f"Logged in as {user['username']}", variant="info")
        if user.get("role") == "admin":
            cf.ui.badge("ADMIN", variant="warning")

        # Logout via real POST route (clean cookie clearing)
        logout_form = """
        <form method="post" action="/auth/logout" style="display:inline">
            <button type="submit"
                    class="inline-flex items-center gap-2 text-sm px-4 h-9 rounded-2xl border border-zinc-700 hover:bg-zinc-900">
                <i class="fa-solid fa-sign-out-alt"></i>
                <span>Sign out</span>
            </button>
        </form>
        """
        # Inject small raw HTML for the form button (beautiful and functional)
        from clayforge.core.element import Element

        class RawLogout(Element):
            def to_html(self):
                return logout_form

        RawLogout()

    # Live stats from DB
    total_customers = database.fetchval("SELECT COUNT(*) FROM customers") or 0
    total_value = database.fetchval("SELECT COALESCE(SUM(value), 0) FROM customers") or 0
    recent_notes = database.fetchval("SELECT COUNT(*) FROM notes") or 0

    with cf.ui.row(gap="4"):
        with cf.ui.card(title="Customers"):
            cf.ui.text(f"{total_customers}", classes="text-4xl font-semibold")
        with cf.ui.card(title="Pipeline value"):
            cf.ui.text(f"${total_value:,}", classes="text-4xl font-semibold text-emerald-400")
        with cf.ui.card(title="Notes logged"):
            cf.ui.text(f"{recent_notes}", classes="text-4xl font-semibold")

    # Customer list + simple interaction
    customers: list[dict[str, Any]] = database.query(
        "SELECT * FROM customers ORDER BY value DESC LIMIT 12"
    )

    with cf.ui.card(title="Active accounts", subtitle="Click a row to view activity (demo)"):
        if not customers:
            cf.ui.text("No customers yet.")
        else:
            for c in customers:
                with cf.ui.row(gap="4", classes="py-3 border-b border-zinc-800 last:border-b-0"):
                    cf.ui.text(f"<strong>{c['name']}</strong>", tag="div")
                    cf.ui.badge(
                        c.get("status", "Active"),
                        variant="success" if c.get("status") == "Active" else "warning",
                    )
                    cf.ui.text(
                        f"${c.get('value', 0):,}", classes="ml-auto font-mono text-sm text-zinc-400"
                    )

                    # Demo action: add a quick note (writes to DB + gives feedback)
                    def add_quick_note(customer_id=c["id"], customer_name=c["name"]):
                        current = get_current_user() or {"username": "unknown"}
                        note = (
                            f"Quick note added from dashboard at {datetime.now().strftime('%H:%M')}"
                        )
                        database.execute(
                            "INSERT INTO notes (customer_id, author, content) VALUES (?, ?, ?)",
                            (customer_id, current["username"], note),
                        )
                        # Beautiful feedback (toasts are wired in the shell)
                        # In a fuller app we would do targeted WS update of the detail area
                        print(f"[CRM] Note added for customer {customer_name}")

                    cf.ui.button(
                        "Add note",
                        variant="secondary",
                        size="sm",
                        on_click=add_quick_note,
                    )

    # Recent activity feed (real DB data)
    notes = database.query(
        """
        SELECT n.*, c.name as customer_name
        FROM notes n
        LEFT JOIN customers c ON n.customer_id = c.id
        ORDER BY n.created_at DESC
        LIMIT 8
        """
    )

    with cf.ui.card(title="Recent activity", subtitle="Live from the database"):
        if not notes:
            cf.ui.text(
                "No notes yet. Use the buttons above to create some.", classes="text-zinc-400"
            )
        else:
            for note in notes:
                ts = note.get("created_at", "")[:16]
                cf.ui.text(
                    f"<span class='text-zinc-400 font-mono text-xs'>{ts}</span> "
                    f"• <strong>{note.get('author', 'system')}</strong> on "
                    f"<span class='text-indigo-400'>{note.get('customer_name', 'customer')}</span>: "
                    f"{note.get('content', '')}",
                    tag="div",
                    classes="text-sm py-1 border-b border-zinc-800 last:border-0",
                )

    cf.ui.footer("Example 09 • Auth + Database working together • ClayForge")


@app.page("/")
def home():
    """Landing / marketing page for the demo tool."""
    user = get_current_user()
    cf.ui.title("ClayForge Internal CRM")
    cf.ui.subtitle("A complete, secure, database-backed internal tool in pure Python")

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="What this example proves"):
            cf.ui.text("• Optional one-click auth with signed cookies")
            cf.ui.text("• Real SQLite (or Postgres) with zero boilerplate")
            cf.ui.text("• Beautiful login forms that just work (native + custom routes)")
            cf.ui.text("• Protected pages + live DB reads/writes from page functions & handlers")
            cf.ui.text("• Production-ready password hashing (bcrypt when available)")

        with cf.ui.card(title="Try it now"):
            if user:
                cf.ui.success(f"You are logged in as {user['username']}.")
                cf.ui.text("Head over to the dashboard to explore the live data.")
            else:
                cf.ui.text("Click the link below or visit /login.")
            cf.ui.button("Open the CRM dashboard", variant="primary", on_click=lambda: None)

    cf.ui.footer("Run with: python examples/internal_crm_with_auth.py")


# ------------------------------------------------------------------
# Make the app discoverable
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure schema exists even for direct run
    _ensure_schema_and_seed()
    print("\nClayForge CRM demo ready.")
    print("Default login: admin / demo123\n")
    app.run(host="127.0.0.1", port=8000)
