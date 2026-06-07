"""
ClayForge Example 06 — Production Analytics Dashboard (Viz + Live Reactivity)

A polished, real-world "Command Center" style analytics application that
showcases advanced usage of ClayForge's visualization system combined with
the full component model.

Highlights:
- Heavy use of PlotlyChart: 4 live KPI indicator cards + 2 rich interactive
  charts (trend + breakdown). All fully reactive with dark ClayForge theme.
- DataTable: fully interactive deals log with client-side sort/search/select.
- Cross-component live updates: every action instantly refreshes charts + table
  via the standard .update_figure() / .update_data() WebSocket contract.
- Beautiful production layout: KPI row, dual-chart section, master-detail
  style controls + optional "Data Copilot" (GrokChat) for insight generation.
- Realistic interactions: add deals via form, simulate market events, run
  "forecast" (adds projected series), filter & export patterns.
- Graceful degradation when `pip install "clayforge[viz]"` is missing.

Run (recommended):
    python examples/06_production_viz_dashboard.py

Or via the CLI (hot reload friendly):
    clayforge run --app examples.06_production_viz_dashboard:app

For the richest experience:
    pip install "clayforge[viz]"
    # plotly + pandas power the beautiful charts & dataframe handling
"""

from __future__ import annotations

import datetime
import random

import clayforge as cf
from clayforge.grok import GrokChat

# ------------------------------------------------------------------
# Optional viz imports — the example remains runnable and beautiful
# even without them (graceful fallback figures + messages).
# ------------------------------------------------------------------
try:
    from clayforge.components.viz import DataTable, PlotlyChart

    HAS_VIZ = True
except Exception:
    HAS_VIZ = False
    PlotlyChart = None  # type: ignore
    DataTable = None  # type: ignore


app = cf.App(
    title="ClayForge • Production Analytics",
    description="Real-time command center built with live Plotly + DataTable",
    theme="dark",
)


# ------------------------------------------------------------------
# Production-grade in-memory data model (imagine this is Redis / Postgres)
# ------------------------------------------------------------------
def _seed_data():
    base_date = datetime.date(2026, 4, 1)
    deals = []
    segments = ["Enterprise", "Growth", "Starter", "Pro"]
    regions = ["Americas", "EMEA", "APAC"]

    for i in range(28):
        d = base_date + datetime.timedelta(days=i)
        seg = random.choice(segments)
        rev = random.randint(18000, 165000) if seg == "Enterprise" else random.randint(4200, 48000)
        deals.append(
            {
                "id": f"DEAL-{2400 + i}",
                "date": d.isoformat(),
                "company": random.choice(
                    [
                        "Acme Corp",
                        "Vertex Labs",
                        "Nimbus",
                        "Pinnacle",
                        "Helix",
                        "Forge AI",
                        "Quantum",
                        "Aether",
                    ]
                ),
                "segment": seg,
                "region": random.choice(regions),
                "revenue": rev,
                "stage": random.choice(
                    ["Closed Won", "Closed Won", "Closed Won", "Negotiation", "Proposal"]
                ),
            }
        )
    return deals


STATE = {
    "deals": _seed_data(),
    "last_event": "System initialized",
}


def _get_deals_df():
    """Return current deals as pandas DataFrame or list[dict]."""
    if not HAS_VIZ:
        return STATE["deals"]
    try:
        import pandas as pd

        return pd.DataFrame(STATE["deals"])
    except Exception:
        return STATE["deals"]


def _compute_kpis():
    """Calculate live KPIs from current data."""
    deals = STATE["deals"]
    total_rev = sum(d["revenue"] for d in deals)
    closed = [d for d in deals if d["stage"] == "Closed Won"]
    closed_rev = sum(d["revenue"] for d in closed)
    win_rate = (len(closed) / max(len(deals), 1)) * 100
    avg_deal = total_rev / max(len(deals), 1)

    return {
        "total_revenue": total_rev,
        "closed_won": closed_rev,
        "deal_count": len(deals),
        "win_rate": round(win_rate, 1),
        "avg_deal": round(avg_deal),
    }


