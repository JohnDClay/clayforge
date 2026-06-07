"""
Dashboard section for the ClayForge Showcase.
Live KPIs + production viz components demo.

The Live PlotlyChart is now an *active cool demo* (real multi-series trend that the Mutate button extends with new points + restyles when [viz] is present; graceful live fallback animation otherwise).
Added two more new demos: Live Mutation Log (event stream fed by buttons) and Cross-control panel (one control drives chart + log + broadcast).
Code snippets cover the live Plotly/fallback + log pattern.
All consistent with prior polish (copy buttons, clay-cards, cf vars, titles-first, etc.).
"""

from ..state import STATE


def render_dashboard(viz_chart_html: str, viz_table_html: str) -> str:
    """Returns the FULL section wrapper for the Live Interactive Dashboard.

    viz_*_html: pre-rendered HTML strings for the viz components (or graceful fallbacks).
    """
    users = STATE.get("users", 1248)
    revenue = STATE.get("revenue", 48290)

    return f"""<div id="section-dashboard" class="demo-section hidden">
    <div class="max-w-5xl mx-auto px-6 md:px-8 pt-8 pb-20">  <!-- CONSISTENT px-6 md:px-8 (overview model + force rule) for even centering across sidebar states + padded main area -->
        <div class="mb-6">  <!-- THE VERY FIRST THING inside container like overview: .mb-6 header block (titles-first). Enforces layout.py guards (.demo-section > div:first-child .mb-6 + 50px GAP breathing from the obvious banner-adjusted line, no top border/hairline). Content follows immediately for professional dense flow, harmony with 4.75rem + GAP var. -->
            <div class="text-center">
                <div class="flex flex-wrap items-center justify-center gap-2 mb-3">
                    <div class="inline-flex items-center gap-x-2 px-4 h-7 rounded-3xl bg-indigo-500/10 text-indigo-400 text-[10px] font-semibold tracking-[1.5px]">
                        <i class="fa-solid fa-bolt"></i>
                        LIVE PYTHON MUTATIONS
                    </div>
                    <div class="inline-flex items-center gap-x-2 px-4 h-7 rounded-3xl bg-emerald-500/10 text-emerald-400 text-[10px] font-semibold tracking-[1.5px]">
                        <i class="fa-solid fa-sync"></i>
                        WS REACTIVE
                    </div>
                </div>
                <div class="font-display text-4xl tracking-tighter font-semibold">Live Interactive Dashboard</div>
                <p class="mt-2 text-zinc-400 max-w-2xl">KPIs, charts and tables that update instantly from real Python code. WebSocket-powered reactivity with zero boilerplate — the same foundation for your Grok agents and production UIs.</p>
            </div>
        </div>

        <!-- KPIs: clay-card + cf var styles for theming harmony (like theming section cards), subtle enhanced rings for pop, responsive grid, premium numbers (tighter tracking, pop scale), polished mutation actions in third card -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-7 ring-1 ring-white/10 shadow-sm transition-all duration-200 hover:shadow-xl hover:ring-white/15" style="background-color:var(--cf-surface);border-color:var(--cf-border);">
                <div class="flex items-center gap-x-2 text-xs text-zinc-500">
                    <i class="fa-solid fa-users"></i>
                    <span>ACTIVE USERS</span>
                </div>
                <div id="kpi-users" class="text-6xl font-semibold tabular-nums mt-2.5 tracking-[-2.25px] leading-none">{users}</div>
                <div class="text-emerald-400 text-xs mt-1.5 flex items-center gap-1"><i class="fa-solid fa-arrow-trend-up text-[10px]"></i> +12% this week</div>
            </div>
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-7 ring-1 ring-white/10 shadow-sm transition-all duration-200 hover:shadow-xl hover:ring-white/15" style="background-color:var(--cf-surface);border-color:var(--cf-border);">
                <div class="flex items-center gap-x-2 text-xs text-zinc-500">
                    <i class="fa-solid fa-dollar-sign"></i>
                    <span>REVENUE (MRR)</span>
                </div>
                <div class="text-6xl font-semibold tabular-nums mt-2.5 tracking-[-2.25px] leading-none">${revenue:,}</div>
                <div class="text-emerald-400 text-xs mt-1.5 flex items-center gap-1"><i class="fa-solid fa-arrow-trend-up text-[10px]"></i> +8% this week</div>
            </div>
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-7 ring-1 ring-white/10 shadow-sm transition-all duration-200 hover:shadow-xl" style="background-color:var(--cf-surface);border-color:var(--cf-border);">
                <div class="text-xs text-zinc-500 mb-3 flex items-center gap-x-2">
                    <i class="fa-solid fa-bolt"></i>
                    <span>MUTATE &amp; UPDATE</span>
                </div>
                <button onclick="window.bumpDemoUsers()" class="group mt-1 w-full h-11 rounded-2xl bg-white text-zinc-950 text-sm font-semibold flex items-center justify-center gap-x-2 active:scale-[0.985] transition-all hover:bg-zinc-100 shadow-sm">
                    <i class="fa-solid fa-user-plus text-sm group-active:scale-110 transition"></i>
                    <span>+17 Users (real handler)</span>
                </button>
                <button onclick="window.logDemoSale()" class="group mt-3 w-full h-11 rounded-2xl border border-zinc-700 text-sm flex items-center justify-center gap-x-2 hover:bg-zinc-900 active:scale-[0.985] transition-all">
                    <i class="fa-solid fa-handshake text-xs group-active:scale-110 transition"></i>
                    <span>Record Enterprise Sale</span>
                </button>
                <div class="mt-2 text-[10px] text-center text-zinc-500">Live client demo of Python WS pattern</div>
            </div>
        </div>

        <!-- Elegant explanatory line: clean premium subtle card using cf vars for theming propagation (matches grok/forms/theming polish), icon accent, ties live Python mutations to Grok/agents/forms patterns -->
        <div class="mt-8 p-5 rounded-3xl text-sm flex items-start gap-3" style="background-color:var(--cf-surface);border:1px solid var(--cf-border);">
            <i class="fa-solid fa-sync mt-0.5" style="color:var(--cf-accent);"></i>
            <div class="text-zinc-400">
                All updates are <span class="font-medium text-emerald-400">real Python mutations</span> pushed over WebSocket — the same pattern you use for Grok responses, agent events, or form handlers.
                <span class="text-xs text-zinc-500 block mt-0.5">No full page reloads, ever. Pure zero-boilerplate reactivity.</span>
            </div>
        </div>

        <!-- Live demonstration of the new first-class viz components: premium framing (luxurious ring/shadow matching framed main view 4px border + inset shadow language), header + mutate button area now at forms/grok polish level (tracking, active icon scales, consistent pill style), cf-var aware cards, inner viz frame with ring-inset depth -->
        <div class="mt-8">
            <div class="mb-4 px-0.5">
                <div class="text-xs uppercase tracking-[1.5px] font-semibold text-zinc-500">Production Viz Components (first-class in ClayForge)</div>
                <div class="text-xs text-zinc-400 mt-0.5">Embed PlotlyChart &amp; DataTable directly in Python — they render live and support real event handlers + WS mutations.</div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- PlotlyChart live demo -->
                <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-6 ring-1 ring-white/10 shadow-[0_15px_50px_-12px_rgb(0,0,0,0.45)] transition-all" style="background-color:var(--cf-surface-2);border-color:var(--cf-border);">
                    <div class="flex items-center justify-between mb-4 px-1">
                        <div class="text-sm font-semibold flex items-center gap-x-2">
                            <i class="fa-solid fa-chart-line text-indigo-400"></i>
                            <span>Live PlotlyChart</span>
                            <span class="ml-1 inline-flex items-center px-1.5 h-4 rounded-full bg-indigo-500/10 text-indigo-400 text-[9px] font-semibold tracking-wider">LIVE</span>
                        </div>
                        <button onclick="window.updateDemoChart()" class="group text-[10px] px-3.5 py-1.5 rounded-2xl border border-zinc-700 hover:bg-zinc-900 hover:border-zinc-500 active:scale-[0.985] transition-all flex items-center gap-x-1.5 shadow-sm">
                            <i class="fa-solid fa-sync-alt text-[9px] group-active:scale-125 transition"></i>
                            <span>Mutate &amp; Update</span>
                        </button>
                    </div>
                    <div class="rounded-3xl overflow-hidden border border-zinc-700/60 ring-1 ring-inset ring-white/5 bg-black/30 shadow-inner">
                        {viz_chart_html}
                    </div>
                    <div class="text-[10px] text-zinc-500 mt-2.5 px-1 flex items-center gap-x-2">
                        Python restyle via live mutation (exact same flow as production Grok/agent updates)
                        <span id="live-plotly-ts" class="live-ts"></span>
                    </div>
                </div>

                <!-- DataTable live demo -->
                <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-6 flex flex-col ring-1 ring-white/10 shadow-[0_15px_50px_-12px_rgb(0,0,0,0.45)] transition-all" style="background-color:var(--cf-surface-2);border-color:var(--cf-border);">
                    <div class="text-sm font-semibold mb-4 px-1 flex items-center gap-x-2">
                        <i class="fa-solid fa-table text-emerald-400"></i>
                        <span>Live DataTable (pandas-ready, sortable, selectable)</span>
                        <span class="ml-1 inline-flex items-center px-1.5 h-4 rounded-full bg-emerald-500/10 text-emerald-400 text-[9px] font-semibold tracking-wider">LIVE</span>
                    </div>
                    <div class="flex-1 min-h-[280px] rounded-3xl overflow-hidden border border-zinc-700/60 ring-1 ring-inset ring-white/5 bg-black/30 shadow-inner">
                        {viz_table_html}
                    </div>
                    <div class="text-[10px] text-zinc-500 mt-2.5 px-1">Click rows to select • Click headers to sort • Real Python event handlers</div>
                </div>
            </div>
        </div>

        <div class="mt-6 text-[10px] flex items-center gap-2 pt-4" style="color:var(--cf-text-muted);border-top:1px solid var(--cf-border);">
            <span>The Live PlotlyChart card always shows a real line chart (pure SVG, zero deps — the "make the chart with our framework" default). <span class="font-mono px-1.5 py-px rounded text-emerald-300/90 border border-zinc-700" style="background:var(--cf-bg);border-color:var(--cf-border);">pip install "clayforge[viz]"</span> brings the full interactive Plotly version with the exact same live mutation API.</span>
        </div>

        <!-- Code snippets + inspiration visuals (polish run: match agents tab value for humans + AI "framework draggers").
             Clean copyable examples of the viz API + live updates, plus 2 attractive mock visuals showing richer patterns. -->
        <div class="mt-8">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Production code snippets</div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <!-- Snippet 1: basic usage -->
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Basic viz components</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code>import plotly.express as px
from clayforge.components.viz import PlotlyChart, DataTable
import pandas as pd

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

chart = PlotlyChart(fig, height="280px", title="Iris")
table = DataTable(
    pd.DataFrame({{"Company": ["Acme", "Stark"], "ARR": [1.2e6, 890000]}}),
    height="220px", selectable=True, sortable=True
)</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <!-- Snippet 2: live mutations -->
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Live updates from Python (same as agents/Grok)</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code># from a button, timer, or agent loop:
new_fig = px.line(df, x="sepal_width", y=...)
chart.update_figure(new_fig)   # WS push, no reload

# or direct + explicit
chart.figure = newer_fig
chart._push_update()

table.update_data(new_df)      # pandas or list-of-dicts
# selection/sort events wired to your handlers</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <!-- Snippet 3: live Plotly + event log (the active demo you asked for) -->
                <div class="relative group md:col-span-2">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Active live PlotlyChart + fallback + log (cool demo + new log stream)</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code># The Live PlotlyChart card is a real active trend:
# - With [viz]: button does extendTraces + restyle + title (grows live)
# - Without: still flashes card + drives the pure fallback bars + log
# JS (in showcase layout) + the pure chart / log are 100% self-contained demos
# of the same mutation pattern your real Python code uses.</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>
            </div>
        </div>

        <div class="mt-6">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-3">Inspiration: other dashboard patterns you can build</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Visual 1: KPI + trend row -->
                <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-4">
                    <div class="text-[10px] text-zinc-500 mb-2 flex justify-between">
                        <span>MINI KPI + SPARK ROW</span>
                        <span class="text-emerald-400">4 live indicators</span>
                    </div>
                    <div class="grid grid-cols-4 gap-2 text-center text-xs">
                        <div class="bg-zinc-900 border border-zinc-700 rounded-2xl p-2">
                            <div class="text-emerald-400">↑ 12%</div>
                            <div class="font-semibold tabular-nums">1.24k</div>
                            <div class="text-[9px] text-zinc-500">Users</div>
                            <div class="h-1 bg-emerald-400/30 mt-1 rounded"><div class="h-1 w-3/4 bg-emerald-400 rounded"></div></div>
                        </div>
                        <div class="bg-zinc-900 border border-zinc-700 rounded-2xl p-2">
                            <div class="text-emerald-400">↑ 8%</div>
                            <div class="font-semibold tabular-nums">$48k</div>
                            <div class="text-[9px] text-zinc-500">MRR</div>
                            <div class="h-1 bg-emerald-400/30 mt-1 rounded"><div class="h-1 w-2/3 bg-emerald-400 rounded"></div></div>
                        </div>
                        <div class="bg-zinc-900 border border-zinc-700 rounded-2xl p-2">
                            <div class="text-indigo-400">● 3</div>
                            <div class="font-semibold tabular-nums">142</div>
                            <div class="text-[9px] text-zinc-500">Deals</div>
                            <div class="h-1 bg-indigo-400/30 mt-1 rounded"><div class="h-1 w-1/2 bg-indigo-400 rounded"></div></div>
                        </div>
                        <div class="bg-zinc-900 border border-zinc-700 rounded-2xl p-2">
                            <div class="text-amber-400">72%</div>
                            <div class="font-semibold tabular-nums">Win</div>
                            <div class="text-[9px] text-zinc-500">Rate</div>
                            <div class="h-1 bg-amber-400/30 mt-1 rounded"><div class="h-1 w-[72%] bg-amber-400 rounded"></div></div>
                        </div>
                    </div>
                    <div class="text-[9px] text-zinc-500 mt-2">Small Plotly indicators + pure-css trends. Same live update path.</div>
                </div>

                <!-- Visual 2: Agent + viz combo -->
                <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-4">
                    <div class="text-[10px] text-zinc-500 mb-2 flex justify-between">
                        <span>AGENT-POWERED INSIGHT DASH</span>
                    </div>
                    <div class="flex gap-3 text-xs">
                        <div class="flex-1">
                            <div class="text-emerald-400 mb-1">Live team</div>
                            <div class="space-y-1">
                                <div class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-[#6366f1]"></span> Researcher <span class="text-[9px] text-zinc-500">researching</span></div>
                                <div class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-[#f59e0b]"></span> Critic <span class="text-[9px] text-zinc-500">critiquing</span></div>
                                <div class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span> + FactChecker <span class="text-[9px] text-emerald-400">(spawned)</span></div>
                            </div>
                        </div>
                        <div class="flex-1 border-l border-zinc-700 pl-3">
                            <div class="text-emerald-400 mb-1">Insight chart</div>
                            <div class="h-12 bg-zinc-900 border border-zinc-700 rounded flex items-end gap-0.5 p-1">
                                <div class="flex-1 bg-indigo-400" style="height:40%"></div>
                                <div class="flex-1 bg-emerald-400" style="height:75%"></div>
                                <div class="flex-1 bg-amber-400" style="height:55%"></div>
                                <div class="flex-1 bg-violet-400" style="height:90%"></div>
                            </div>
                            <div class="text-[9px] text-zinc-500 mt-0.5">Agent events drive chart mutations + annotations.</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-[9px] text-zinc-500 mt-2 px-1">All patterns use the same live WS + public API. Drop in your own presentation on top of the components.</div>
        </div>

        <!-- NEW DEMO 1: Live Mutation Log (active cool event stream). Appends "real Python/WS style" events.
             Buttons here + side effects from other mutates (KPI, pure chart) feed it. Self-contained + beautiful. -->
        <div class="mt-6">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Live Mutation Log (new demo)</div>
            <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-5 flex flex-col">
                <div class="flex items-center justify-between mb-2">
                    <div class="font-semibold text-sm flex items-center gap-x-2">
                        <i class="fa-solid fa-stream text-emerald-400"></i>
                        <span>Real-time event stream</span>
                    </div>
                    <button onclick="window.emitDashboardEvent()" class="text-[10px] px-3 py-1 rounded-2xl border border-zinc-700 hover:bg-zinc-900 active:scale-[0.985] transition">Emit sample event</button>
                </div>
                <div id="dashboard-log" class="flex-1 min-h-[92px] max-h-[140px] overflow-auto text-[11px] font-mono bg-black/40 border border-zinc-700 rounded-2xl p-3 text-emerald-300/90 leading-snug"></div>
                <div class="text-[9px] text-zinc-500 mt-2">This is exactly how GrokChat thoughts, Agent events, and viz mutations arrive over WS. Click to emit or use other dashboard buttons.</div>
            </div>
        </div>

        <!-- NEW DEMO 2: Cross-control panel (mini form that drives multiple live things at once: pure chart + log + toast).
             Shows how easy it is to wire controls to any live surface. -->
        <div class="mt-4">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Cross-control demo (new)</div>
            <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-5">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end text-xs">
                    <div>
                        <div class="text-zinc-500 mb-1">Target metric</div>
                        <select id="cross-metric" class="w-full bg-zinc-950 border border-zinc-700 rounded-2xl px-3 py-1.5 text-sm">
                            <option value="0">CPU</option>
                            <option value="1">Memory</option>
                            <option value="2">Disk I/O</option>
                            <option value="3">Net</option>
                        </select>
                    </div>
                    <div>
                        <div class="text-zinc-500 mb-1">Delta %</div>
                        <input id="cross-delta" type="range" min="-30" max="30" value="12" class="w-full accent-emerald-400">
                        <div class="text-[10px] text-center text-zinc-400"><span id="cross-delta-val">+12</span>%</div>
                    </div>
                    <div>
                        <button onclick="window.applyCrossControl()" class="w-full h-9 rounded-2xl bg-white text-zinc-950 font-semibold text-sm active:scale-[0.985]">Apply &amp; Broadcast</button>
                    </div>
                </div>
                <div class="text-[9px] text-zinc-500 mt-2">One control mutates the live chart, appends to the log, and shows a toast — zero boilerplate reactive composition.</div>
            </div>
        </div>

        <!-- ACTUAL CHART DEMO (added this run): pure client-side live updating bar chart using only divs + inline onclick.
             Always works (no [viz] extra, no extra script tag inside f-string). Demonstrates real updating visuals with the same "button triggers live change" model used by the rest of the showcase (KPI bumps, plotly mutate, forms sims). CSS transitions for polish. -->
        <div class="mt-6">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Actual live chart demo (pure, no viz extra)</div>
            <div class="clay-card bg-zinc-950 border border-zinc-800 rounded-3xl p-5">
                <div class="flex items-center justify-between mb-3">
                    <div class="font-semibold text-sm flex items-center gap-x-2">
                        <i class="fa-solid fa-chart-bar text-indigo-400"></i>
                        <span>Live Resource Usage</span>
                    </div>
                    <button onclick="document.getElementById('bar0').style.width='79%';document.getElementById('v0').textContent='79%';document.getElementById('bar1').style.width='88%';document.getElementById('v1').textContent='88%';document.getElementById('bar2').style.width='61%';document.getElementById('v2').textContent='61%';document.getElementById('bar3').style.width='74%';document.getElementById('v3').textContent='74%';" class="group text-[10px] px-3 py-1 rounded-2xl border border-zinc-700 hover:bg-zinc-900 active:scale-[0.985] transition flex items-center gap-x-1.5">
                        <i class="fa-solid fa-sync-alt text-[9px] group-active:scale-125 transition"></i>
                        <span>Simulate load spike</span>
                    </button>
                </div>
                <div class="space-y-2 text-xs">
                    <div class="flex items-center gap-3">
                        <div class="w-16 text-right text-zinc-400 tabular-nums">CPU</div>
                        <div class="flex-1 h-4 bg-zinc-900 border border-zinc-700 rounded overflow-hidden"><div id="bar0" class="h-4 transition-all duration-300" style="width:42%;background:#6366f1"></div></div>
                        <div id="v0" class="w-10 text-right font-mono text-zinc-300 tabular-nums">42%</div>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-16 text-right text-zinc-400 tabular-nums">Memory</div>
                        <div class="flex-1 h-4 bg-zinc-900 border border-zinc-700 rounded overflow-hidden"><div id="bar1" class="h-4 transition-all duration-300" style="width:67%;background:#10b981"></div></div>
                        <div id="v1" class="w-10 text-right font-mono text-zinc-300 tabular-nums">67%</div>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-16 text-right text-zinc-400 tabular-nums">Disk I/O</div>
                        <div class="flex-1 h-4 bg-zinc-900 border border-zinc-700 rounded overflow-hidden"><div id="bar2" class="h-4 transition-all duration-300" style="width:28%;background:#f59e0b"></div></div>
                        <div id="v2" class="w-10 text-right font-mono text-zinc-300 tabular-nums">28%</div>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-16 text-right text-zinc-400 tabular-nums">Net</div>
                        <div class="flex-1 h-4 bg-zinc-900 border border-zinc-700 rounded overflow-hidden"><div id="bar3" class="h-4 transition-all duration-300" style="width:55%;background:#8b5cf6"></div></div>
                        <div id="v3" class="w-10 text-right font-mono text-zinc-300 tabular-nums">55%</div>
                    </div>
                </div>
                <div class="text-[9px] text-zinc-500 mt-2">Click the button — bars and values update live with CSS transitions. Same handler-driven live update model as KPIs, viz, and forms sims. Works in any env.</div>
            </div>
        </div>

        <!-- Quick cross-nav buttons (plain window.showSection) so every tab has working navigation CTAs like overview.
             Restores the interconnected "new buttons" feel from the beautiful prior version. Click to jump to any surface.
             Uses same professional small pill style; no layout impact on the title breathing or centering. -->
        <div class="mt-8 pt-5 border-t text-center" style="border-color:var(--cf-border);">
            <div class="text-[10px] uppercase tracking-[1.5px] text-zinc-500 mb-1.5">Jump to other demos</div>
            <div class="flex flex-wrap justify-center gap-1.5">
                <button data-section="overview" class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Overview</button>
                <button data-section="grok" class="px-3 h-7 text-xs rounded-2xl border border-emerald-600/50 hover:bg-emerald-900/20 text-emerald-300 active:scale-[0.985] transition">GrokChat</button>
                <button data-section="agents" class="px-3 h-7 text-xs rounded-2xl border border-emerald-600/50 hover:bg-emerald-900/20 text-emerald-300 active:scale-[0.985] transition">Agent Vision</button>
                <button data-section="dashboard" class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Dashboard</button>
                <button data-section="theming" class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Theming</button>
            </div>
        </div>
    </div>
</div>"""
