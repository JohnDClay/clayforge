"""
ClayForge Example 08 — Internal Operations Console (Realistic Admin Tool)

A complete, production-quality internal tooling surface that demonstrates
how ClayForge excels at building beautiful, highly interactive admin and
operations applications with almost zero boilerplate.

What this shows:
- Master DataTable (tickets/customers) with full client-side search, sort,
  and selection — the centerpiece of most internal tools.
- Live detail panel that reacts to row selection: rich read-only + editable
  fields (text inputs), status transitions, and action buttons.
- Multiple form-style controls: filters, bulk actions, "add note", priority
  escalations. All wired with real server handlers.
- Optional live PlotlyChart showing operational health metrics that update
  when you resolve/escalate tickets.
- Activity / audit trail as a second live DataTable.
- Professional UX patterns: optimistic updates, status badges, confirmation
  flows via cards, "last action" banners, keyboard-friendly flows.
- Graceful behavior with or without the [viz] extra.

This is the exact kind of tool an internal platform, support, or RevOps team
would use every day.

Run:
    python examples/08_ops_console.py

Or via CLI (best for iteration):
    clayforge run --app examples.08_ops_console:app

Optional (for the health chart + richer tables):
    pip install "clayforge[viz]"

Discoverability & cross-integration:
- Pairs perfectly with auth+db (see examples/auth_db_todo.py and internal_crm_with_auth.py) for real persisted tickets/customers instead of in-memory STATE (use @require_login on pages + Database for production internal tools).
- Add optional GrokChat "AI Ops Copilot" exactly as in examples/06_production_viz_dashboard.py.
- `clayforge showcase` has viz in Dashboard tab; `clayforge gallery` Command Center has live DataTable/Plotly + cross-mutation demos.
"""

from __future__ import annotations

import datetime
import random
from typing import Any

import clayforge as cf

# ------------------------------------------------------------------
# Optional viz (DataTable + PlotlyChart for health metrics)
# ------------------------------------------------------------------
try:
    from clayforge.components.viz import DataTable, PlotlyChart

    HAS_VIZ = True
except Exception:
    HAS_VIZ = False
    DataTable = PlotlyChart = None  # type: ignore


app = cf.App(
    title="ClayForge • Ops Console",
    description="Internal customer operations & support workbench",
    theme="dark",
)


# ------------------------------------------------------------------
# Realistic in-memory "database"
# ------------------------------------------------------------------
def _seed_tickets() -> list[dict[str, Any]]:
    companies = [
        "Acme Corp",
        "Vertex",
        "Helix Labs",
        "Pinnacle AI",
        "Forge",
        "Nimbus",
        "QuantumBase",
        "Aether",
    ]
    owners = ["sarah@acme.io", "mike@ops.co", "jane@revops.ai", "you@company.com"]
    priorities = ["P0", "P1", "P2", "P3"]
    statuses = ["Open", "In Progress", "Waiting on Customer", "Resolved"]

    tickets = []
    for i in range(19):
        age = random.randint(0, 14)
        created = (datetime.datetime.now() - datetime.timedelta(days=age)).strftime("%Y-%m-%d")
        tickets.append(
            {
                "id": f"TCK-{9000 + i}",
                "company": random.choice(companies),
                "subject": random.choice(
                    [
                        "SSO login failures after domain migration",
                        "Webhook delivery delays > 4h",
                        "Billing tier upgrade not reflected",
                        "Export CSV missing custom fields",
                        "Rate limit errors on /v2/search",
                        "Feature request: bulk user invites",
                    ]
                ),
                "priority": random.choice(priorities),
                "status": random.choice(statuses),
                "owner": random.choice(owners),
                "created": created,
                "value": random.randint(4200, 185000),
                "notes": "",
            }
        )
    return tickets


STATE: dict[str, Any] = {
    "tickets": _seed_tickets(),
    "selected_id": None,
    "last_action": "Console initialized with live data",
    "audit": [],
}


def _get_tickets_df():
    if not HAS_VIZ:
        return STATE["tickets"]
    try:
        import pandas as pd

        return pd.DataFrame(STATE["tickets"])
    except Exception:
        return STATE["tickets"]


def _log_audit(action: str, ticket_id: str | None = None):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = {"ts": ts, "action": action, "ticket": ticket_id or "-"}
    STATE["audit"].append(entry)
    if len(STATE["audit"]) > 25:
        STATE["audit"] = STATE["audit"][-25:]
    STATE["last_action"] = action