# ------------------------------------------------------------------
# Plotly figure factories — all return either real figures or safe dicts
# ------------------------------------------------------------------
def _make_kpi_indicator(
    title: str, value: int | float, prefix: str = "$", suffix: str = "", delta: str = ""
):
    """Beautiful large KPI using Plotly Indicator (production look)."""
    if not HAS_VIZ:
        return {"data": [], "layout": {"title": f"{title}: {prefix}{value:,}{suffix}"}}

    try:
        import plotly.graph_objects as go

        fig = go.Figure(
            go.Indicator(
                mode="number+delta",
                value=value,
                number={
                    "prefix": prefix,
                    "suffix": suffix,
                    "font": {"size": 42, "color": "#f4f4f5"},
                },
                delta={"reference": value * 0.87, "relative": True, "font": {"size": 13}},
                title={"text": title, "font": {"size": 13, "color": "#a1a1aa"}},
            )
        )
        fig.update_layout(
            height=138,
            margin=dict(t=8, r=12, b=8, l=12),
            paper_bgcolor="#18181b",
            plot_bgcolor="#18181b",
        )
        if delta:
            fig.data[0].delta = {"reference": value * 0.87, "relative": True}
        return fig
    except Exception:
        return {"data": [{"type": "indicator", "value": value, "title": {"text": title}}]}


def _make_trend_figure():
    """Multi-series revenue trend over the period (live updates add points)."""
    if not HAS_VIZ:
        return {
            "data": [
                {"x": ["2026-04-01", "2026-04-28"], "y": [1240000, 1875000], "type": "scatter"}
            ],
            "layout": {"title": "Revenue Trend (install clayforge[viz] for full)"},
        }

    try:
        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame(STATE["deals"])
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby(df["date"].dt.date)["revenue"].sum().reset_index()
        daily.columns = ["date", "revenue"]

        fig = px.line(
            daily,
            x="date",
            y="revenue",
            title="Daily Revenue Trend",
            markers=True,
        )
        fig.update_layout(
            height=340,
            margin=dict(t=30, r=20, b=30, l=40),
            paper_bgcolor="#18181b",
            plot_bgcolor="#18181b",
            font=dict(color="#e4e4e7"),
            xaxis=dict(gridcolor="#27272a"),
            yaxis=dict(gridcolor="#27272a", tickprefix="$"),
        )
        return fig
    except Exception:
        return {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [120, 190, 240]}],
            "layout": {"title": "Trend (fallback)"},
        }


def _make_breakdown_figure():
    """Segment + Region breakdown bar chart."""
    if not HAS_VIZ:
        return {
            "data": [{"type": "bar", "x": ["Enterprise", "Growth"], "y": [820000, 310000]}],
            "layout": {},
        }

    try:
        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame(STATE["deals"])
        fig = px.bar(
            df,
            x="segment",
            y="revenue",
            color="region",
            barmode="group",
            title="Revenue by Segment & Region",
        )
        fig.update_layout(
            height=340,
            margin=dict(t=30, r=20, b=30, l=40),
            paper_bgcolor="#18181b",
            plot_bgcolor="#18181b",
            font=dict(color="#e4e4e7"),
        )
        return fig
    except Exception:
        return {
            "data": [
                {"type": "bar", "x": ["Enterprise", "Growth", "Starter"], "y": [820, 310, 140]}
            ],
            "layout": {},
        }


# ------------------------------------------------------------------
# Live component references (captured during page render for handlers)
# ------------------------------------------------------------------
_live_refs: dict = {}  # Holds 'kpi1', 'kpi2', ..., 'trend', 'breakdown', 'table'


def _refresh_all_viz():
    """Push fresh data to every live visualization component."""
    if not HAS_VIZ or not _live_refs:
        return

    kpis = _compute_kpis()

    try:
        if "kpi1" in _live_refs:
            _live_refs["kpi1"].update_figure(
                _make_kpi_indicator("Total Pipeline", kpis["total_revenue"], "$")
            )
        if "kpi2" in _live_refs:
            _live_refs["kpi2"].update_figure(
                _make_kpi_indicator("Closed Won", kpis["closed_won"], "$")
            )
        if "kpi3" in _live_refs:
            _live_refs["kpi3"].update_figure(
                _make_kpi_indicator("Deals", kpis["deal_count"], "", "", "")
            )
        if "kpi4" in _live_refs:
            _live_refs["kpi4"].update_figure(
                _make_kpi_indicator("Win Rate", kpis["win_rate"], "", "%")
            )

        if "trend" in _live_refs:
            _live_refs["trend"].update_figure(_make_trend_figure())
        if "breakdown" in _live_refs:
            _live_refs["breakdown"].update_figure(_make_breakdown_figure())
        if "table" in _live_refs:
            _live_refs["table"].update_data(_get_deals_df())
    except Exception as e:
        print(f"[VizDashboard] Refresh warning: {e}")


# ------------------------------------------------------------------
# Action handlers — all mutate STATE and trigger live component patches
# ------------------------------------------------------------------
def _add_deal(company: str, segment: str, region: str, value: int):
    new_deal = {
        "id": f"DEAL-{2400 + len(STATE['deals']) + random.randint(10, 99)}",
        "date": datetime.date.today().isoformat(),
        "company": company or "New Prospect",
        "segment": segment,
        "region": region,
        "revenue": value,
        "stage": "Proposal",
    }
    STATE["deals"].append(new_deal)
    STATE["last_event"] = f"Added {new_deal['id']} • ${value:,}"
    _refresh_all_viz()


