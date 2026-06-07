"""
ClayForge Showcase

A single beautiful experience that demonstrates what people can build.

Run:
    python -m clayforge showcase
    python -m clayforge run --app showcase:app

Modular architecture:
- layout.py: all chrome (sidebar, topbar, styles, scripts, collapse logic)
- sections/: one file per major demo area
- state.py: demo data
- app.py: thin orchestrator (imports, live component setup, composition)

GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk.
- Uses a brand new, completely different pure client-side HTML/JS visual demo (re-created like the canvas Research Swarm fix for Agent Vision to eliminate embed risks forever).
- NO GrokChat() instance created, NO add_child, NO .to_html() interp in the showcase page.
- The demo lives ONLY inside #section-grok .demo-section (self-contained typewriter streaming, tool cards, demo trigger buttons for visuals).
- Real GrokChat (with optional real streaming via api_key/on_message + WS) remains fully available for user apps and examples/03_grok_chat.py.
- The Agent Vision tab uses the *real* AgentCanvas component (created/seeded/attached here with update_agent_status + add_event, .to_html() ONLY inside its dedicated tab). Framework-native re-create so the showcase's swarm demo is buildable with ClayForge itself (see user: "re-create this again in clayforg framework... look close to that bubble rendition"). 5 nodes + bubble polish (layout) evokes the cool canvas while using 100% framework.
- Each tab starts with nice title + prose first (scroll lands on title).
- Gallery removed; the showcase is our showcase.
"""

import clayforge as cf
from clayforge.grok import AgentCanvas

# Import the new modular structure (no regressions)
from .layout import build_showcase_page
from .sections import (
    render_agents,
    render_dashboard,
    render_forms,
    render_grok,
    render_overview,
    render_theming,
)

# Dogfood the new theming APIs at import time (beautiful default preserved)
cf.set_theme(cf.Theme(name="showcase", mode="dark"))  # explicit use of cf.Theme + set_theme

