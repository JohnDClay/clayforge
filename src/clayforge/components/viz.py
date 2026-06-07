"""
ClayForge Visualization Components

Production-ready, beautiful visualization primitives that follow the exact
ClayForge Element contract (dataclass + __post_init__ + _maybe_attach_or_root
+ to_html + context-manager support + WS live updates via _push_update).

Dependencies (plotly + pandas + altair) are strictly optional and gated behind the
"viz" extra:

    pip install "clayforge[viz]"

- plotly: used for PlotlyChart (CDN-loaded at runtime, no server dep)
- pandas: used optionally inside DataTable for DataFrame handling
- altair: available for users who prefer to create Altair charts and pass
  rendered output or use alongside ClayForge components

Design:
- Drop-in components that "just work" inside @app.page, ui.card(), with: blocks
- Server-side rendering to clean Tailwind zinc/indigo HTML + self-contained JS
- Full live reactivity: call .update_figure(...) or .update_data(...) and the
  browser receives a precise WebSocket DOM patch (no page reload)
- Automatic dark theme harmony with the rest of ClayForge
- Event support (future chart clicks, row selection, sorting notifications)
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..core.element import Element

# ------------------------------------------------------------------
# Optional heavy dependencies (never imported at module load time
# unless the user actually instantiates the component that needs them)
# ------------------------------------------------------------------
_pd = None  # populated lazily inside DataTable only


def _get_pandas():
    """Lazy, cached import of pandas. Returns None if unavailable."""
    global _pd
    if _pd is None:
        try:
            import pandas as _pandas  # type: ignore

            _pd = _pandas
        except Exception:
            _pd = False  # sentinel: pandas not installed
    return _pd if _pd is not False else None


# ------------------------------------------------------------------
# PlotlyChart
# ------------------------------------------------------------------


@dataclass
class PlotlyChart(Element):
    """
    A production-grade, reactive Plotly chart component.

    Zero boilerplate beautiful charts that participate in the live WebSocket
    update system exactly like GrokChat and AgentCanvas.

    Usage (basic):

        import plotly.express as px
        from clayforge.components.viz import PlotlyChart
        import clayforge as cf

        df = px.data.iris()
        fig = px.scatter(
            df, x="sepal_width", y="sepal_length",
            color="species", title="Iris"
        )

        @app.page("/")
        def demo():
            PlotlyChart(fig, height="520px", title="Interactive Scatter")

    Live updates (the killer feature):

        chart = PlotlyChart(fig)
        ...
        # Later, from a button handler or timer:
        new_fig = px.line(...)
        chart.update_figure(new_fig)           # pushes via WS automatically
        # or
        chart.figure = newer_fig
        chart._push_update()                   # explicit

    Context manager + layout friendly:

        with ui.card(classes="p-0 overflow-hidden"):
            PlotlyChart(fig, height="380px")

    With ui factories (also supported):
        cf.ui.divider()
        PlotlyChart(...)   # auto-attaches if top-level

    Props:
        figure: plotly Figure | dict | None
        height: CSS height (e.g. "480px", "60vh")
        width:  CSS width  (default "100%")
        config: Plotly config dict (merged with nice defaults)
        title:  Optional header shown above the chart
        classes: extra Tailwind classes on the outer container

    The component automatically:
    - Loads Plotly from CDN (only once per page)
    - Applies beautiful dark theme defaults matching ClayForge zinc/indigo
    - Uses Plotly.react for smooth client-side transitions when possible
    - Fully survives live DOM replacement from the WS layer

    Advanced:
        chart.on("plotly_click", my_handler)   # future-proof hook
    """

    figure: Any = None  # plotly.graph_objects.Figure | dict | None
    height: str = "480px"
    width: str = "100%"
    config: dict[str, Any] = field(default_factory=dict)
    title: str | None = None

    # --- internal live state (never in repr) ---
    _client_ref: Any | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # Dataclass inheritance fix: support PlotlyChart(fig, title=...) without
        # first positional binding to Element.id (swap if non-str id looks like figure).
        if (
            self.figure is None
            and self.id is not None
            and not isinstance(self.id, (str, type(None)))
        ):
            self.figure = self.id
            import uuid

            object.__setattr__(self, "id", f"el_{uuid.uuid4().hex[:10]}")

        super().__post_init__()

        # Make `PlotlyChart(...)` work beautifully at top level of a page
        # or inside any `with ui.card():`, `with ui.row():` etc.
        try:
            from ..core.ui import _maybe_attach_or_root

            _maybe_attach_or_root(self)
        except Exception:
            pass  # still perfectly usable if attached manually

    # ------------------------------------------------------------------
    # Live update API (identical spirit to GrokChat / AgentCanvas)
    # ------------------------------------------------------------------

    def update_figure(self, figure: Any, *, live: bool = True) -> None:
        """Replace the current figure and optionally push a live WS update."""
        self.figure = figure
        if live:
            self._push_update()

    def _push_update(self, client: Any = None) -> None:
        """Push a fresh HTML representation of this chart over the WebSocket."""
        if client is None:
            client = self._client_ref or getattr(self, "_client", None)

        if client is None:
            return

        try:
            html = self.to_html()
            loop = asyncio.get_event_loop()
            loop.create_task(client.send_update(self.id, html))
        except RuntimeError:
            # No running loop (very early render) — initial HTML is sufficient
            pass
        except Exception:
            # Never let a visualization error take down the app
            pass

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _get_figure_json(self) -> str:
        """Robust serialization supporting Figure objects, dicts, and fallbacks."""
        if self.figure is None:
            return "{}"

        fig = self.figure
        try:
            if hasattr(fig, "to_json"):
                return fig.to_json()
            if hasattr(fig, "to_dict"):
                return json.dumps(fig.to_dict())
            return json.dumps(fig)
        except Exception:
            try:
                return json.dumps(fig)
            except Exception:
                return "{}"

    def to_html(self) -> str:
        """Server-rendered HTML + self-bootstrapping Plotly script."""
        fig_json = self._get_figure_json()

        # Beautiful, minimal defaults + full user override
        cfg: dict[str, Any] = {
            "displaylogo": False,
            "responsive": True,
            "displayModeBar": "hover",
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            **self.config,
        }
        config_json = json.dumps(cfg)

        title_html = ""
        if self.title:
            title_html = (
                f'<div class="px-5 pt-4 pb-2.5 text-sm font-semibold text-white '
                f'border-b border-zinc-800 bg-zinc-950/60">{self.title}</div>'
            )

        plot_div_id = f"plot_{self.id}"

        # The outer shell matches every other ClayForge card / component
        shell = f'''
<div id="{self.id}" class="bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-sm ring-1 ring-white/5 {self.classes or ""}" style="width:{self.width}; height:{self.height};">
    {title_html}
    <div id="{plot_div_id}" style="width:100%; height:100%; min-height:180px;"></div>
</div>
        '''.strip()

        # Self-contained bootstrap script. Uses Plotly.react when the div already
        # exists (friendly to future targeted updates) and falls back gracefully.
        script = f"""