def _simulate_market_event():
    """Realistic chaotic market move — mutates many rows."""
    if not STATE["deals"]:
        return
    boost = random.choice([1.18, 0.79, 1.31])
    for d in random.sample(STATE["deals"], k=min(9, len(STATE["deals"]))):
        d["revenue"] = int(d["revenue"] * boost)
        if random.random() > 0.6:
            d["stage"] = random.choice(["Closed Won", "Negotiation", "Proposal"])

    STATE["last_event"] = f"Market event applied • multiplier {boost:.2f}x"
    _refresh_all_viz()


def _run_forecast():
    """Add a projected series by extending the trend chart (demo only)."""
    # We simply boost a few future-ish entries to simulate model output
    for d in STATE["deals"][-5:]:
        d["revenue"] = int(d["revenue"] * 1.27)
    STATE["last_event"] = "Forecast model run — +27% projected uplift applied to tail"
    _refresh_all_viz()


def _reset_dataset():
    STATE["deals"] = _seed_data()
    STATE["last_event"] = "Dataset reset to seed"
    _refresh_all_viz()


# ------------------------------------------------------------------
# The main page — beautiful, self-documenting, educational layout
# ------------------------------------------------------------------
@app.page("/")
def production_dashboard():
    cf.ui.title("Analytics Command Center")
    cf.ui.subtitle(
        "Live multi-chart dashboard • Reactive DataTable • Production data flows — all in pure Python"
    )

    # Hero status bar
    with cf.ui.row(gap="4"):
        with cf.ui.card(classes="flex-1"):
            cf.ui.text(f"Last event: {STATE['last_event']}", size="sm")
            cf.ui.badge("All systems live • WebSocket synced", variant="success")

        with cf.ui.card(classes="px-4"):
            cf.ui.button("Reset Data", on_click=_reset_dataset, variant="ghost", size="sm")

    cf.ui.divider()

    # ------------------------------------------------------------------
    # LIVE KPI ROW — four beautiful Plotly indicators (the star pattern)
    # ------------------------------------------------------------------
    kpis = _compute_kpis()

    with cf.ui.row(gap="4"):
        if HAS_VIZ and PlotlyChart:
            _live_refs["kpi1"] = PlotlyChart(
                _make_kpi_indicator("Total Pipeline", kpis["total_revenue"], "$"),
                height="148px",
                classes="flex-1",
            )
            _live_refs["kpi2"] = PlotlyChart(
                _make_kpi_indicator("Closed Won", kpis["closed_won"], "$"),
                height="148px",
                classes="flex-1",
            )
            _live_refs["kpi3"] = PlotlyChart(
                _make_kpi_indicator("Active Deals", kpis["deal_count"], "", ""),
                height="148px",
                classes="flex-1",
            )
            _live_refs["kpi4"] = PlotlyChart(
                _make_kpi_indicator("Win Rate", kpis["win_rate"], "", "%"),
                height="148px",
                classes="flex-1",
            )
        else:
            # Graceful text fallback
            for label, val, unit in [
                ("Total Pipeline", f"${kpis['total_revenue']:,}", ""),
                ("Closed Won", f"${kpis['closed_won']:,}", ""),
                ("Deals", str(kpis["deal_count"]), ""),
                ("Win Rate", f"{kpis['win_rate']}%", ""),
            ]:
                with cf.ui.card(title=label, classes="flex-1"):
                    cf.ui.text(f"{val}{unit}", size="2xl")

    cf.ui.divider()

    # ------------------------------------------------------------------
    # MAIN CHARTS — two rich interactive visualizations side-by-side
    # ------------------------------------------------------------------
    with cf.ui.row(gap="5"):
        if HAS_VIZ and PlotlyChart:
            with cf.ui.card(classes="flex-1 p-0 overflow-hidden"):
                _live_refs["trend"] = PlotlyChart(
                    _make_trend_figure(),
                    height="360px",
                    title="Revenue Trend (interactive)",
                )

            with cf.ui.card(classes="flex-1 p-0 overflow-hidden"):
                _live_refs["breakdown"] = PlotlyChart(
                    _make_breakdown_figure(),
                    height="360px",
                    title="Segment × Region Breakdown",
                )
        else:
            with cf.ui.card(title="Charts require clayforge[viz]"):
                cf.ui.text('pip install "clayforge[viz]" to see live Plotly dashboards here.')

    cf.ui.divider()

    # ------------------------------------------------------------------
    # DATA TABLE + POWERFUL ACTION PANEL (the heart of production UX)
    # ------------------------------------------------------------------
    with cf.ui.row(gap="6"):
        # The reactive master table
        with cf.ui.card(classes="flex-[2] p-0 overflow-hidden"):
            if HAS_VIZ and DataTable:
                _live_refs["table"] = DataTable(
                    _get_deals_df(),
                    title="Live Deal Flow (client-side sortable • searchable • selectable)",
                    height="420px",
                    selectable=True,
                    sortable=True,
                    searchable=True,
                    on_select=lambda p: print(f"[Dashboard] Row selected: {p}"),
                )
            else:
                cf.ui.text("Install clayforge[viz] for the interactive DataTable experience.")

        # Control center — forms + high-signal actions
        with cf.ui.column(gap="4", classes="flex-1"):
            with cf.ui.card(title="Log New Deal", subtitle="Instantly reflected everywhere"):
                company = cf.ui.text_input("Company", value="Forge Dynamics", classes="mb-2")
                segment = cf.ui.text_input("Segment", value="Growth", classes="mb-2")
                region = cf.ui.text_input("Region", value="EMEA", classes="mb-2")
                value_str = cf.ui.text_input("Value (USD)", value="47500", classes="mb-2")

                def do_add():
                    try:
                        val = int(value_str.value.replace(",", "").replace("$", ""))
                    except Exception:
                        val = 42000
                    _add_deal(company.value, segment.value, region.value, val)

                cf.ui.button(
                    "Log Deal → Live Update",
                    on_click=do_add,
                    variant="primary",
                    classes="w-full mt-1",
                )

            with cf.ui.card(
                title="Simulation Controls", subtitle="Watch the entire dashboard react"
            ):
                cf.ui.button(
                    "Simulate Market Event",
                    on_click=_simulate_market_event,
                    variant="secondary",
                    classes="w-full mb-2",
                )
                cf.ui.button(
                    "Run Forecast Model (+27%)",
                    on_click=_run_forecast,
                    variant="secondary",
                    classes="w-full mb-2",
                )
                cf.ui.button(
                    "Reset to Seed Data", on_click=_reset_dataset, variant="ghost", classes="w-full"
                )

            with cf.ui.card(title="How this works"):
                cf.ui.markdown(
                    "All four KPI indicators and both charts are <b>PlotlyChart</b> instances.<br>"
                    "The table is a <b>DataTable</b>.<br><br>"
                    "Handlers call <span class='font-mono'>.update_figure()</span> and "
                    "<span class='font-mono'>.update_data()</span> — exactly like GrokChat & AgentCanvas.<br><br>"
                    "Zero manual JS or WebSocket code required."
                )

    # ------------------------------------------------------------------
    # OPTIONAL AI COPILOT — combines viz with GrokChat (another hero component)
    # ------------------------------------------------------------------
    cf.ui.divider()

    with cf.ui.card(
        title="Data Copilot", subtitle="Ask natural language questions about the live dataset"
    ):

        def copilot_handler(chat: GrokChat, message: str):
            import time

            kpis = _compute_kpis()
            # Very small "real" analysis using current live state
            reply = (
                f"Current pipeline: ${kpis['total_revenue']:,} across {kpis['deal_count']} deals "
                f"({kpis['win_rate']}% win rate). "
            )
            if "forecast" in message.lower() or "trend" in message.lower():
                reply += "The recent uptick looks driven by Enterprise segment in EMEA. I would double down on that motion."
            elif "win" in message.lower():
                reply += "Focus on moving Negotiation deals forward — they represent the largest untapped revenue."
            else:
                reply += "Happy to dive deeper into any segment or region."

            for chunk in [reply[i : i + 11] for i in range(0, len(reply), 11)]:
                chat.stream_append(chunk)
                time.sleep(0.028)
            chat.flush()

        GrokChat(
            model="grok-analytics-copilot",
            height="260px",
            placeholder="Ask about trends, segments, or what to do next...",
            on_message=copilot_handler,
        )
        cf.ui.text(
            "For real prod, wire copilot to db queries (see auth_db_*.py) or agent teams (07). Full Command Center cross-mutation in gallery.",
            size="xs",
        )

    cf.ui.footer(
        "Example 06 • Production-grade live visualizations • PlotlyChart + DataTable + GrokChat • "
        "Every mutation is a real WebSocket patch"
    )

    # Clean root return (optional but nice)
    return cf.ui.column()


if __name__ == "__main__":
    print("Starting ClayForge Production Analytics Dashboard...")
    print("Tip: pip install 'clayforge[viz]' for gorgeous live Plotly + pandas DataTables.")
    print("All charts and the table will hot-update when you click the action buttons.")
    app.run()