# Pre-compute the viz demo HTML at module level.
# This prevents raw Plotly Figure / DataTable objects from ever being
# instantiated during render_page() calls (especially the "ready" one),
# which was causing "unhashable type: 'Figure'" in the element registry.
#
# CRITICAL: The Live PlotlyChart card in the showcase MUST always show a real visible
# line chart (user: "why aren't you making the chart look like a fucking chart. it is
# literally a chart demo with no chart. make a line chart or something... if not then
# we need to get rid of it and make the chart with our framework").
#
# Strategy:
# - When clayforge[viz] + pandas/plotly are present: use the real first-class PlotlyChart
#   (full interactive, dark theme, live update_figure support — this *is* the framework's viz).
# - Default (no extra): embed a beautiful, self-contained, zero-dep multi-series **SVG line chart**
#   that looks like a production line chart (axes, grid, legend for Acme/Stark/Wayne, nice
#   ClayForge colors, markers). This is "with our framework" in spirit: pure, beautiful by
#   default, zero boilerplate, and the exact same live mutation pattern (JS-driven point
#   append + path update on "Mutate & Update" + auto on tab open) that real PlotlyChart and
#   Grok/agent components use. Always a chart. No dashed install prompt in the demo.
_viz_chart_html = """<div class="h-[280px] w-full bg-zinc-950 rounded-2xl overflow-hidden border border-zinc-800/70" style="background:#0a0a0a">
<svg id="demo-line-chart" width="100%" height="280" viewBox="0 0 620 280" preserveAspectRatio="xMidYMid meet" style="display:block">
  <defs>
    <linearGradient id="gridGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#27272a" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#18181b" stop-opacity="0.3"/>
    </linearGradient>
  </defs>
  <!-- background + subtle grid -->
  <rect x="0" y="0" width="620" height="280" fill="#0a0a0a"/>
  <!-- vertical grid lines -->
  <g stroke="#27272a" stroke-width="1" opacity="0.7">
    <line x1="70" y1="30" x2="70" y2="230"/>
    <line x1="160" y1="30" x2="160" y2="230"/>
    <line x1="250" y1="30" x2="250" y2="230"/>
    <line x1="340" y1="30" x2="340" y2="230"/>
    <line x1="430" y1="30" x2="430" y2="230"/>
    <line x1="520" y1="30" x2="520" y2="230"/>
  </g>
  <!-- horizontal grid lines (y scale) -->
  <g stroke="#27272a" stroke-width="1" opacity="0.55">
    <line x1="55" y1="55" x2="580" y2="55"/>
    <line x1="55" y1="95" x2="580" y2="95"/>
    <line x1="55" y1="135" x2="580" y2="135"/>
    <line x1="55" y1="175" x2="580" y2="175"/>
    <line x1="55" y1="215" x2="580" y2="215"/>
  </g>
  <!-- y axis labels -->
  <g fill="#64748b" font-size="11" font-family="ui-monospace, monospace">
    <text x="42" y="58" text-anchor="end">45</text>
    <text x="42" y="98" text-anchor="end">35</text>
    <text x="42" y="138" text-anchor="end">25</text>
    <text x="42" y="178" text-anchor="end">15</text>
    <text x="42" y="218" text-anchor="end">5</text>
  </g>
  <!-- x axis labels (time steps) -->
  <g fill="#64748b" font-size="10" font-family="ui-monospace, monospace">
    <text x="70" y="248" text-anchor="middle">0</text>
    <text x="160" y="248" text-anchor="middle">1</text>
    <text x="250" y="248" text-anchor="middle">2</text>
    <text x="340" y="248" text-anchor="middle">3</text>
    <text x="430" y="248" text-anchor="middle">4</text>
    <text x="520" y="248" text-anchor="middle">5</text>
  </g>
  <!-- title -->
  <text x="310" y="22" text-anchor="middle" fill="#e4e4e7" font-size="13" font-weight="600" font-family="Inter, system-ui, sans-serif">Live Company Metrics (ARR trend signals)</text>
  <!-- Acme (indigo) -->
  <polyline id="line-acme" points="70,198 160,162 250,182 340,118 430,90 520,78" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <!-- Stark (emerald) -->
  <polyline id="line-stark" points="70,210 160,186 250,142 340,166 430,98 520,74" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <!-- Wayne (amber) -->
  <polyline id="line-wayne" points="70,218 160,198 250,170 340,130 430,82 520,62" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <!-- current data point markers (match initial) -->
  <g fill="#6366f1" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="198" r="3.5"/><circle cx="160" cy="162" r="3.5"/><circle cx="250" cy="182" r="3.5"/>
    <circle cx="340" cy="118" r="3.5"/><circle cx="430" cy="90" r="3.5"/><circle cx="520" cy="78" r="3.5"/>
  </g>
  <g fill="#10b981" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="210" r="3.5"/><circle cx="160" cy="186" r="3.5"/><circle cx="250" cy="142" r="3.5"/>
    <circle cx="340" cy="166" r="3.5"/><circle cx="430" cy="98" r="3.5"/><circle cx="520" cy="74" r="3.5"/>
  </g>
  <g fill="#f59e0b" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="218" r="3.5"/><circle cx="160" cy="198" r="3.5"/><circle cx="250" cy="170" r="3.5"/>
    <circle cx="340" cy="130" r="3.5"/><circle cx="430" cy="82" r="3.5"/><circle cx="520" cy="62" r="3.5"/>
  </g>
  <!-- legend -->
  <g font-size="11" font-family="Inter, system-ui, sans-serif">
    <rect x="420" y="8" width="10" height="10" rx="2" fill="#6366f1"/><text x="435" y="17" fill="#a1a1aa">Acme</text>
    <rect x="480" y="8" width="10" height="10" rx="2" fill="#10b981"/><text x="495" y="17" fill="#a1a1aa">Stark</text>
    <rect x="540" y="8" width="10" height="10" rx="2" fill="#f59e0b"/><text x="555" y="17" fill="#a1a1aa">Wayne</text>
  </g>
  <!-- axis lines -->
  <g stroke="#3f3f46" stroke-width="1.5">
    <line x1="55" y1="30" x2="55" y2="230"/>
    <line x1="55" y1="230" x2="580" y2="230"/>
  </g>
</svg>
</div>"""
_viz_table_html = '<div class="h-72 flex items-center justify-center text-sm text-zinc-500 border border-dashed border-zinc-700 rounded-2xl">Install <span class="font-mono mx-1">clayforge[viz]</span> for live DataTable</div>'

