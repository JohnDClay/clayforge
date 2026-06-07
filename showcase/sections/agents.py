"""
Agent Vision section for the ClayForge Showcase.

Framework-native re-create (this run): uses the *real* AgentCanvas component from the framework (dogfooded here in dedicated tab only):
- Live embed of AgentCanvas.to_html() (dynamic mermaid graph, status pills, thought/event stream with rich tool cards)
- Seeded on creation in showcase/app.py with update_agent_status / add_thought / add_event (exact public API per examples/04)
- Controls (play/inject/reset) come from the component itself — clicking ▶ Start runs the upgraded ~3x longer orchestration demo that dynamically spawns new agents (FactChecker/Visualizer/Publisher "pop up" live in graph/pills/feed as if created on-demand). add_agent is now first-class.
- Stunning Live Collaboration Graph polish (pulsing rounded bubbles, animated flowing handoff edges, jitter, tool/spawn bursts, recent highlights + re-render hooks/patch/observer in layout JS) via showcase-specific CSS/JS on top of real AgentCanvas mermaid so the graph is the star — visually on par with the bad-ass 3x long sim + rich feed/tool cards. 100% buildable with ClayForge.
  (User: "we do need to upgrade the live collaboration chart part...it is kind of boring. the rest of the demo run is bad ass tho... make that part more visually on par with the rest of what we have... make the visuals of the agentic team working in real time feel so good. i want our whole team on this too. all agents on hand. team make this research swarm the experience i envision please. go team.")

NO standalone canvas hack; this tab actually uses the framework's AgentCanvas so the showcase demonstrates real usage.

ALWAYS starts with the nice title block + prose first (scroll lands here via showSection).

Title + "all" use .text-center (nested like overview) + consistent containers for centering + pt-2 + layout padding-top:3.5rem.

See examples/04_multi_agent_vision.py for full production patterns with real orchestration loop + GrokChat brain.

Below the live demo: a prominent clean copyable starter (great for people and for AIs evaluating the framework) + two inspiration visuals of other cool agentic presentations you can build with the exact same public API.

Standardized 5-item Jump nav.
"""

import textwrap