# ------------------------------------------------------------------
# Live component refs
# ------------------------------------------------------------------
_live: dict[str, Any] = {}  # table, health_chart, audit_table, etc.


def _refresh_table():
    if "table" in _live and _live["table"]:
        try:
            _live["table"].update_data(_get_tickets_df())
        except Exception:
            pass


def _refresh_health_chart():
    if "health" in _live and _live["health"] and HAS_VIZ:
        try:
            _live["health"].update_figure(_make_health_figure())
        except Exception:
            pass


def _refresh_audit():
    if "audit_table" in _live and _live["audit_table"] and HAS_VIZ:
        try:
            _live["audit_table"].update_data(STATE["audit"])
        except Exception:
            pass


def _make_health_figure():
    """Small operational health sparkline / bar for the console header."""
    if not HAS_VIZ:
        return {
            "data": [{"type": "bar", "y": [12, 8, 3, 1]}],
            "layout": {"title": "Health (viz extra needed)"},
        }

    try:
        import plotly.graph_objects as go

        open_t = len([t for t in STATE["tickets"] if t["status"] != "Resolved"])
        p0 = len([t for t in STATE["tickets"] if t["priority"] == "P0"])
        resolved_today = random.randint(1, 5)  # simulated

        fig = go.Figure(
            [
                go.Bar(
                    x=["Open", "P0 Critical", "Resolved (sim)"],
                    y=[open_t, p0, resolved_today],
                    marker_color=["#f59e0b", "#ef4444", "#10b981"],
                ),
            ]
        )
        fig.update_layout(
            height=128,
            margin=dict(t=10, r=10, b=20, l=30),
            paper_bgcolor="#18181b",
            plot_bgcolor="#18181b",
            font=dict(color="#a1a1aa", size=11),
            showlegend=False,
        )
        return fig
    except Exception:
        return {"data": [{"type": "bar", "y": [open_t, p0]}], "layout": {}}


# ------------------------------------------------------------------
# Core actions — realistic operations workflows
# ------------------------------------------------------------------
def _apply_filters(status_filter: str = "", priority_filter: str = "", search: str = ""):
    """Server-side filter that updates the live table (client-side search still works on top)."""
    filtered = STATE["tickets"]
    if status_filter:
        filtered = [t for t in filtered if t["status"].lower() == status_filter.lower()]
    if priority_filter:
        filtered = [t for t in filtered if t["priority"] == priority_filter]
    if search:
        s = search.lower()
        filtered = [
            t
            for t in filtered
            if s in t["company"].lower() or s in t["subject"].lower() or s in t["id"].lower()
        ]

    if "table" in _live and _live["table"]:
        try:
            _live["table"].update_data(filtered)
        except Exception:
            pass
    STATE["last_action"] = f"Filters applied ({len(filtered)} shown)"


def _change_status(ticket_id: str, new_status: str):
    for t in STATE["tickets"]:
        if t["id"] == ticket_id:
            old = t["status"]
            t["status"] = new_status
            _log_audit(f"Status: {old} → {new_status}", ticket_id)
            break
    _refresh_table()
    _refresh_health_chart()
    _refresh_audit()


def _assign_ticket(ticket_id: str, new_owner: str):
    for t in STATE["tickets"]:
        if t["id"] == ticket_id:
            t["owner"] = new_owner
            _log_audit(f"Reassigned to {new_owner}", ticket_id)
            break
    _refresh_table()
    _refresh_audit()


def _add_note(ticket_id: str, note: str):
    for t in STATE["tickets"]:
        if t["id"] == ticket_id:
            prefix = t.get("notes", "")
            t["notes"] = (prefix + " | " + note).strip(" |") if prefix else note
            _log_audit(f"Note added: {note[:45]}...", ticket_id)
            break
    _refresh_table()
    _refresh_audit()


def _escalate(ticket_id: str):
    for t in STATE["tickets"]:
        if t["id"] == ticket_id:
            if t["priority"] != "P0":
                t["priority"] = "P0"
                t["status"] = "In Progress"
            _log_audit("ESCALATED to P0", ticket_id)
            break
    _refresh_table()
    _refresh_health_chart()
    _refresh_audit()


def _bulk_resolve():
    """Resolves all non-P0 open tickets (demo bulk action)."""
    count = 0
    for t in STATE["tickets"]:
        if t["status"] != "Resolved" and t["priority"] != "P0":
            t["status"] = "Resolved"
            count += 1
    if count:
        _log_audit(f"Bulk resolved {count} tickets")
    _refresh_table()
    _refresh_health_chart()
    _refresh_audit()