try:
    import pandas as pd
    import plotly.express as px

    from clayforge.components.viz import DataTable, PlotlyChart

    # Cool active demo chart: multi-series line with markers (time-series style for "live updates" feel).
    # Tied thematically to the Live DataTable companies below (Acme/Stark/Wayne signals + Oscorp covered in table mutates).
    # Users see real Plotly that the "Mutate & Update" button dramatically extends/restyles with new live points.
    _df = pd.DataFrame(
        {
            "t": list(range(6)),
            "Acme": [12, 19, 15, 27, 31, 34],
            "Stark": [8, 14, 22, 18, 29, 35],
            "Wayne": [5, 11, 17, 24, 33, 38],
        }
    )
    _fig = px.line(
        _df,
        x="t",
        y=["Acme", "Stark", "Wayne"],
        markers=True,
        title="Live Company Metrics (ARR trend signals — Mutate & Update grows live)",
        height=280,
    )
    _viz_chart_html = PlotlyChart(_fig, height="280px").to_html()

    _table_df = pd.DataFrame(
        {
            "Company": ["Acme", "Stark", "Wayne", "Oscorp"],
            "ARR": [1240000, 890000, 2100000, 450000],
            "Stage": ["Series B", "Public", "Series C", "Series A"],
        }
    )
    _viz_table_html = DataTable(_table_df, height="280px").to_html()
except Exception:
    pass  # graceful fallback for environments without the [viz] extra

# GUARANTEED VISIBLE LINE CHART FOR THE SHOWCASE DEMO (addresses "make the chart look like a fucking chart"
# and "make the chart with our framework").
# The Live PlotlyChart card in the Production Viz section now *always* renders a real multi-series
# SVG line chart (Acme / Stark / Wayne) with grid, axes, legend, markers. Zero deps, zero timing races
# with hidden sections or CDN. The JS in layout.py (updateDemoChart) performs real live mutations on it
# (append points, shift window, update polylines + pop new circles) — exactly the production pattern.
# When clayforge[viz] is installed the *real* PlotlyChart component is still fully available for user
# apps (and is the first-class framework viz with update_figure + WS live updates).
_DEMO_LINE_CHART_SVG = """<div class="h-[280px] w-full bg-zinc-950 rounded-2xl overflow-hidden border border-zinc-800/70" style="background:#0a0a0a">
<svg id="demo-line-chart" width="100%" height="280" viewBox="0 0 620 280" preserveAspectRatio="xMidYMid meet" style="display:block">
  <defs>
    <linearGradient id="gridGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#27272a" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#18181b" stop-opacity="0.3"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="620" height="280" fill="#0a0a0a"/>
  <g stroke="#27272a" stroke-width="1" opacity="0.7">
    <line x1="70" y1="30" x2="70" y2="230"/>
    <line x1="160" y1="30" x2="160" y2="230"/>
    <line x1="250" y1="30" x2="250" y2="230"/>
    <line x1="340" y1="30" x2="340" y2="230"/>
    <line x1="430" y1="30" x2="430" y2="230"/>
    <line x1="520" y1="30" x2="520" y2="230"/>
  </g>
  <g stroke="#27272a" stroke-width="1" opacity="0.55">
    <line x1="55" y1="55" x2="580" y2="55"/>
    <line x1="55" y1="95" x2="580" y2="95"/>
    <line x1="55" y1="135" x2="580" y2="135"/>
    <line x1="55" y1="175" x2="580" y2="175"/>
    <line x1="55" y1="215" x2="580" y2="215"/>
  </g>
  <g fill="#64748b" font-size="11" font-family="ui-monospace, monospace">
    <text x="42" y="58" text-anchor="end">45</text>
    <text x="42" y="98" text-anchor="end">35</text>
    <text x="42" y="138" text-anchor="end">25</text>
    <text x="42" y="178" text-anchor="end">15</text>
    <text x="42" y="218" text-anchor="end">5</text>
  </g>
  <g fill="#64748b" font-size="10" font-family="ui-monospace, monospace">
    <text x="70" y="248" text-anchor="middle">0</text>
    <text x="160" y="248" text-anchor="middle">1</text>
    <text x="250" y="248" text-anchor="middle">2</text>
    <text x="340" y="248" text-anchor="middle">3</text>
    <text x="430" y="248" text-anchor="middle">4</text>
    <text x="520" y="248" text-anchor="middle">5</text>
  </g>
  <text x="310" y="22" text-anchor="middle" fill="#e4e4e7" font-size="13" font-weight="600" font-family="Inter, system-ui, sans-serif">Live Company Metrics (ARR trend signals)</text>
  <polyline id="line-acme" points="70,198 160,162 250,182 340,118 430,90 520,78" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <polyline id="line-stark" points="70,210 160,186 250,142 340,166 430,98 520,74" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <polyline id="line-wayne" points="70,218 160,198 250,170 340,130 430,82 520,62" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
  <g fill="#6366f1" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="198" r="3.5"/><circle cx="160" cy="162" r="3.5"/><circle cx="250" cy="182" r="3.5"/>
    <circle cx="340" cy="118" r="3.5"/><circle cx="430" cy="90" r="3.5"/><circle cx="520" cy="78" r="3.5"/>
  </g>
  <g fill="#10b981" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="210" r="3.5"/><circle cx="160" cy="186" r="3.5"/><circle cx="250" cy="142" r="3.5"/>
    <circle cx="340" cy="166" r="3.5"/><circle cx="430" cy="98" r="3.5"/><circle cx="520" cy="74" r="3.5"/>
  </g>
  <g fill="#f59e0b" stroke="#0a0a0a" stroke-width="1.5">
    <circle cx="70" cy="218" r="3.5"/><circle cx="160" cy="198" r="3.5"/><circle cx="250" cy="170" r="3.5"/>
    <circle cx="340" cy="130" r="3.5"/><circle cx="430" cy="82" r="3.5"/><circle cx="520" cy="62" r="3.5"/>
  </g>
  <g font-size="11" font-family="Inter, system-ui, sans-serif">
    <rect x="420" y="8" width="10" height="10" rx="2" fill="#6366f1"/><text x="435" y="17" fill="#a1a1aa">Acme</text>
    <rect x="480" y="8" width="10" height="10" rx="2" fill="#10b981"/><text x="495" y="17" fill="#a1a1aa">Stark</text>
    <rect x="540" y="8" width="10" height="10" rx="2" fill="#f59e0b"/><text x="555" y="17" fill="#a1a1aa">Wayne</text>
  </g>
  <g stroke="#3f3f46" stroke-width="1.5">
    <line x1="55" y1="30" x2="55" y2="230"/>
    <line x1="55" y1="230" x2="580" y2="230"/>
  </g>
</svg>
</div>"""