def render_agents(agent_canvas=None) -> str:
    """Agent Vision tab content.

    If agent_canvas provided (from showcase orchestrator): embed the real AgentCanvas.to_html()
    (mermaid graph, live status pills, rich tool cards in stream). Framework-native re-create:
    this tab dogfoods the actual framework component (AgentCanvas + public update/add_event API)
    so the showcase demonstrates real buildable usage (no more standalone viz for our own demo).
    Visuals: stunning Live Collaboration Graph (on par with bad-ass demo) via showcase CSS/JS enhancer on the real mermaid (pulsing, animated edges, bursts etc).
    - Proper .demo-section wrapper (hidden) for tab switching.
    - .mb-8 header with title + prose first (padding-top:3.5rem clears topbar + small pt-2 + increased mbs).
    - Title and all use nested text-center (exact match to overview hero) for centering.
    - Premium frame around the embed for world-class polish.
    - Clean copyable production starter snippet + two "other visuals you can build" inspiration cards (replaced the old verbose meta quote block).
    - Standardized 5-item Jump nav (data-section).
    - textwrap.dedent.
    """
    if agent_canvas is not None:
        comp_html = agent_canvas.to_html()
        embed_block = f"""
<div class="mt-6">
    <div class="mb-2.5 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 px-0.5">
        <div class="uppercase text-[10px] tracking-[1.5px] font-semibold text-emerald-400/90">Framework-Native Research Swarm (AgentCanvas dogfood)</div>
        <div class="text-[10px] text-zinc-500">real AgentCanvas + update_agent_status/add_event • <strong>stunning Live Collaboration Graph</strong> (pulsing bubbles, flowing edges, bursts + jitter on live team)</div>
    </div>
    <div class="rounded-3xl overflow-hidden shadow-[0_20px_60px_-15px_rgb(0,0,0,0.65)] ring-1 ring-white/5 border border-zinc-800 bg-zinc-950">
        {comp_html}
    </div>
</div>
"""
    else:
        # Light path (tests/imports): simple teaser, no component
        embed_block = """
<div class="mt-8 w-full px-6">
    <div class="bg-zinc-950 border border-zinc-800 rounded-3xl p-6 text-center ring-1 ring-white/5">
        <div class="text-emerald-400 text-xs tracking-[1.5px] font-semibold mb-2">LIVE FRAMEWORK AGENTCANVAS (pass instance for full demo)</div>
        <div class="text-sm text-zinc-400">Pass a real AgentCanvas(...) instance to render_agents() to see the full interactive demo here (dynamic graph + <strong>stunning Live Collaboration Graph</strong> (pulsing bubbles, flowing animated edges, bursts/jitter), status, rich tool cards, WS reactivity).</div>
    </div>
</div>
"""

    # The embed_block is placed after the prose (title+prose always first). The real component brings its own header/controls/pills/graph/stream.
    # This makes the swarm demo actually built with / using the ClayForge framework (not standalone hack).
    # Per user directive: re-created using real AgentCanvas so "buildable with our framework".
    # Visuals upgraded (stunning Live Collaboration Graph: pulsing rounded bubbles, animated flowing edges, jitter, tool-bursts, recent highlights + live JS hooks in layout) so the graph is the star — feels so good, on par with the bad-ass long orchestration + rich feed.
    # "make the visuals of the agentic team working in real time feel so good. i want our whole team on this too."

    return textwrap.dedent(f"""
<div id="section-agents" class="demo-section hidden">
    <div class="max-w-5xl mx-auto px-6 md:px-8 pt-2 pb-20">
        <div class="mb-8 pt-2">
            <div class="text-center">
                <div class="text-emerald-400 text-xs tracking-[2px] font-semibold">NATIVE MULTI-AGENT SUPPORT</div>
                <div class="font-display text-4xl tracking-tighter font-semibold mt-1">AgentCanvas</div>
                <p class="text-zinc-400 mt-2">The live orchestration surface for real AI agent teams. Production hooks (update_agent_status + rich add_event tool cards + <span class="font-mono">add_agent</span> for dynamic spawns) with instant WS reactivity — exactly like GrokChat.</p>
                <p class="text-xs text-zinc-500 mt-1">Click ▶ Start inside the canvas for the extended 3x demo: watch new specialist agents pop up mid-run in the <strong>Live Collaboration Graph</strong> — now visually stunning with rounded pulsing bubbles, flowing animated edge handoffs, organic jitter, tool-triggered bursts, and live activity highlights. The graph feels <em>alive</em>. See examples/04 for full production orchestration patterns.</p>
            </div>
        </div>

        <div class="prose prose-invert max-w-none text-zinc-300 space-y-4 mb-8">
            <p>AgentCanvas gives you a live, reactive view into multi-agent systems — dynamic graphs, real-time status, and rich tool events. The public API is designed so your real agent code can drive the visualization directly from any orchestration loop.</p>
            <p>Call <span class="font-mono text-emerald-300">update_agent_status</span>, <span class="font-mono text-emerald-300">add_event</span> (for beautiful tool cards), <span class="font-mono text-emerald-300">add_thought</span>, and <span class="font-mono text-emerald-300">add_agent</span> — every mutation pushes instantly via WS. <strong>Click ▶ Start</strong> for a ~3x longer orchestration demo that dynamically spawns new agents (FactChecker, Visualizer, Publisher pop up live in the <strong>Live Collaboration Graph</strong> — deeper shadows, animated data-flow connections pulsing with handoffs, jitter/scale on working nodes, burst flashes + color-morphs on tool/spawn/status (using each agent's color), recent activity rings, + live SVG thinking rings + floating particles added on every re-render). This makes viewers say "hell yeah this is the agentic viz I want". The graph is the visual star that makes the whole research swarm feel so good — synced perfectly to thoughts/tools/status (feels so good in real time).</p>
        </div>

        {embed_block}

        <!-- Clean, copyable usage + inspiration visuals (replaces verbose meta quote block).
             Designed so a human or an AI "dragging" for a framework sees exactly how to use the public API
             and gets excited about what else is possible with AgentCanvas. -->
        <div class="mt-10">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Production-ready starter</div>

            <div class="relative group">
                <pre class="font-mono text-[11px] bg-zinc-950 border border-zinc-800 rounded-2xl p-4 overflow-auto text-zinc-200 leading-[1.35]"><code>from clayforge.grok import AgentCanvas

canvas = AgentCanvas(
    agents=[
        {{"name": "Researcher", "role": "Deep research &amp; sources", "color": "#6366f1"}},
        {{"name": "WebSearch",  "role": "Tool calling &amp; data", "color": "#10b981"}},
        {{"name": "Critic",     "role": "Quality &amp; contradictions", "color": "#f59e0b"}},
        {{"name": "Synthesizer","role": "Final artifacts", "color": "#8b5cf6"}},
    ],
    title="Research Swarm",
    height="420px",
    show_controls=True,
)

# Drive it live from your real orchestration (sync threads, async, etc.)
canvas.update_agent_status("Researcher", "researching", "14 sources")
canvas.add_thought("Researcher", "pulled 14 results for \"ai ui frameworks 2026\"")
canvas.add_event("Researcher", "tool", "web_search",
                 tool_name="web_search", args={{"q": "..."}}, result="14 high-signal sources")

# Dynamic team growth — new agents pop into the graph + pills + feed
canvas.add_agent("FactChecker", "Verification", "#10b981")
canvas.add_thought("FactChecker", "New specialist spawned mid-orchestration")</code></pre>

                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-2 right-2 text-[10px] bg-emerald-600 text-white px-2 py-px rounded'; t.textContent='copied!'; this.after(t); setTimeout(()=>t.remove(), 1400)" class="absolute top-3 right-3 text-[10px] px-2.5 py-1 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[9px]"></i>
                    <span class="hidden sm:inline">Copy</span>
                </button>
            </div>

            <div class="mt-8">
                <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-3">Other visuals you can create with the same public API</div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Visual 1: Parallel tool execution -->
                    <div class="bg-zinc-950 border border-zinc-800 rounded-2xl p-4">
                        <div class="flex items-center justify-between text-[10px] text-zinc-500 mb-3">
                            <span>PARALLEL TOOL SWARM</span>
                            <span class="text-emerald-400 text-[10px]">live tool cards + status</span>
                        </div>
                        <div class="space-y-2 text-xs">
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full" style="background:#6366f1"></div>
                                <div class="font-medium flex-1">Researcher</div>
                                <div class="px-2 py-px rounded bg-indigo-500/20 text-indigo-400 text-[10px]">tool: web_search</div>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full" style="background:#10b981"></div>
                                <div class="font-medium flex-1">WebSearch</div>
                                <div class="px-2 py-px rounded bg-emerald-500/20 text-emerald-400 text-[10px]">tool: parallel_fetch</div>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full" style="background:#f59e0b"></div>
                                <div class="font-medium flex-1">FactChecker</div>
                                <div class="px-2 py-px rounded bg-amber-500/20 text-amber-400 text-[10px]">tool: verify</div>
                            </div>
                        </div>
                        <div class="text-[10px] text-zinc-500 mt-3 italic">Rich <span class="font-mono text-emerald-300">add_event()</span> tool cards pop automatically. Same canvas, different visual layer.</div>
                    </div>

                    <!-- Visual 2: Growing specialist team -->
                    <div class="bg-zinc-950 border border-zinc-800 rounded-2xl p-4">
                        <div class="flex items-center justify-between text-[10px] text-zinc-500 mb-3">
                            <span>GROWING SPECIALIST TEAM</span>
                        </div>
                        <div class="flex flex-wrap gap-2 text-xs">
                            <div class="px-3 py-1 rounded-2xl bg-zinc-900 border border-indigo-500/50 flex items-center gap-1.5"><span>🔬</span> Researcher</div>
                            <div class="px-3 py-1 rounded-2xl bg-zinc-900 border border-emerald-500/50 flex items-center gap-1.5"><span>🛠️</span> WebSearch</div>
                            <div class="px-3 py-1 rounded-2xl bg-zinc-900 border border-amber-500/50 flex items-center gap-1.5"><span>🧐</span> Critic</div>
                            <div class="px-3 py-1 rounded-2xl bg-emerald-900/30 border border-emerald-400 flex items-center gap-1.5"><span class="text-emerald-400">+</span> FactChecker <span class="text-[9px] text-emerald-400">(spawned)</span></div>
                            <div class="px-3 py-1 rounded-2xl bg-emerald-900/30 border border-emerald-400 flex items-center gap-1.5"><span class="text-emerald-400">+</span> Visualizer <span class="text-[9px] text-emerald-400">(spawned)</span></div>
                        </div>
                        <div class="text-[10px] text-zinc-500 mt-3">Call <span class="font-mono text-emerald-300">add_agent()</span> any time — graph, pills, and feed all update instantly.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick cross-nav buttons (plain window.showSection) -->
        <div class="mt-6 pt-4 border-t text-center" style="border-color:var(--cf-border);">
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
</div>
""").strip()