<script>
(function() {{
    function renderPlotly() {{
        const container = document.getElementById('{plot_div_id}');
        if (!container) return;

        const fig = {fig_json};
        const cfg = {config_json};

        const layout = Object.assign({{}}, fig.layout || {{}});

        // Gorgeous ClayForge-native dark theme when user supplied no template
        if (!layout.template && !layout.paper_bgcolor) {{
            layout.paper_bgcolor = '#18181b';
            layout.plot_bgcolor  = '#18181b';
            layout.font = {{ color: '#e4e4e7', family: 'Inter, system-ui, sans-serif', size: 12 }};
            layout.margin = layout.margin || {{ t: 24, r: 24, b: 32, l: 36 }};
            if (layout.xaxis !== undefined) layout.xaxis.gridcolor = '#27272a';
            if (layout.yaxis !== undefined) layout.yaxis.gridcolor = '#27272a';
            if (layout.legend !== undefined) layout.legend.font = {{ color: '#a1a1aa' }};
        }}

        const data = fig.data || [];

        const doPlot = () => {{
            if (window.Plotly && container) {{
                // react is efficient when the plot div is reused
                Plotly.react(container, data, layout, cfg).catch(console.error);
            }}
        }};

        if (window.Plotly) {{
            doPlot();
        }} else {{
            const s = document.createElement('script');
            s.src = 'https://cdn.plot.ly/plotly-2.35.2.min.js';
            s.onload = doPlot;
            s.onerror = () => console.warn('[ClayForge] Failed to load Plotly from CDN');
            document.head.appendChild(s);
        }}
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', renderPlotly, {{ once: true }});
    }} else {{
        // give the DOM a tiny breath (important inside dynamic sections)
        setTimeout(renderPlotly, 0);
    }}
}})();
</script>
        """.strip()

        return shell + "\n" + script

    def _html_tag(self) -> str:
        return "div"

    def handle_event(self, event_name: str, data: dict[str, Any]) -> Any:
        """Future extension point for plotly_* events (click, hover, etc.)."""
        return super().handle_event(event_name, data)


# ------------------------------------------------------------------
# DataTable
# ------------------------------------------------------------------


@dataclass
class DataTable(Element):
    """
    First-class, pandas-native data table with excellent defaults.

    Client-side sorting, live search, and row selection — all wired back to
    your Python code via the standard WebSocket event system.

    Usage:

        import pandas as pd
        from clayforge.components.viz import DataTable

        df = pd.DataFrame({"city": [...], "population": [...]})

        table = DataTable(
            df,
            title="World Cities",
            height="380px",
            selectable=True,
            on_select=lambda payload: print("Selected row", payload)
        )

    Live updates:

        table.update_data(new_df)          # instantly pushes new rows over WS

    Inside layouts:

        with ui.card(classes="p-0"):
            DataTable(df, height="320px")

    Selection / sorting events:

        table.on("select", my_handler)     # receives {"row_index": int, ...}
        table.on("sort",   my_handler)     # receives {"column": str, "direction": "asc|desc"}

    The handler is also available as the on_select= convenience kwarg.

    Data accepted:
        - pandas.DataFrame
        - list[dict]
        - dict[str, list]  (column-oriented)

    All dependencies optional. Works perfectly with zero rows or missing pandas.
    """

    data: Any = None  # DataFrame | list[dict] | dict | None
    columns: list[str] | None = None
    height: str = "420px"
    title: str | None = None
    selectable: bool = True
    sortable: bool = True
    searchable: bool = True
    page_size: int | None = None  # v1: None means render everything (simple & fast)
    on_select: Callable[[dict[str, Any]], Any] | None = None

    # live / interaction state
    _client_ref: Any | None = field(default=None, repr=False)
    _selected_index: int | None = field(default=None, repr=False)
    _search_term: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        # Fix for dataclass inheritance: positional first arg (e.g. DataTable(df, title=..))
        # used to bind to Element.id instead of our .data . Swap back here if detected.
        if self.data is None and self.id is not None and not isinstance(self.id, (str, type(None))):
            self.data = self.id
            import uuid

            object.__setattr__(self, "id", f"el_{uuid.uuid4().hex[:10]}")

        super().__post_init__()

        try:
            from ..core.ui import _maybe_attach_or_root

            _maybe_attach_or_root(self)
        except Exception:
            pass

        # Convenience wiring (identical pattern used by Button in ui.py)
        if self.on_select is not None:
            self.on("select", self._handle_select)

    def _handle_select(self, data: dict[str, Any]) -> None:
        """Internal bridge so on_select= works exactly like on_click= on buttons."""
        if self.on_select:
            try:
                self.on_select(data)
            except Exception:
                # User callbacks must never crash the table / server
                pass

    # ------------------------------------------------------------------
    # Live data mutation API
    # ------------------------------------------------------------------

    def update_data(self, data: Any, *, live: bool = True) -> None:
        """Replace the underlying data and (optionally) push a live table refresh."""
        self.data = data
        self._selected_index = None
        if live:
            self._push_update()

    def _push_update(self, client: Any = None) -> None:
        if client is None:
            client = self._client_ref or getattr(self, "_client", None)
        if client is None:
            return
        try:
            html = self.to_html()
            loop = asyncio.get_event_loop()
            loop.create_task(client.send_update(self.id, html))
        except RuntimeError:
            pass
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Data helpers (pandas optional, never crashes)
    # ------------------------------------------------------------------

    def _normalize_data(self) -> list[dict[str, Any]]:
        """Convert whatever the user passed into a clean list of records."""
        if self.data is None:
            return []

        pandas = _get_pandas()
        if pandas is not None:
            try:
                if isinstance(self.data, pandas.DataFrame):
                    df = self.data
                    if self.columns:
                        keep = [c for c in self.columns if c in df.columns]
                        if keep:
                            df = df[keep]
                    # convert NaN etc to friendly strings for display
                    return df.to_dict(orient="records")
            except Exception:
                pass  # fall through to other formats

        # list of dicts (or list of anything that behaves like one)
        if isinstance(self.data, (list, tuple)):
            if len(self.data) == 0:
                return []
            first = self.data[0]
            if isinstance(first, dict):
                recs: list[dict[str, Any]] = list(self.data)  # type: ignore
                if self.columns:
                    recs = [{k: r.get(k) for k in self.columns if k in r} for r in recs]
                return recs

        # column-oriented dict
        if isinstance(self.data, dict):
            keys = list(self.data.keys())
            if keys:
                try:
                    n = len(next(iter(self.data.values())))
                    recs = []
                    for i in range(n):
                        recs.append({k: self.data[k][i] for k in keys})
                    return recs
                except Exception:
                    pass

        # last resort: wrap scalars or unknown
        return [{"value": str(self.data)}]

    def _get_columns(self, records: list[dict[str, Any]]) -> list[str]:
        if self.columns:
            return list(self.columns)
        if not records:
            return []
        # preserve insertion order from first record
        return list(records[0].keys())

    # ------------------------------------------------------------------
    # Rendering — gorgeous, self-contained table + interactivity
    # ------------------------------------------------------------------

    def to_html(self) -> str:
        records = self._normalize_data()
        cols = self._get_columns(records)

        title_html = ""
        if self.title:
            row_count = len(records)
            title_html = (
                f'<div class="flex items-center justify-between px-5 pt-4 pb-2.5 '
                f'bg-zinc-950/70 border-b border-zinc-800 text-sm font-semibold text-white">'
                f"<span>{self.title}</span>"
                f'<span class="font-mono text-[10px] text-zinc-500">{row_count} rows</span>'
                f"</div>"
            )

        # Header row with sort affordances
        thead_cells = ""
        for c in cols:
            sort_attr = f' data-col="{c}" data-dir="asc"' if self.sortable else ""
            thead_cells += (
                f'<th class="px-4 py-3 text-left text-[10px] font-semibold tracking-[0.5px] '
                f"text-zinc-400 uppercase border-b border-zinc-800 select-none "
                f'{"hover:text-white cursor-pointer transition-colors" if self.sortable else ""}"'
                f"{sort_attr}>{c}"
                f'<span class="sort-ind text-[9px] ml-0.5 opacity-50">{" ↕" if self.sortable else ""}</span></th>'
            )

        # Body rows (selection highlight persisted across Python-driven updates)
        tbody = ""
        for idx, row in enumerate(records):
            cells = ""
            for c in cols:
                val = row.get(c, "")
                safe = str(val).replace("<", "&lt;").replace(">", "&gt;")[:160]
                cells += f'<td class="px-4 py-2.5 text-sm text-zinc-200 border-t border-zinc-800 tabular-nums">{safe}</td>'

            sel_cls = (
                " bg-indigo-500/10 ring-1 ring-inset ring-indigo-500/30"
                if self._selected_index == idx
                else ""
            )
            tbody += (
                f'<tr data-row-index="{idx}" '
                f'class="hover:bg-zinc-800/60 transition-colors {sel_cls} '
                f'{"cursor-pointer" if self.selectable else ""}">'
                f"{cells}</tr>"
            )

        if not tbody:
            tbody = (
                '<tr><td colspan="99" class="px-5 py-8 text-center text-zinc-500 text-sm">'
                "No data to display</td></tr>"
            )

        # Optional live search bar (beautiful & tiny)
        search_bar = ""
        if self.searchable:
            search_bar = f'''
            <div class="px-5 py-3 bg-zinc-950/40 border-b border-zinc-800">
                <input id="{self.id}-search" type="text"
                       class="w-full bg-zinc-900 border border-zinc-700 focus:border-indigo-500/60 text-sm rounded-2xl px-4 py-1.5 text-zinc-200 placeholder:text-zinc-500 outline-none transition-all"
                       placeholder="Filter rows..." value="{self._search_term}">
            </div>'''

        table = f'''
        <div class="flex-1 overflow-auto custom-scroll" style="max-height: calc(100% - 0px);">
            <table class="w-full border-collapse">
                <thead class="sticky top-0 z-10 bg-zinc-900"><tr>{thead_cells}</tr></thead>
                <tbody id="{self.id}-tbody">{tbody}</tbody>
            </table>
        </div>
        '''

        # The complete component (matches aesthetic language of every other element)
        html = f'''
<div id="{self.id}" class="bg-zinc-900 border border-zinc-800 rounded-3xl flex flex-col overflow-hidden shadow-sm {self.classes or ""}" style="height:{self.height}; width:100%;">
    {title_html}
    {search_bar}
    {table}
</div>
        '''.strip()

        # All interactivity is self-contained. No external JS libs required.
        # Events are sent using the exact same protocol the global ClayForge client expects.
        js = f"""