# For the showcase demo we use the guaranteed pure SVG line chart so the card *always* looks like
# a real chart (no dashed note, no reliance on optional plotly at runtime for the visual).
# The real PlotlyChart component (and its live update API) remains the first-class offering for
# user applications.
_viz_chart_for_demo = _DEMO_LINE_CHART_SVG


app = cf.App(title="ClayForge Showcase 2026")


@app.page("/")
def showcase():
    """Thin orchestrator page.

    Clean dedicated-tab strategy (no more "on every page" problems):
    - GrokChat tab: pure JS demo viz (self-contained, no live GrokChat Element in this surface).
    - Agent Vision tab: now uses the *real* AgentCanvas component from the framework (created here, seeded with public API update_agent_status/add_event per examples/04, attached for registry, .to_html() embedded ONLY inside #section-agents). Framework re-create so showcase swarm "is buildable with our framework" (user directive). 5 agents + layout bubble polish makes it look close to the prior canvas bubble rendition while dogfooding real component.
    - All other sections pure marketing HTML.
    - Result: the swarm demo is actually built using / demonstrating ClayForge's AgentCanvas (real mermaid, pills, tool cards, controls driven by public methods). Real component also available in examples/04.
      Titles first everywhere. Gallery removed; the showcase is our showcase.
    """
    # Use the pre-computed module-level strings (prevents Figure leakage into element tree)
    # For the "Live PlotlyChart" demo slot we deliberately use the guaranteed pure SVG line chart
    # (_viz_chart_for_demo) so the card always renders a visible, beautiful, multi-series line chart
    # with no external dependencies or client render races. This is the "make the chart with our
    # framework" solution the user asked for.
    viz_chart_html = _viz_chart_for_demo
    viz_table_html = _viz_table_html

    current_theme_name = cf.get_theme().name

    # Build sections.
    # GrokChat tab: pure client-side demo (no live element for that tab).
    # Agent Vision: create real AgentCanvas (5 agents for bubble node parity), seed with framework public API calls (update_agent_status + add_thought + add_event) for a live populated look (exactly as in examples/04), attach as child for WS registry, pass to render_agents so its .to_html() is interpolated ONLY inside the dedicated #section-agents. This makes the showcase's swarm demo actually use (and demonstrate) the ClayForge framework's AgentCanvas component (real dynamic graph/cards/controls + bubble polish in layout for "close to that bubble rendition").
    # Real AgentCanvas (and GrokChat) remain fully available in examples/ and user code.
    # All tabs start with title + prose first.
    s1 = render_overview()
    s2 = render_theming(current_server_theme=current_theme_name)
    s3 = render_forms()
    s4 = render_dashboard(viz_chart_html, viz_table_html)
    s5 = render_grok()  # pure demo viz

    # --- Real AgentCanvas for the Agent Vision tab (dogfooding the framework) ---
    # 5-agent team (Researcher/WebSearch/Critic/Synthesizer/Coordinator) + rich initial seed using public API.
    # Per user request this run: demo now 3x longer when ▶ Start clicked, with several new agents dynamically
    # spawning mid-process ("pop up" in graph/pills as if created on the fly). Richer seed here so first tab
    # open already looks impressive ("hell yeah — this is the visual agentic flow I want").
    # "lets create an experience for anyone thinking about creating their own ai agents and such. go team."
    swarm_team = [
        {"name": "Researcher", "role": "Deep research & sources", "color": "#6366f1"},
        {"name": "WebSearch", "role": "Tool calling & data", "color": "#10b981"},
        {"name": "Critic", "role": "Quality & contradictions", "color": "#f59e0b"},
        {"name": "Synthesizer", "role": "Final artifacts", "color": "#8b5cf6"},
        {"name": "Coordinator", "role": "Orchestration & handoff", "color": "#64748b"},
    ]
    agent_canvas = AgentCanvas(
        agents=swarm_team,
        title="Research Swarm",
        height="520px",
        show_controls=True,  # the component's play/inject/reset buttons are part of the nice demo
    )
    # Richer initial seed (more thoughts + multiple rich tool cards + varied live statuses) for instant "wow" on load.
    # The internal Start sim (upgraded in components.py) is now ~3x longer with FactChecker/Visualizer/Publisher spawning live.
    # Upgraded Live Agentic Swarm Graph (rich shapes, animated handoff edges, real-time jitter) keeps visual pace.
    # All via real public API so 100% representative of what users get in their own apps (see examples/04).
    agent_canvas.update_agent_status("Researcher", "researching", "3 sources")
    agent_canvas.add_thought("Researcher", 'pulled 14 results for "ai ui frameworks 2026"')
    agent_canvas.add_event(
        "Researcher",
        "tool",
        "web_search",
        tool_name="web_search",
        args={"q": "ai ui frameworks 2026"},
        result="14 high-signal sources found. Top relevance 0.92.",
    )
    agent_canvas.add_thought("Researcher", "Tagged 3 vendor deep-dives + funding signals.")
    agent_canvas.update_agent_status("WebSearch", "tool_use", "parallel fetch")
    agent_canvas.add_thought("WebSearch", "Querying G2 + Crunchbase + dev forums in parallel...")
    agent_canvas.add_event(
        "WebSearch",
        "tool",
        "parallel_fetch",
        tool_name="multi_source",
        args={"targets": ["g2", "crunchbase", "hn"]},
        result="27 data points, 4 outliers flagged",
    )
    agent_canvas.update_agent_status("Critic", "critiquing", "2 tensions")
    agent_canvas.add_thought(
        "Critic", "noted contradiction in two claims; escalating to primary sources"
    )
    agent_canvas.add_event("Critic", "log", "cross-checked with primary sources")
    agent_canvas.add_thought(
        "Critic", "One claim was marketing spin — corrected in shared context."
    )
    agent_canvas.update_agent_status("Synthesizer", "synthesizing", "1 artifact")
    agent_canvas.add_thought("Synthesizer", "produced draft GTM playbook v0.9")
    agent_canvas.add_event(
        "Synthesizer",
        "tool",
        "report_writer",
        tool_name="artifact",
        args={"sections": 5},
        result="Playbook + OKR matrix ready for review",
    )
    agent_canvas.update_agent_status("Coordinator", "thinking", "orchestrating handoff")
    agent_canvas.add_thought("Coordinator", "All lanes active — monitoring for quality gates.")

    s6 = render_agents(agent_canvas)

    sections_html = s1 + s2 + s3 + s4 + s5 + s6

    content = build_showcase_page(sections_html)

    # Return a single Text root...
    # Attach the live agent_canvas as child (for registry/WS like GrokChat in its tab).
    # Text.to_html emits the raw content (with the embed string inside agents section only).
    # Purge keeps only t.
    t = cf.ui.text(content, tag="div")
    t.add_child(agent_canvas)

    # Purge *everything* except our intended `t`.
    import clayforge.core.ui as _ui

    _ui._current_roots[:] = [t]

    return t


if __name__ == "__main__":
    app.run()