def _reset_data():
    STATE["tickets"] = _seed_tickets()
    STATE["selected_id"] = None
    STATE["audit"].clear()
    STATE["last_action"] = "Data reset to realistic seed"
    _refresh_table()
    _refresh_health_chart()
    _refresh_audit()


# Selection handler — powers the beautiful live detail panel
def _on_ticket_select(payload: dict[str, Any]):
    try:
        idx = payload.get("row_index")
        df = _get_tickets_df()
        if isinstance(df, list):
            if 0 <= idx < len(df):
                STATE["selected_id"] = df[idx]["id"]
        else:
            # pandas path
            row = df.iloc[idx].to_dict()
            STATE["selected_id"] = row.get("id")
        STATE["last_action"] = f"Selected {STATE['selected_id']}"
        print(f"[OpsConsole] Detail panel focused on {STATE['selected_id']}")
    except Exception as e:
        print(f"[OpsConsole] Select error: {e}")


# ------------------------------------------------------------------
# The main console page
# ------------------------------------------------------------------
@app.page("/")
def ops_console():
    cf.ui.title("Customer Ops Console")
    cf.ui.subtitle("Internal platform for support, RevOps, and success teams — zero design debt")

    # Top status + global actions
    with cf.ui.row(gap="4"):
        with cf.ui.card(classes="flex-1"):
            cf.ui.text(f"Last action: {STATE['last_action']}", size="sm")
            cf.ui.badge("Live • All changes stream via WebSocket", variant="success")

        cf.ui.button("Reset Seed Data", on_click=_reset_data, variant="ghost", size="sm")
        cf.ui.button(
            "Bulk Resolve Non-Critical", on_click=_bulk_resolve, variant="secondary", size="sm"
        )

    cf.ui.divider()

    # ------------------------------------------------------------------
    # OPERATIONAL HEALTH + FILTERS (the command bar)
    # ------------------------------------------------------------------
    with cf.ui.row(gap="5"):
        # Mini health viz
        with cf.ui.card(classes="w-80 p-0 overflow-hidden"):
            if HAS_VIZ and PlotlyChart:
                _live["health"] = PlotlyChart(
                    _make_health_figure(),
                    height="128px",
                    title="Live Ticket Health",
                )
            else:
                cf.ui.text("Ticket health metrics (install clayforge[viz] for live chart)")

        # Powerful filter bar
        with cf.ui.card(title="Filters & Search", classes="flex-1"):
            status_f = cf.ui.text_input(
                "Status (exact)", placeholder="Open / In Progress / Resolved", classes="mb-2"
            )
            prio_f = cf.ui.text_input("Priority", placeholder="P0 / P1 / P2 / P3", classes="mb-2")
            search_f = cf.ui.text_input(
                "Search company / subject / ID", placeholder="acme or webhook", classes="mb-2"
            )

            def apply_now():
                _apply_filters(status_f.value, prio_f.value, search_f.value)

            with cf.ui.row(gap="3"):
                cf.ui.button("Apply Filters (server)", on_click=apply_now, variant="primary")
                cf.ui.button("Clear", on_click=lambda: _refresh_table(), variant="ghost")

    cf.ui.divider()

    # ------------------------------------------------------------------
    # THE MASTER TABLE — heart of every ops tool
    # ------------------------------------------------------------------
    with cf.ui.row(gap="6"):
        with cf.ui.card(classes="flex-[2] p-0 overflow-hidden"):
            if HAS_VIZ and DataTable:
                tbl = DataTable(
                    _get_tickets_df(),
                    title="Support Tickets — fully interactive (sort • search • click to inspect)",
                    height="420px",
                    selectable=True,
                    sortable=True,
                    searchable=True,
                    on_select=_on_ticket_select,
                )
                _live["table"] = tbl
            else:
                cf.ui.text("Install clayforge[viz] to unlock the beautiful interactive DataTable.")
                # Show a simple textual list as fallback
                for t in STATE["tickets"][:6]:
                    cf.ui.text(
                        f"{t['id']} • {t['company']} • {t['priority']} • {t['status']}", size="sm"
                    )

        # ------------------------------------------------------------------
        # LIVE DETAIL + ACTION PANEL (this is what makes it feel real)
        # ------------------------------------------------------------------
        with cf.ui.column(gap="4", classes="flex-1"):
            with cf.ui.card(title="Ticket Detail", subtitle="Selection-driven • Live actions"):
                if STATE["selected_id"]:
                    sel = next(
                        (t for t in STATE["tickets"] if t["id"] == STATE["selected_id"]), None
                    )
                    if sel:
                        cf.ui.text(f"{sel['id']} — {sel['company']}", size="lg")
                        cf.ui.badge(
                            f"{sel['priority']}  •  {sel['status']}",
                            variant="warning" if sel["priority"] in ("P0", "P1") else "default",
                        )
                        cf.ui.text(f"Owner: {sel['owner']}", size="sm")
                        cf.ui.text(f"Value: ${sel['value']:,}", size="sm")
                        cf.ui.text(f"Subject: {sel['subject']}", size="sm")

                        if sel.get("notes"):
                            cf.ui.markdown(f"<b>Notes:</b> {sel['notes']}")

                        cf.ui.divider()

                        # Action form inside detail
                        new_note = cf.ui.text_input(
                            "Add internal note",
                            placeholder="Customer replied with logs...",
                            classes="mb-2",
                        )

                        def add_note_now():
                            if new_note.value:
                                _add_note(sel["id"], new_note.value)

                        cf.ui.button(
                            "Add Note",
                            on_click=add_note_now,
                            variant="secondary",
                            size="sm",
                            classes="w-full mb-2",
                        )

                        # Status transitions
                        with cf.ui.row(gap="2"):
                            cf.ui.button(
                                "Mark In Progress",
                                on_click=lambda: _change_status(sel["id"], "In Progress"),
                                size="sm",
                            )
                            cf.ui.button(
                                "Resolve",
                                on_click=lambda: _change_status(sel["id"], "Resolved"),
                                size="sm",
                                variant="primary",
                            )

                        cf.ui.button(
                            "Escalate to P0",
                            on_click=lambda: _escalate(sel["id"]),
                            variant="danger",
                            size="sm",
                            classes="w-full mt-2",
                        )

                        cf.ui.button(
                            "Assign to me",
                            on_click=lambda: _assign_ticket(sel["id"], "you@company.com"),
                            variant="ghost",
                            size="sm",
                            classes="w-full mt-1",
                        )
                else:
                    cf.ui.text(
                        "Click any row in the table above to load rich detail and actions here.",
                        size="sm",
                    )
                    cf.ui.markdown(
                        "Selection events are wired via <span class='font-mono'>on_select=</span> exactly like button handlers."
                    )
                    cf.ui.text(
                        "See full production patterns (incl. auth+db persistence + GrokChat copilot) in clayforge gallery Command Center + examples/06 and auth_db_*.py.",
                        size="xs",
                    )

            # Quick global actions card
            with cf.ui.card(title="Quick Actions"):
                cf.ui.button(
                    "Escalate All P1s",
                    on_click=lambda: [
                        _escalate(t["id"]) for t in STATE["tickets"] if t["priority"] == "P1"
                    ][:4],
                    variant="danger",
                    size="sm",
                    classes="w-full mb-2",
                )
                cf.ui.button(
                    "Resolve All Waiting",
                    on_click=lambda: [
                        _change_status(t["id"], "Resolved")
                        for t in STATE["tickets"]
                        if t["status"] == "Waiting on Customer"
                    ],
                    variant="secondary",
                    size="sm",
                    classes="w-full",
                )

    cf.ui.divider()

    # ------------------------------------------------------------------
    # AUDIT TRAIL — second live DataTable showing complete history
    # ------------------------------------------------------------------
    with cf.ui.card(
        classes="p-0 overflow-hidden",
        title="Audit Trail",
        subtitle="Immutable log of every mutation in this session",
    ):
        if HAS_VIZ and DataTable:
            audit_tbl = DataTable(
                STATE["audit"],
                height="210px",
                title="Action History",
                searchable=True,
                sortable=True,
            )
            _live["audit_table"] = audit_tbl
        else:
            for entry in STATE["audit"][-8:]:
                cf.ui.text(f"{entry['ts']} • {entry['action']} ({entry['ticket']})", size="sm")

    cf.ui.footer(
        "Example 08 • Realistic Internal Admin Tool • DataTable selection + live detail forms + bulk actions + audit trail • "
        "The exact pattern used in real customer operations platforms"
    )

    return cf.ui.column()


if __name__ == "__main__":
    print("Starting ClayForge Internal Ops Console...")
    print("Select rows in the main table to drive the live detail panel with real actions.")
    print(
        "Filters, status changes, escalations, and notes all update the table + health metrics instantly."
    )
    app.run()
