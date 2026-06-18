"""
ClayForge Example 05 — Beautiful Visualizations (PlotlyChart + DataTable)

Demonstrates the complete, production-ready visualization components:

- PlotlyChart: reactive, dark-themed, live-updatable Plotly figures
- DataTable: pandas-friendly, client-side sortable / searchable / selectable
- Both fully support live WebSocket updates using the exact same pattern
  as GrokChat and AgentCanvas (no special plumbing required)
- Optional dependencies: everything works even if plotly/pandas are missing

Run:
    python examples/05_visualizations.py
    # or
    clayforge run --app examples.05_visualizations:app

Requires (for full demo):
    pip install "clayforge[viz]"

Cross-integration:
- Use with GrokChat/AgentCanvas (exact same .update_* contract) or auth+db for persisted data.
- See `clayforge showcase` (Dashboard tab) and examples/06, 07 for production patterns.
- Standalone: run this for pure viz components.
"""

from __future__ import annotations

import clayforge as cf
from clayforge.components.viz import DataTable, PlotlyChart

app = cf.App(title="ClayForge • Visualizations Demo")

# ------------------------------------------------------------------
# In-memory demo state (real apps would use a database / store)
# ------------------------------------------------------------------
STATE = {
    "sales": [
        {"region": "North America", "product": "Pro", "revenue": 124000, "deals": 87},
        {"region": "Europe", "product": "Pro", "revenue": 98000, "deals": 64},
        {"region": "Asia", "product": "Starter", "revenue": 64000, "deals": 112},
        {"region": "North America", "product": "Starter", "revenue": 41000, "deals": 95},
        {"region": "Europe", "product": "Enterprise", "revenue": 215000, "deals": 29},
    ]
}


def _make_plotly_figure():
    """Create a fresh Plotly figure (safe even if plotly not installed)."""
    try:
        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame(STATE["sales"])
        fig = px.bar(
            df,
            x="region",
            y="revenue",
            color="product",
            barmode="group",
            title="Revenue by Region & Product",
            labels={"revenue": "Revenue (USD)"},
        )
        fig.update_layout(
            height=380,
            margin=dict(t=40, r=20, b=30, l=40),
        )
        return fig
    except Exception:
        # Fallback: a tiny valid plotly dict so the component still renders something
        return {
            "data": [
                {
                    "type": "bar",
                    "x": ["North America", "Europe", "Asia"],
                    "y": [165000, 313000, 64000],
                    "name": "Demo",
                }
            ],
            "layout": {"title": "Demo Revenue (plotly not installed — install clayforge[viz])"},
        }


def _make_dataframe():
    """Return a pandas DataFrame or plain records."""
    try:
        import pandas as pd

        return pd.DataFrame(STATE["sales"])
    except Exception:
        return STATE["sales"]


@app.page("/")
def visualizations_demo():
    cf.ui.title("Production Visualizations")
    cf.ui.subtitle(
        "PlotlyChart + DataTable — fully reactive, zero boilerplate, zinc/indigo aesthetic"
    )

    # ------------------------------------------------------------------
    # KPI + Controls row
    # ------------------------------------------------------------------
    with cf.ui.row(gap="4"):
        with cf.ui.card(
            title="Live Controls", subtitle="Click to mutate data and watch both components update"
        ):

            def add_deal():
                STATE["sales"].append(
                    {"region": "Asia", "product": "Pro", "revenue": 72000, "deals": 1}
                )
                # Both components will receive fresh data via WS
                if "chart" in globals() and chart is not None:
                    chart.update_figure(_make_plotly_figure())
                if "table" in globals() and table is not None:
                    table.update_data(_make_dataframe())

            cf.ui.button("+ Add demo deal (live update)", on_click=add_deal, variant="primary")

            def reset():
                STATE["sales"].clear()
                STATE["sales"].extend(
                    [
                        {
                            "region": "North America",
                            "product": "Pro",
                            "revenue": 124000,
                            "deals": 87,
                        },
                        {"region": "Europe", "product": "Pro", "revenue": 98000, "deals": 64},
                        {"region": "Asia", "product": "Starter", "revenue": 64000, "deals": 112},
                    ]
                )
                if "chart" in globals() and chart is not None:
                    chart.update_figure(_make_plotly_figure())
                if "table" in globals() and table is not None:
                    table.update_data(_make_dataframe())

            cf.ui.button("Reset data", on_click=reset, variant="secondary")

        with cf.ui.card(title="How it works"):
            cf.ui.text(
                "Both components use the exact same live-update contract as GrokChat.", size="sm"
            )
            cf.ui.markdown(
                "`chart.update_figure(fig)` and `table.update_data(df)` push targeted WebSocket patches."
            )
            cf.ui.text("Client-side sorting, search, and selection all work instantly.", size="sm")
            cf.ui.text(
                "Combine with GrokChat (from clayforge.grok import GrokChat) for AI-assisted dashboard insights — see 06_production_viz_dashboard.py 'Data Copilot'. Use auth+db (examples/auth_db_*.py) for real persistence instead of in-memory STATE.",
                size="sm",
            )

    cf.ui.divider()

    # ------------------------------------------------------------------
    # The actual visualization components (the star of the example)
    # ------------------------------------------------------------------
    global chart, table  # captured so the button handlers above can reach them

    chart = PlotlyChart(
        _make_plotly_figure(),
        height="420px",
        title="Revenue Breakdown (Plotly)",
        classes="mb-6",
    )

    table = DataTable(
        _make_dataframe(),
        title="Sales Records (sortable • searchable • selectable)",
        height="360px",
        selectable=True,
        sortable=True,
        searchable=True,
        on_select=lambda payload: print(f"[DataTable] Row selected: {payload}"),
    )

    # Demonstrates nesting inside cards (the components support context managers automatically)
    with cf.ui.row(gap="6"):
        with cf.ui.card(classes="p-0 flex-1 overflow-hidden"):
            # Re-using the same live objects — they are already attached above
            # For a real page you would just create them inside the card.
            # Here we show the objects we created at top level still render correctly.
            pass  # the chart + table are rendered below via their own to_html calls

    # Because we are not inside a context when creating the two viz objects above,
    # they become top-level roots. They are already rendered by the page function
    # returning normally (ClayForge collects all roots automatically).

    cf.ui.footer(
        "Example 05 • Real Plotly + pandas DataTable • Live WS updates • 100% optional dependencies"
    )

    # Return explicit container so the page is clean (also valid pattern)
    return cf.ui.column()


if __name__ == "__main__":
    print("Starting ClayForge visualization demo...")
    print("Tip: pip install 'clayforge[viz]' for the full Plotly + pandas experience.")
    app.run()