<script>
(function() {{
    const rootId = '{self.id}';
    const root = document.getElementById(rootId);
    if (!root) return;
    const tbody = document.getElementById(rootId + '-tbody');
    const send = (evt, payload) => {{
        const sock = window.__cfSocket;
        if (sock && sock.readyState === 1) {{
            sock.send(JSON.stringify({{
                type: "event",
                element_id: rootId,
                event: evt,
                data: payload || {{}}
            }}));
        }}
    }};

    // Row selection (single-select with nice highlight)
    if ({str(self.selectable).lower()}) {{
        tbody.addEventListener('click', function(e) {{
            const tr = e.target.closest('tr[data-row-index]');
            if (!tr) return;
            tbody.querySelectorAll('tr').forEach(r => r.classList.remove('bg-indigo-500/10', 'ring-1', 'ring-inset', 'ring-indigo-500/30'));
            tr.classList.add('bg-indigo-500/10', 'ring-1', 'ring-inset', 'ring-indigo-500/30');
            const idx = parseInt(tr.getAttribute('data-row-index'), 10);
            send('select', {{ row_index: idx }});
        }});
    }}

    // Client-side column sorting (robust for strings + numbers)
    if ({str(self.sortable).lower()}) {{
        root.querySelectorAll('th[data-col]').forEach(function(th) {{
            th.addEventListener('click', function() {{
                const colName = th.getAttribute('data-col');
                const dir = (th.getAttribute('data-dir') || 'asc') === 'asc' ? 'desc' : 'asc';
                th.setAttribute('data-dir', dir);

                // reset indicators
                root.querySelectorAll('th .sort-ind').forEach(s => s.textContent = ' ↕');
                th.querySelector('.sort-ind').textContent = (dir === 'asc' ? ' ↑' : ' ↓');

                const rows = Array.from(tbody.querySelectorAll('tr[data-row-index]'));
                const colIdx = Array.from(th.parentNode.children).indexOf(th);

                rows.sort(function(a, b) {{
                    const ta = (a.children[colIdx] || {{}}).textContent.trim();
                    const tb = (b.children[colIdx] || {{}}).textContent.trim();
                    const na = parseFloat(ta), nb = parseFloat(tb);
                    let cmp = 0;
                    if (!isNaN(na) && !isNaN(nb)) cmp = na - nb;
                    else cmp = ta.localeCompare(tb, undefined, {{ numeric: true, sensitivity: 'base' }});
                    return dir === 'asc' ? cmp : -cmp;
                }});
                rows.forEach(r => tbody.appendChild(r));
                send('sort', {{ column: colName, direction: dir }});
            }});
        }});
    }}

    // Instant client-side filtering
    const search = document.getElementById(rootId + '-search');
    if (search) {{
        const doFilter = () => {{
            const q = search.value.toLowerCase();
            tbody.querySelectorAll('tr[data-row-index]').forEach(tr => {{
                tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
            }});
        }};
        search.addEventListener('input', doFilter);
        // preserve previous search across live updates
        if (search.value) doFilter();
    }}
}})();
</script>
        """.strip()

        return html + "\n" + js

    def _html_tag(self) -> str:
        return "div"

    def handle_event(self, event_name: str, data: dict[str, Any]) -> Any:
        """Store selection state so future re-renders can re-highlight."""
        if event_name == "select":
            try:
                self._selected_index = int(data.get("row_index", -1))
            except Exception:
                self._selected_index = None
            # capture client for subsequent programmatic updates
            self._client_ref = getattr(self, "_client", None) or self._client_ref
        return super().handle_event(event_name, data)
