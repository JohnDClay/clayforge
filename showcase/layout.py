"""
Showcase Layout & Chrome

Clean extraction of all custom full-bleed chrome for the ClayForge Showcase:
- Persistent CSS-driven collapsible sidebar (icon-only mode, no re-renders)
- Topbar with live indicator + toggles
- Expand affordance bar
- All styles and robust JS (section switching, keyboard, localStorage persistence)
- Nav generation (CSS classes preserved exactly for active/collapsed states)

ROBUST LAYOUT SYSTEM:
Single --sidebar-width CSS variable + early-sync IIFE + applySidebarState + window resize listener
guarantees main content ALWAYS adjusts its left padding cleanly (18rem <-> 4rem) with smooth transitions,
zero overlap, zero gaps, on load / toggle / resize / all screen sizes.
The core mechanism for "size fit with sidebar": the var update in applySidebarState (and early IIFE) drives
#main-content { padding-left: calc(var(--sidebar-width, 18rem) + 16px) } (and topbar/handle). For Agent Vision
the *framework-native* Research Swarm (real AgentCanvas + update_agent_status/add_event per examples/04, see agents.py)
is in w-full wrapper outside max-w so the live mermaid+ pills+tool-cards reflow with varying width (text areas
capped for polish + .demo-section .max-w-5xl force rule). showSection + load use scrollTo({top:0}).
Agents tab: real AgentCanvas (bubbly nodes via mermaid + our pulse enhancer for "close to bubble rendition").
Grok tab: inits the brand new pure JS GrokChat demo viz. GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk. (different code). Mermaid re-flow for framework AgentCanvas lives in apply (no canvas+raf). 50px title gap is the obvious line (GIANT BANNERs
in get_showcase_styles + get_showcase_scripts). All pages have Jump nav. Gallery removed; showcase is our showcase.
Production-polished; zero embed leaks or centering regressions. This run: re-created swarm in framework so showcase demo *is buildable with our framework* (user: "why did we make something for our literal showcase that is not even buildable with our framework? that doesn't work. we will need to re-create this again in clayforg framework... look close to that bubble rendition").
"""

from __future__ import annotations

# --- Public API for chrome assembly ---


def get_showcase_styles() -> str:
    """Return the custom <style> block for full-bleed showcase layout.
    All sidebar/main-content spacing/overlap issues resolved via single --sidebar-width CSS var system.
    Includes the .demo-section .max-w-5xl force rule (with agent vision fix + uniformity across sidebar states) so
    title+content centering + padding is uniform for max-w areas while the framework AgentCanvas (Research Swarm)
    uses fluid outside wrapper for reflow (real mermaid nodes get bubble polish + pulse via enhancer).
    """
    return """
        :root {
            --sidebar-width-expanded: 18rem;
            --sidebar-width-collapsed: 0px;   /* FULL collapse: nothing visible except the expand arrow/handle */
            --sidebar-width: 18rem;
        }

        .sidebar-collapsed-only { display: none; }

        /* Robust CSS-driven collapsed state for reliable icon-only nav */
        #sidebar.collapsed .nav-item {
            width: 2.5rem;
            height: 2.5rem;
            padding: 0;
            margin-left: auto;
            margin-right: auto;
            justify-content: center;
            gap: 0;
        }
        #sidebar.collapsed .nav-label { display: none !important; }

        /* Full-bleed tight professional layout */
        #cf-page-root > div {
            max-width: none !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Safety net for auto-attached roots (from Elements created during page render).
           GrokChat tab uses pure JS demo (no live GrokChat Element).
           Agent Vision tab *does* use real AgentCanvas (created in showcase/app.py, attached as child for registry, its .to_html() string embedded only inside #section-agents .demo-section).
           The guard below hides any auto-rooted AgentCanvas copy at #cf-page-root level (the interactive one is nested inside the hidden-until-shown section, so visible only on that tab).
           Broad net for other leaks. This is how we safely embed the real component without "on every page" problems.
        */
        #cf-page-root > div.bg-zinc-900.border.border-zinc-800.rounded-3xl.flex.flex-col.overflow-hidden { display: none !important; } /* AgentCanvas auto root guard (real one used for Agent Vision tab) */
        /* Broad safety net: any flex direct child at cf-page-root level (common for our components) but not the main content wrapper — hide so leaked top-level send/start buttons etc from auto-attach go off-screen / never visible. Prevents any residual cutoff or duplicate UI at top of pages. */
        #cf-page-root > div.flex:not(#main-layout) { display: none !important; }

        body > nav:first-of-type,
        body > footer {
            display: none !important;
        }
        body {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        /* === ROBUST VAR-DRIVEN SIDEBAR + MAIN CONTENT LAYOUT ===
           Single source of truth: --sidebar-width (updated by JS on toggle/init/resize).
           - Sidebar width, topbar left offset, main-content left padding, and expand handle
             all react instantly and transition smoothly from ONE value change.
           - Eliminates desync, overlap, gaps, and per-element style fights.
           - Reliable on initial load (early script + CSS fallback), after every toggle,
             on window resize/orientation, and across all screen sizes.
           - Preserves exact zinc/indigo aesthetic and all demo functionality.
        */
        #sidebar {
            width: var(--sidebar-width, 18rem);
            border-right: 4px solid #52525b;
            box-shadow: 8px 0 20px -6px rgb(0 0 0 / 0.55);
            overflow: hidden; /* when collapsed to 0px, nothing leaks */
            /* width transition provided by element's Tailwind transition-all + explicit below for precision */
        }

        /* When fully collapsed, the sidebar itself is invisible except for the separate expand handle */
        #sidebar.collapsed {
            border-right: none;
            box-shadow: none;
        }
        #topbar {
            left: var(--sidebar-width, 18rem);
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        #main-content {
            padding-top: 3.5rem; /* clear fixed h-14 topbar so content/titles start right under bar. Sections use small pt-2 for breathing. This gets title to top of viewable area, eliminates black void above title on tab open. */
            padding-left: calc(var(--sidebar-width, 18rem) + 16px);
            transition: padding-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            min-height: 100vh;
            box-sizing: border-box;
            border-left: 4px solid #52525b; /* HARD, HIGH-CONTRAST border that is the true left edge of the main view pane — content stops here */
            background: #0a0a0a;
            box-shadow: inset 6px 0 14px -4px rgb(0 0 0 / 0.45);
            overflow-x: hidden; /* absolutely prevent any content from bleeding left under the sidebar */
        }
        #sidebar-expand-handle {
            left: var(--sidebar-width, 0px);
            width: 14px;
            transition: left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            background: #27272a;
            border-right: 1px solid #3f3f46;
            z-index: 60;
        }
        #sidebar-expand-handle:hover {
            width: 18px;
            background: #3f3f46;
        }

        /* === CONSISTENT CENTERING FOR ALL TABS (agent vision fix + uniformity across sidebar states) ===
           Force uniform side padding on inner max-w-5xl containers across ALL sections
           (agents was px-6 only while overview used px-6 md:px-8; others varied).
           This ensures professional even/centered look for title and all content
           (headers, prose, wrappers) + symmetrical breathing on every tab/siderbar state.
           2rem matches common md:px-8 value. Placed here in chrome for immediate effect
           without requiring every section file change (though agents will be normalized too).
           NOTE: AgentCanvas wrapper in agents.py is intentionally *outside* its section's max-w-5xl
           (full-width fluid child of .demo-section) so it *does* grow/shrink with main area on sidebar toggle;
           the header prose + post meta stay in max-w for polish. The rule still applies to agents' max-w parts.
           Agent vision fix + uniformity across sidebar states: ensures title area (in max-w) + all other tabs' content
           get consistent padding even as main area width changes via the --sidebar-width driven padding-left.
        */
        .demo-section .max-w-5xl {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* Ensure demo sections are properly isolated via the 'hidden' class (toggled by showSection JS). This keeps each tab's content from appearing or affecting layout on other tabs. */
        .demo-section.hidden {
            display: none !important;
        }

        /* Polish for the brand new pure-JS GrokChat demo viz (Grok tab only; different from real component classes).
           Flex layout makes messages fill + composer bottom-pinned. Tool pop animation + subtle bubble lift on hover for "better looking".
           Isolated to .grok-demo-chat so zero leakage to other tabs or real GrokChat usage.
        */
        .grok-demo-chat {
            display: flex;
            flex-direction: column;
        }
        .grok-demo-chat #grok-demo-messages {
            min-height: 0; /* allow flex shrink for scroll */
        }
        .grok-demo-chat .grok-demo-bubble {
            transition: transform 120ms ease, box-shadow 120ms ease;
        }
        .grok-demo-chat .grok-demo-bubble:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px -2px rgb(0 0 0 / 0.3);
        }
        .grok-demo-chat .grok-demo-tool {
            animation: grokToolPop 180ms ease-out;
        }
        @keyframes grokToolPop {
            from { opacity: 0; transform: translateY(6px) scale(0.985); }
            to { opacity: 1; transform: none; }
        }

        /* Fullscreen mode for Grok demo (user request: taller conversation view, toggleable FS + back button).
           Makes the chat area much larger (and immersive) for reading long convos, while keeping within the custom chrome.
           Messages get extra breathing/padding in FS. Chat widens via negative margin to eat the max-w padding for fuller feel.
           Demo controls (composer + button row) remain fully usable at bottom thanks to flex layout.
           Button text toggles between ⛶ Fullscreen / Exit Fullscreen (synced in init too).
        */
        .grok-demo-chat.grok-fs {
            height: 75vh !important;
            max-width: none !important;
            margin-left: -2rem;
            margin-right: -2rem;
            box-shadow: 0 0 0 1px #3f3f46, 0 30px 90px -20px rgb(0 0 0 / 0.85);
            transition: height 200ms ease, max-width 200ms ease, margin 200ms ease;
        }
        .grok-demo-chat.grok-fs #grok-demo-messages {
            min-height: 0;
            padding: 1.25rem 1rem !important; /* more breathing on messages for tall FS view */
        }

        /* === FRAMEWORK-NATIVE BUBBLE RENDITION POLISH (Agent Vision tab only) ===
           Real AgentCanvas (mermaid graph + status pills + rich tool cards) styled to look *close to the
           prior standalone canvas bubble rendition* (rounded "bubble" nodes, active pulsing/glow on
           non-idle, tool cards already pop via component). 100% buildable with framework: uses the
           live AgentCanvas(...) + update_agent_status / add_event (see app.py seed + examples/04).
           Scoped strictly to #section-agents + .demo-section so zero leakage to other tabs.
           The JS enhancer (in scripts) post-processes svg nodes for pulse when status active.
           This satisfies: "re-create this again in clayforge framework... look close to that bubble rendition".
        */
        #section-agents .mermaid .node rect {
            rx: 16px !important;
            ry: 16px !important;
            transition: filter 160ms ease, transform 160ms ease;
        }
        #section-agents .mermaid .node:hover rect {
            filter: brightness(1.12) saturate(1.08);
        }
        /* Early rules generalized lightly for diamond shapes too (core upgrade) */
        #section-agents .mermaid .node polygon {
            transition: filter 160ms ease, transform 160ms ease;
        }
        #section-agents .mermaid .node:hover polygon {
            filter: brightness(1.12) saturate(1.08);
        }
        @keyframes cf-agent-bubble-pulse {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.035); }
        }
        /* Active nodes (component gives thick stroke + status in label for non-idle) get the sick pulse - cover rect + poly for shapes */
        #section-agents .mermaid .node rect[style*="stroke-width:3"],
        #section-agents .mermaid .node rect[style*="stroke-width: 3"],
        #section-agents .mermaid .node polygon[style*="stroke-width:3"] {
            animation: cf-agent-bubble-pulse 1.55s ease-in-out infinite;
            filter: drop-shadow(0 0 5px rgba(103,232,249,0.35));
        }
        /* Tool cards in the stream already feel like popping bubbles; give extra lift on the tab */
        #section-agents .bg-zinc-950.border.border-zinc-700.rounded-2xl {
            transition: transform 140ms ease, box-shadow 140ms ease;
        }
        #section-agents .bg-zinc-950.border.border-zinc-700.rounded-2xl:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px -4px rgb(0 0 0 / 0.35);
        }

        /* === UPGRADED LIVE COLLABORATION GRAPH (mermaid in Agent Vision) ===
           Make the 'Live Collaboration Graph' visually on par with the bad-ass demo (pulsing nodes, tool cards, long sim with spawns).
           Real-time agentic team working feel: deeper visuals, animated connections for 'handoffs' and activity, enhanced pulsing for working agents,
           better depth/shadows to make the team 'feel alive' in the graph. Scoped to #section-agents.
           Complements existing bubble node polish + enhancer JS (which post-processes SVG for jitter/pulse on active, now with burst + path anims + live hooks).
           Goal: first-time viewer says 'hell yeah, this is the real-time agentic viz I want for my teams'.
           User: "we do need to upgrade the live collaboration chart part...it is kind of boring. the rest of the demo run is bad ass tho... make that part more visually on par with the rest of what we have... make the visuals of the agentic team working in real time feel so good."
        */
        #section-agents .mermaid {
            background: #050505;
            border-radius: 16px;
            border: 1px solid #27272a;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), 0 10px 30px -10px rgb(0 0 0 / 0.6);
            overflow: hidden;
        }
        #section-agents .mermaid svg {
            filter: drop-shadow(0 8px 24px rgb(0 0 0 / 0.55)) drop-shadow(0 2px 6px rgb(0 0 0 / 0.3));
            transition: filter 220ms cubic-bezier(0.23, 1, 0.32, 1);
            background: transparent;
        }
        #section-agents .mermaid svg:hover {
            filter: drop-shadow(0 12px 36px rgb(0 0 0 / 0.7)) drop-shadow(0 4px 10px rgb(0 0 0 / 0.4));
        }
        /* Deep activity ring + premium node visuals for the star graph (UPGRADED for core's richer mermaid: supports rect for stadium/rounded + polygon for diamond critique nodes etc.) */
        #section-agents .mermaid .node rect {
            rx: 18px !important;
            ry: 18px !important;
            transition: transform 160ms cubic-bezier(0.23,1,0.32,1), filter 160ms ease, stroke 120ms ease;
            filter: drop-shadow(0 3px 8px rgb(0 0 0 / 0.45));
        }
        #section-agents .mermaid .node:hover rect {
            filter: brightness(1.15) saturate(1.1) drop-shadow(0 4px 12px rgb(0 0 0 / 0.5));
            transform: scale(1.015);
        }
        /* Support diamond/polygon shapes (critique/fact nodes from core upgrade) + circles for hubs */
        #section-agents .mermaid .node polygon,
        #section-agents .mermaid .node circle,
        #section-agents .mermaid .node ellipse {
            transition: transform 160ms cubic-bezier(0.23,1,0.32,1), filter 160ms ease, stroke 120ms ease;
            filter: drop-shadow(0 3px 8px rgb(0 0 0 / 0.45));
        }
        #section-agents .mermaid .node:hover polygon,
        #section-agents .mermaid .node:hover circle,
        #section-agents .mermaid .node:hover ellipse {
            filter: brightness(1.15) saturate(1.1) drop-shadow(0 4px 12px rgb(0 0 0 / 0.5));
            transform: scale(1.015);
        }
        #section-agents .mermaid .node text {
            font-weight: 600;
            letter-spacing: 0.2px;
        }
        /* Stronger base + active styles (thick stroke from mermaid diagram for non-idle + .active/.recent from JS). Generalized beyond rect for new shapes (diamonds get glow too) */
        #section-agents .mermaid .node.active rect,
        #section-agents .mermaid .node.active polygon,
        #section-agents .mermaid .node.active circle,
        #section-agents .mermaid .node.active ellipse,
        #section-agents .mermaid .node.recent rect,
        #section-agents .mermaid .node.recent polygon,
        #section-agents .mermaid .node.recent circle,
        #section-agents .mermaid .node.recent ellipse,
        #section-agents .mermaid .node rect[style*="stroke-width:3"],
        #section-agents .mermaid .node rect[style*="stroke-width: 3"],
        #section-agents .mermaid .node polygon[style*="stroke-width:3"],
        #section-agents .mermaid .node polygon[style*="stroke-width: 3"] {
            filter: drop-shadow(0 0 11px rgba(103,232,249,0.65)) drop-shadow(0 4px 10px rgb(0 0 0 / 0.35));
        }
        /* Animated connections: always subtle flow for 'alive team' feel; stronger + cyan on active handoffs */
        #section-agents .mermaid .edgePath path,
        #section-agents .mermaid .flowchart-link {
            stroke: #3f3f46;
            stroke-width: 2.25;
            transition: stroke 140ms ease, stroke-width 140ms ease, stroke-dasharray 140ms ease;
        }
        #section-agents .mermaid .edgePath.active path,
        #section-agents .mermaid .edgePath path[style*="stroke:#6366f1"],
        #section-agents .mermaid .edgePath path[style*="stroke:#10b981"],
        #section-agents .mermaid .edgePath path[style*="stroke:#ef4444"],
        #section-agents .mermaid .edgePath path[style*="stroke:#06b6d4"],
        #section-agents .mermaid .edgePath path[style*="stroke:#f472b6"] {
            stroke: #67e8f9;
            stroke-width: 2.75;
            stroke-dasharray: 7 4;
            animation: cf-edge-flow 980ms linear infinite;
        }
        @keyframes cf-edge-flow {
            to { stroke-dashoffset: -11; }
        }
        /* Arrowheads pop with activity */
        #section-agents .mermaid .arrowheadPath {
            fill: #52525b;
            transition: fill 120ms ease;
        }
        #section-agents .mermaid .edgePath.active .arrowheadPath,
        #section-agents .mermaid .edgePath path[style*="stroke:#6366f1"] ~ .arrowheadPath {
            fill: #67e8f9;
            filter: drop-shadow(0 0 3px rgba(103,232,249,0.6));
        }
        /* Burst flash + organic jitter for working agents (triggered by JS enhancer on tool/status/spawn) */
        @keyframes cf-agent-bubble-pulse {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.032); }
        }
        @keyframes cf-agent-jitter {
            0%,100% { transform: translate(0,0) scale(1.032); }
            20% { transform: translate(0.7px, -0.5px) scale(1.038); }
            40% { transform: translate(-0.5px, 0.6px) scale(1.035); }
            70% { transform: translate(0.4px, 0.3px) scale(1.04); }
        }
        @keyframes cf-agent-burst {
            0% { transform: scale(1.09); filter: drop-shadow(0 0 16px rgba(103,232,249,0.85)) drop-shadow(0 3px 9px rgb(0 0 0 / 0.4)); }
            35% { transform: scale(1.045); filter: drop-shadow(0 0 9px rgba(103,232,249,0.55)); }
            100% { transform: scale(1.032); filter: drop-shadow(0 0 11px rgba(103,232,249,0.65)) drop-shadow(0 4px 10px rgb(0 0 0 / 0.35)); }
        }
        #section-agents .mermaid .node.active rect,
        #section-agents .mermaid .node.active polygon,
        #section-agents .mermaid .node.active circle,
        #section-agents .mermaid .node.active ellipse,
        #section-agents .mermaid .node rect[style*="stroke-width:3"],
        #section-agents .mermaid .node polygon[style*="stroke-width:3"] {
            animation: cf-agent-bubble-pulse 1.48s ease-in-out infinite, cf-agent-jitter 620ms steps(3) infinite;
        }
        #section-agents .mermaid .node.burst rect,
        #section-agents .mermaid .node.burst polygon {
            animation: cf-agent-burst 820ms cubic-bezier(0.23,1.0,0.32,1) forwards;
        }
        /* Recent activity highlight (wired from showSection/apply + enhancer) */
        #section-agents .mermaid .node.recent rect,
        #section-agents .mermaid .node.recent polygon {
            stroke-width: 3.5px !important;
            filter: drop-shadow(0 0 14px rgba(52,211,153,0.55)) drop-shadow(0 0 11px rgba(103,232,249,0.4));
        }
        /* Tool cards lift already present, enhanced depth on agents tab for harmony with graph */
        #section-agents .bg-zinc-950.border.border-zinc-700.rounded-2xl {
            transition: transform 140ms cubic-bezier(0.23,1,0.32,1), box-shadow 140ms ease, border-color 120ms;
        }
        #section-agents .bg-zinc-950.border.border-zinc-700.rounded-2xl:hover {
            transform: translateY(-1.5px);
            box-shadow: 0 10px 24px -6px rgb(0 0 0 / 0.4);
            border-color: #3f3f46;
        }

        /* === REAL-TIME SVG PARTICLES + RINGS (added dynamically by enhance JS on every re-render) ===
           'thinking' nodes get orbiting/expanding rings + floating particles (tiny dots) for alive AI swarm feel.
           Status flash: quick color burst using the agent's own color (from core data-activity).
           Data flow on edges already strong; this + rings makes graph the visual star synced to thoughts/tools/spawns.
           Scoped #section-agents only. Re-applied after mermaid.run via patch/observer/enhance calls.
        */
        #section-agents .mermaid .node .thinking-ring {
            fill: none;
            stroke: currentColor;
            stroke-width: 1.75;
            opacity: 0.55;
            pointer-events: none;
            animation: cf-ring-expand 1650ms cubic-bezier(0.23,1,0.32,1) infinite;
        }
        #section-agents .mermaid .node .ai-particle {
            fill: #67e8f9;
            opacity: 0.85;
            pointer-events: none;
            animation: cf-particle-drift 780ms ease-out forwards;
        }
        #section-agents .mermaid .node .ai-particle.p2 { animation-delay: 120ms; }
        #section-agents .mermaid .node .ai-particle.p3 { animation-delay: 260ms; }
        #section-agents .mermaid .node .ai-particle.p4 { animation-delay: 410ms; }
        @keyframes cf-ring-expand {
            0% { transform: scale(0.92); opacity: 0.7; }
            50% { transform: scale(1.18); opacity: 0.35; }
            100% { transform: scale(0.92); opacity: 0.7; }
        }
        @keyframes cf-particle-drift {
            0% { transform: translate(0,0) scale(1); opacity: 0.9; }
            80% { transform: translate(var(--dx, 6px), var(--dy, -7px)) scale(0.6); opacity: 0.1; }
            100% { transform: translate(var(--dx, 8px), var(--dy, -9px)) scale(0.3); opacity: 0; }
        }
        /* Color-morph flash for status changes, driven by JS using per-agent color from data-activity */
        #section-agents .mermaid .node.flash rect {
            transition: filter 90ms ease, stroke 90ms;
            filter: drop-shadow(0 0 18px var(--flash-color, #67e8f9)) brightness(1.25);
        }

        /* === LIVE VIZ DEMO UPGRADE (exact Production Viz Components block: Live PlotlyChart + Live DataTable) ===
           Makes the two cards under "Production Viz Components (first-class...)" show obvious cool visual change.
           - Plotly: new points extend on lines, restyle, title ts (when [viz]); strong card glow + ts badge always.
           - DataTable: ARR cells bump + emerald flash on mutate; occasional new row slides in (demo of Python .update_data).
           - Auto one mutate shortly after switching to Dashboard tab ("changes when the demo is started").
           - Filter input, row select, header sort already real (from component self-JS) + now backed by live value mutation.
           - "Python restyle via live mutation (exact same flow as production Grok/agent updates)" is now visually true here.
           Scoped strictly to dashboard section so zero leakage. Matches user request for visible cool demo in this part.
        */
        #section-dashboard .live-viz-card-glow {
            box-shadow: 0 0 0 3px rgba(99,102,241,0.28), 0 15px 50px -12px rgb(0,0,0,0.45) !important;
            transition: box-shadow 140ms ease;
        }
        #section-dashboard td.live-cell-update {
            animation: cf-live-cell-flash 820ms ease-out;
            background: rgba(16,185,129,0.22) !important;
            transition: background 120ms ease;
        }
        @keyframes cf-live-cell-flash {
            0% { background: rgba(16,185,129,0.48); transform: scale(1.015); }
            55% { background: rgba(16,185,129,0.16); }
            100% { background: transparent; transform: scale(1); }
        }
        #section-dashboard tr.live-new-row {
            animation: cf-new-row-slide 380ms ease-out;
        }
        @keyframes cf-new-row-slide {
            from { opacity: 0; transform: translateY(-7px); }
            to { opacity: 1; transform: none; }
        }
        #section-dashboard .live-ts {
            font-family: ui-monospace, monospace;
            font-size: 9px;
            color: #64748b;
        }

        /* === PURE SVG LINE CHART (the always-visible "Live PlotlyChart" demo when no [viz]) ===
           Pro look: dark grid, colored series (Acme indigo / Stark emerald / Wayne amber), crisp markers.
           JS mutations (below) append new points, shift the window, update polylines + circles live.
           This is the "make the chart with our framework" solution: zero external deps, beautiful
           by default, 100% live-mutable via the same pattern as real PlotlyChart / Grok / agents.
           Scoped to the dashboard card only.
        */
        #section-dashboard #demo-line-chart {
            background: #0a0a0a;
            border-radius: 12px;
        }
        #section-dashboard #demo-line-chart polyline {
            transition: stroke 120ms ease;
        }
        #section-dashboard #demo-line-chart circle {
            transition: transform 160ms cubic-bezier(0.23,1,0.32,1), opacity 120ms ease;
        }
        #section-dashboard #demo-line-chart circle.new-point {
            animation: cf-point-pop 420ms ease-out;
        }
        @keyframes cf-point-pop {
            0% { transform: scale(0.3); opacity: 0.3; }
            60% { transform: scale(1.25); }
            100% { transform: scale(1); opacity: 1; }
        }

"""


def get_showcase_scripts() -> str:
    """Return the robust JS for sidebar collapse, nav, section switching, and demo handlers.
    Sidebar state via single CSS var + resize listener = perfect sync forever.
    showSection always scrollTo top=0. Agents: framework-native AgentCanvas (real, no canvas swarm hack); mermaid reflow + bubble enhancer call.
    Grok: init brand new pure JS chat demo viz (GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk).
    Mermaid reinit + enhanceAgentBubbles for framework swarm called from apply/showSection.
    Delegation + window. assigns + early IIFE preserved.
    """
    return """
    // --- Robust Collapsible Sidebar + Navigation + Section Switching ---
    // All toggles (chevron inside sidebar + Menu button in topbar) + expand handle share the same reliable path.
    // SINGLE --sidebar-width CSS var (set in apply + early script) drives sidebar width, topbar, main-content padding-left, handle.
    // + resize listener + CSS transitions = production-polished, zero-overlap, zero-gap behavior forever.
    // Nav uses persistent DOM elements + CSS for collapsed icon-only (no re-render, active preserved).
    // showSection always scrolls to top of viewport (main content area starts below fixed topbar).
    // showSection for agents: framework-native AgentCanvas (real component + bubble enhancer for close-to-canvas look). Sidebar open by default for all (incl agents).
    // showSection for grok: init the brand new pure JS GrokChat demo viz (completely different code).
    // Resize guard (__cfSkipApplyOnNextResize) enables safe dispatch for mermaid re-inits.

    // Sidebar defaults OPEN on startup and for each tab/page until the user manually closes it the first time (then we persist the closed state).
    // (Agents no longer forces close; fixed per user to be open by default again for all pages.)
    // Only toggleSidebar / expandSidebar (user clicks) write to localStorage.
    let hasManualSidebarPref = localStorage.getItem('cf-sidebar-collapsed') !== null;
    let sidebarCollapsed = hasManualSidebarPref ? (localStorage.getItem('cf-sidebar-collapsed') === 'true') : false;
    let currentSection = 'overview';
    const TOPBAR_HEIGHT = 16; // matches h-14 fixed topbar + border; used to prevent title/button cutoff under header

    // (No more pure canvas swarm JS; Agent Vision tab now uses real AgentCanvas embed from framework.
    // Mermaid reinit for graph reflow on sidebar resize is in applySidebarState below.)

    function applySidebarState() {
        const sidebar = document.getElementById('sidebar');
        const topbar = document.getElementById('topbar');
        const icon = document.getElementById('collapse-icon');
        const handle = document.getElementById('sidebar-expand-handle');

        if (!sidebar || !topbar) return;

        const expanded = '18rem';
        const collapsed = '0px';
        const currentWidth = sidebarCollapsed ? collapsed : expanded;

        // CENTRAL ROBUST MECHANISM:
        // Update a SINGLE CSS custom property. The entire layout (sidebar, topbar, #main-content padding, handle)
        // reacts automatically via CSS. Guarantees zero overlap, zero unwanted gaps, and silky transitions
        // on every state change. No more inline style desyncs or fallback branches for main-content.
        document.documentElement.style.setProperty('--sidebar-width', currentWidth);

        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');

            document.querySelectorAll('.sidebar-expanded-only').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.sidebar-collapsed-only').forEach(el => el.style.display = 'flex');

            if (icon) icon.classList.replace('fa-chevron-left', 'fa-chevron-right');

            if (handle) {
                handle.classList.remove('hidden');
            }
        } else {
            sidebar.classList.remove('collapsed');

            document.querySelectorAll('.sidebar-expanded-only').forEach(el => el.style.display = '');
            document.querySelectorAll('.sidebar-collapsed-only').forEach(el => el.style.display = 'none');

            if (icon) icon.classList.replace('fa-chevron-right', 'fa-chevron-left');

            if (handle) handle.classList.add('hidden');
        }

        // Agent Vision special (real AgentCanvas embed): re-run mermaid on the live graph when sidebar changes the container width.
        // The embed brings its own .mermaid pre + init script. On width change we remove data-processed and re-run so the svg reflows.
        // (No auto sidebar collapse for agents anymore; open by default for all pages.)
        const agentsEl = document.getElementById('section-agents');
        if (agentsEl && !agentsEl.classList.contains('hidden') && window.mermaid) {
            setTimeout(() => {
                try {
                    const pres = agentsEl.querySelectorAll('.mermaid');
                    pres.forEach(p => {
                        if (p) {
                            p.removeAttribute('data-processed');
                            mermaid.run({ nodes: [p] }).catch(() => {});
                        }
                    });
                    const svgs = agentsEl.querySelectorAll('.mermaid svg');
                    svgs.forEach(s => {
                        if (s) {
                            s.style.width = '100%';
                            s.style.maxWidth = '100%';
                            s.style.height = 'auto';
                        }
                    });
                    setTimeout(() => {
                        try {
                            window.__cfSkipApplyOnNextResize = true;
                            window.dispatchEvent(new Event('resize'));
                        } catch (e) {}
                    }, 0);
                    // Wire more for graph: after sidebar-driven reinit+run, re-enhance (patch also catches) + highlight recent activity nodes for live feel.
                    setTimeout(() => {
                        if (typeof window.enhanceAgentBubbles === 'function') window.enhanceAgentBubbles();
                        if (typeof window.highlightRecentGraphActivity === 'function') window.highlightRecentGraphActivity();
                    }, 95);
                } catch (e) {}
            }, 70);
        }
    }

    function toggleSidebar() {
        sidebarCollapsed = !sidebarCollapsed;
        localStorage.setItem('cf-sidebar-collapsed', sidebarCollapsed);
        hasManualSidebarPref = true;
        applySidebarState();
    }

    function expandSidebar() {
        if (sidebarCollapsed) {
            sidebarCollapsed = false;
            localStorage.setItem('cf-sidebar-collapsed', 'false');
            hasManualSidebarPref = true;
            applySidebarState();
        }
    }

    function updateActiveNav(name) {
        currentSection = name;
        document.querySelectorAll('#sidebar-nav .nav-item').forEach(item => {
            const isActive = item.dataset.section === name;
            if (isActive) {
                item.classList.add('bg-indigo-600', 'text-white');
                item.classList.remove('hover:bg-zinc-800', 'text-zinc-300');
            } else {
                item.classList.remove('bg-indigo-600', 'text-white');
                item.classList.add('hover:bg-zinc-800', 'text-zinc-300');
            }
        });
    }

    // Bootstrap sidebar state + active nav (the var-driven applySidebarState makes this bulletproof)
    function initSidebar() {
        setTimeout(() => {
            applySidebarState();
            updateActiveNav(currentSection);
        }, 40);
    }

    function showSection(name) {
        document.querySelectorAll('.demo-section').forEach(s => s.classList.add('hidden'));
        const el = document.getElementById('section-' + name);
        if (el) el.classList.remove('hidden');

        updateActiveNav(name);

        if (name === 'agents') {
            // Agents tab: no longer forces sidebar closed (per user: "fix that now so it says open by default again").
            // Previously programmed to default closed during earlier issues; now consistent open-by-default for all pages/tabs until manual close.
            // Framework-native re-create: real AgentCanvas (seeded with update_agent_status/add_event in app.py).
            // Call bubble enhancer (rounds nodes, pulses active ones via CSS+post-process + NEW live hooks/bursts/paths) so it looks close to the
            // old canvas "bubble rendition" while being 100% buildable with the framework (no standalone code).
            if (typeof window.enhanceAgentBubbles === 'function') {
                setTimeout(() => window.enhanceAgentBubbles(), 90);
            }
            // Re-enhance shortly after possible mermaid re-runs (sidebar etc). Also explicitly wire highlightRecent for 'just switched to live swarm' activity pop on nodes.
            setTimeout(() => {
                if (typeof window.enhanceAgentBubbles === 'function') window.enhanceAgentBubbles();
                if (typeof window.highlightRecentGraphActivity === 'function') window.highlightRecentGraphActivity();
            }, 380);
        }

        if (name === 'grok') {
            // Boot / refresh the brand new pure JS GrokChat demo viz (GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk;
            // completely different implementation, no live component). Ensures pre-seeded state + any demo controls ready
            // when tab activates (scroll lands on title first, then demo).
            if (typeof window.initGrokDemoViz === 'function') {
                setTimeout(() => window.initGrokDemoViz(), 30);
            }
        }

        // Ensure sidebar stays open for all tabs/pages (incl agents) until the *user* has manually closed it at least once.
        // (No more special close for agents.)
        if (!hasManualSidebarPref) {
            sidebarCollapsed = false;
            if (typeof applySidebarState === 'function') {
                applySidebarState();
            }
        }

        // Always scroll all the way up when opening a tab (so each page "starts" at the very top under the fixed topbar).
        // Previous offset/scrollIntoView + scrollBy was landing a little low from prior experiments.
        window.scrollTo({ top: 0, behavior: 'instant' });
    }

    // === EARLY CORE WIRING (restores nav/demos after complex graph polish) ===
    // Assign window.* and the data-section delegation *immediately* after basic functions are defined.
    // This guarantees sidebar nav, jump buttons, hero CTAs, and toggle work even if later
    // enhanceAgentBubbles / highlight / grok IIFE (the big visual polish added for the "live collab chart" upgrade)
    // has any runtime or (future) syntax issues. Core interactivity must never regress.
    // Delegation uses capture:true so it reliably intercepts before other listeners.
    // Also do an immediate (sync) bootstrap of initial visible section + sidebar so the page
    // is usable even if the 'load' listener timing is marginal (script at end of body).
    window.showSection = showSection;
    window.toggleSidebar = toggleSidebar;
    window.expandSidebar = expandSidebar;

    // Early delegation for all [data-section] (sidebar links + "Jump to other demos" on every tab).
    (function(){
        if (window.__cfNavDelegated) return;
        window.__cfNavDelegated = true;
        document.addEventListener('click', function(ev){
            const t = ev.target.closest('[data-section]');
            if(t){
                const sec = t.getAttribute('data-section');
                if(sec && typeof window.showSection === 'function') window.showSection(sec);
                if(t.tagName === 'A' || t.tagName === 'BUTTON') ev.preventDefault();
            }
        }, true);
    })();

    // Immediate (non-load) initial paint bootstrap: show overview, init sidebar var state.
    // Defensive against load timing + ensures user sees content + working buttons on open.
    (function(){
        try {
            document.querySelectorAll('.demo-section').forEach(s => s.classList.add('hidden'));
            const o = document.getElementById('section-overview');
            if (o) o.classList.remove('hidden');
            else {
                const first = document.querySelector('.demo-section');
                if (first) first.classList.remove('hidden');
            }
            if (typeof initSidebar === 'function') initSidebar();
            // One early apply for the CSS var (in case init's timeout is slow)
            if (typeof applySidebarState === 'function') applySidebarState();
        } catch(e) {}
    })();

    function bumpDemoUsers() {
        const el = document.getElementById('kpi-users');
        if (!el) return;
        let v = parseInt(el.textContent);
        v += 17;
        el.textContent = v;
        const t = document.createElement('div');
        t.className = 'fixed bottom-6 right-6 bg-emerald-600 text-white px-5 py-3 rounded-2xl text-sm z-[999]';
        t.textContent = '+17 users recorded on server';
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2200);
    }
    
    function logDemoSale() {
        alert('Enterprise sale of $14,200 logged. In a real app this would push a live KPI update.');
    }
    
    function submitDemoForm() {
        const t = document.createElement('div');
        t.className = 'fixed bottom-6 right-6 bg-white text-zinc-950 px-6 py-3 rounded-2xl text-sm shadow z-[999]';
        t.textContent = 'Request submitted to the team.';
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2600);
    }
    
    // Demo for the Live PlotlyChart / pure line chart in the dashboard.
    // THE FIX (user verbatim): "why aren't you making the chart look like a fucking chart.
    // it is literally a chart demo with no chart. make a line chart or something. ...
    // if not then we need to get rid of it and make the chart with our framework. come on team."
    //
    // - When [viz] + plotly present: real PlotlyChart (first-class framework component) with extendTraces etc.
    // - Default (no extra): the _viz_chart_html is now a rich, always-visible, zero-dep SVG line chart
    //   (Acme indigo, Stark emerald, Wayne amber) with grid/axes/legend/markers. Looks like a real chart
    //   on first paint. "make the chart with our framework" — pure, beautiful default, live-mutable.
    // - Mutate & Update (and auto ~580ms after dashboard tab open) visibly extends the lines:
    //   new points arrive on the right, window shifts, polylines + circles update with pop/glow.
    //   Same "Python restyle via live mutation" story as real PlotlyChart / Grok / Agent updates.
    // - One button also drives the DataTable mutations + lower pure bars + log (composition demo).
    window.updateDemoChart = function() {
        const section = document.querySelector('#section-dashboard');
        const plotlyDiv = section ? section.querySelector('.plotly-graph-div') : null;

        if (plotlyDiv && window.Plotly) {
            // Real first-class Plotly path (when clayforge[viz] is installed)
            try {
                const newX = [Date.now() % 100000];
                const newY = [Math.random()*20 + 25, Math.random()*18 + 22, Math.random()*15 + 30];
                Plotly.extendTraces(plotlyDiv, {x: [[newX[0]], [newX[0]], [newX[0]]], y: [ [newY[0]], [newY[1]], [newY[2]] ] }, [0,1,2]);
                Plotly.restyle(plotlyDiv, {
                    'marker.size': [Math.random()*6 + 7],
                    'line.width': [Math.random()*1.5 + 2.5]
                });
                Plotly.relayout(plotlyDiv, {
                    title: 'Live Company Metrics — updated ' + new Date().toLocaleTimeString()
                });
            } catch(e) {
                Plotly.restyle(plotlyDiv, { 'marker.size': [Math.random() * 12 + 6] });
            }
        } else {
            // THE CHART: pure SVG line chart (always present, zero deps, framework-spirit beautiful demo).
            // This is what the user sees by default. It is a real line chart, not an install prompt.
            const svg = section ? section.querySelector('#demo-line-chart') : null;
            if (svg) {
                // Internal live data for the three series (metric space 0-48). Matches the initial
                // visual in the SVG we emitted from app.py. We keep a sliding window of recent points.
                if (!window.__demoLineData) {
                    window.__demoLineData = {
                        acme:  [12,19,15,27,31,34,29],
                        stark: [8,14,22,18,29,35,32],
                        wayne: [5,11,17,24,33,38,36]
                    };
                }
                const data = window.__demoLineData;
                const maxPoints = 9;

                // Push a new "live" observation for each series (small random walk + upward bias = growth feel)
                function pushSeries(arr, bias = 1.6) {
                    const last = arr[arr.length - 1];
                    const delta = (Math.random() - 0.38) * 7.5 + bias;
                    let next = Math.max(4, Math.min(47, Math.round(last + delta)));
                    arr.push(next);
                    if (arr.length > maxPoints) arr.shift();
                    return arr;
                }
                pushSeries(data.acme, 1.8);
                pushSeries(data.stark, 1.4);
                pushSeries(data.wayne, 2.1);

                // Map metric value -> SVG y (30 top padding ... 230 bottom)
                const scaleY = (v) => 230 - (v / 48) * 175;

                // X positions evenly spaced across the chart area (left 70 ... right 520)
                const n = data.acme.length;
                const xFor = (i) => 70 + (i / Math.max(1, n-1)) * (520 - 70);

                // Rebuild the three polylines
                const rebuild = (id, arr, color) => {
                    const poly = svg.querySelector('#' + id);
                    if (!poly) return;
                    let pts = '';
                    for (let i = 0; i < arr.length; i++) {
                        pts += xFor(i) + ',' + scaleY(arr[i]) + ' ';
                    }
                    poly.setAttribute('points', pts.trim());
                    poly.setAttribute('stroke', color);
                };
                rebuild('line-acme', data.acme, '#6366f1');
                rebuild('line-stark', data.stark, '#10b981');
                rebuild('line-wayne', data.wayne, '#f59e0b');

                // Replace the point markers with fresh ones (newest gets the "new-point" pop)
                let ptsGroup = svg.querySelector('#demo-points');
                if (!ptsGroup) {
                    ptsGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                    ptsGroup.id = 'demo-points';
                    svg.appendChild(ptsGroup);
                }
                ptsGroup.innerHTML = '';

                const addPoints = (arr, color) => {
                    for (let i = 0; i < arr.length; i++) {
                        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                        c.setAttribute('cx', xFor(i));
                        c.setAttribute('cy', scaleY(arr[i]));
                        c.setAttribute('r', i === arr.length-1 ? '4.2' : '3.2');
                        c.setAttribute('fill', color);
                        c.setAttribute('stroke', '#0a0a0a');
                        c.setAttribute('stroke-width', '1.5');
                        if (i === arr.length-1) c.classList.add('new-point');
                        ptsGroup.appendChild(c);
                    }
                };
                addPoints(data.acme, '#6366f1');
                addPoints(data.stark, '#10b981');
                addPoints(data.wayne, '#f59e0b');
            }

            // Also drive the liked lower pure bar chart as a secondary visual
            const pureContainer = section ? section.querySelector('#pure-chart-container') : null;
            if (pureContainer) {
                const bars = pureContainer.querySelectorAll('[id^="bar"]');
                bars.forEach((bar) => {
                    const newW = (25 + Math.random()*70) + '%';
                    bar.style.width = newW;
                    const val = bar.parentElement.parentElement.querySelector('[id^="v"]');
                    if (val) val.textContent = Math.round(parseFloat(newW)) + '%';
                });
            }

            // Strong visual reaction on the Live PlotlyChart card itself (the rounded holder)
            const vizHolder = section ? section.querySelector('.clay-card .rounded-3xl.overflow-hidden') : null;
            if (vizHolder) {
                vizHolder.style.transition = 'box-shadow 120ms, background 120ms';
                vizHolder.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.35)';
                setTimeout(() => { if (vizHolder) vizHolder.style.boxShadow = ''; }, 520);
            }
            const card = section ? section.querySelector('.clay-card') : null;
            if (card) {
                card.style.transition = 'box-shadow .2s';
                card.style.boxShadow = '0 0 0 3px rgba(99,102,241,.35)';
                setTimeout(() => { if (card) card.style.boxShadow = ''; }, 420);
            }
        }

        // Always drive the DataTable live mutation from the same action (both Production Viz cards evolve together)
        if (typeof window.updateDemoTable === 'function') {
            setTimeout(window.updateDemoTable, 70);
        }

        // Prominent live glow on the plotly card wrapper
        const plotlyCard = section ? section.querySelector('.clay-card') : null;
        if (plotlyCard) {
            plotlyCard.classList.add('live-viz-card-glow');
            setTimeout(() => { if (plotlyCard) plotlyCard.classList.remove('live-viz-card-glow'); }, 620);
        }

        // Persist a small "last updated" timestamp in the card subtext
        const liveTs = section ? section.querySelector('#live-plotly-ts') : null;
        if (liveTs) liveTs.textContent = '• updated ' + new Date().toLocaleTimeString();

        const toast = document.createElement('div');
        toast.className = 'fixed bottom-6 right-6 bg-indigo-600 text-white px-5 py-3 rounded-2xl text-sm z-[999]';
        toast.textContent = (plotlyDiv && window.Plotly)
            ? 'Live Plotly extended + table mutated (real Python WS-style flow)'
            : 'SVG line chart extended (pure, zero-dep demo — install [viz] for full Plotly)';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2600);
    };

    // Live DataTable mutation (called by the main Mutate button and on dashboard tab start).
    // Bumps ARR values with flash (emerald), occasionally appends a demo new row (slides in, auto-cleans),
    // flashes the table card. This makes the "Live DataTable ... Real Python event handlers" + "Python restyle
    // via live mutation" description visually true and cool. The component already gives working Filter rows...
    // input + clickable sort headers + selectable rows (indigo highlight); we now layer Python-driven data change on top.
    window.updateDemoTable = function() {
        const section = document.querySelector('#section-dashboard');
        if (!section) return;
        // The DataTable renders inside the second .clay-card under the Production Viz grid.
        // Find its tbody (it has id ending -tbody) or any data-row trs.
        let tbody = section.querySelector('tbody[id$="-tbody"]');
        if (!tbody) {
            const cards = section.querySelectorAll('.clay-card');
            if (cards[1]) tbody = cards[1].querySelector('tbody');
        }
        if (!tbody) {
            // graceful: flash the whole table card area
            const tcard = section.querySelectorAll('.clay-card')[1];
            if (tcard) {
                tcard.classList.add('live-viz-card-glow');
                setTimeout(() => tcard && tcard.classList.remove('live-viz-card-glow'), 480);
            }
            return;
        }

        const rows = Array.from(tbody.querySelectorAll('tr[data-row-index]'));
        if (!rows.length) return;

        // Prefer a recognizable company row (Acme / Stark / Wayne / Oscorp) for thematic tie-in with the chart.
        let target = rows.find(r => /Acme|Stark|Wayne|Oscorp/i.test(r.textContent || '')) || rows[Math.floor(Math.random() * rows.length)];

        const tds = target.querySelectorAll('td');
        if (tds.length > 1) {
            // ARR is typically column index 1 (Company, ARR, Stage)
            const arrCell = tds[1];
            let raw = (arrCell.textContent || '').replace(/[^0-9]/g, '');
            let num = parseInt(raw, 10) || 450000;
            const bump = 75000 + Math.floor(Math.random() * 165000);
            num += bump;
            arrCell.textContent = num.toLocaleString();
            arrCell.classList.add('live-cell-update');
            setTimeout(() => { if (arrCell) arrCell.classList.remove('live-cell-update'); }, 920);
        }

        // Occasionally demonstrate "new data from Python" by appending a fresh row (like a new company signal).
        if (Math.random() < 0.38 && rows.length < 8) {
            const newTr = document.createElement('tr');
            newTr.setAttribute('data-row-index', 'live-' + Date.now());
            newTr.className = 'hover:bg-zinc-800/60 transition-colors cursor-pointer live-new-row';
            newTr.innerHTML = '<td class="px-4 py-2.5 text-sm text-zinc-200 border-t border-zinc-800">ForgeAI</td>'
                            + '<td class="px-4 py-2.5 text-sm text-zinc-200 border-t border-zinc-800 tabular-nums">275000</td>'
                            + '<td class="px-4 py-2.5 text-sm text-zinc-200 border-t border-zinc-800">Seed</td>';
            tbody.appendChild(newTr);
            // let it live a while then remove (keeps demo clean, shows transient live growth)
            setTimeout(() => { if (newTr && newTr.parentNode) newTr.parentNode.removeChild(newTr); }, 6200);
        }

        // Card glow for the table card (second under the header)
        const tcard = section.querySelectorAll('.clay-card')[1] || tbody.closest('.clay-card');
        if (tcard) {
            tcard.classList.add('live-viz-card-glow');
            setTimeout(() => { if (tcard) tcard.classList.remove('live-viz-card-glow'); }, 520);
        }
    };

    // (Legacy setShowcaseTheme removed — now unified on applyShowcaseTheme + SHOWCASE_THEME_PRESETS for full fidelity to cf.Theme system)

    function injectAgentThought() {
        const c = document.getElementById('thought-stream');
        if (!c) return;
        const d = document.createElement('div');
        d.className = 'text-emerald-400';
        d.textContent = 'Synthesizer: Combining sources into final report...';
        c.appendChild(d);
        c.scrollTop = 9999;
    }
    
    // Keyboard: Ctrl+B or Cmd+B toggles sidebar from anywhere
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
            e.preventDefault();
            toggleSidebar();
        }
    });

    // Resize listener: re-apply state on window resize / orientation change / screen size shifts.
    // Combined with var-driven CSS, this makes layout behavior bulletproof with zero manual tweaks.
    // Guard with __cfSkipApplyOnNextResize allows safe dispatchEvent(new Event('resize')) from agents mermaid reinit
    // (notifies framework AgentCanvas internals / other listeners of our sidebar-driven content-area
    // width change) WITHOUT causing recursive apply calls or continuous re-scheduling while on agents tab.
    window.addEventListener('resize', () => {
        if (typeof applySidebarState === 'function') {
            if (window.__cfSkipApplyOnNextResize) {
                window.__cfSkipApplyOnNextResize = false;
                return;
            }
            applySidebarState();
        }
    });

    // Boot to overview at the very top + initialize sidebar
    window.addEventListener('load', () => {
        // Show only the overview section first
        document.querySelectorAll('.demo-section').forEach(s => s.classList.add('hidden'));
        const o = document.getElementById('section-overview');
        if (o) o.classList.remove('hidden');

        if (typeof initSidebar === 'function') {
            initSidebar();
        }

        // Force scroll all the way to top on initial load (each "page" opens scrolled to the very top under topbar).
        // Previous changes had it landing a little low.
        setTimeout(() => {
            window.scrollTo({ top: 0, behavior: 'instant' });
        }, 50);

        // Update URL hash for cleanliness
        if (history.replaceState) {
            history.replaceState(null, '', window.location.pathname);
        }
    });

    // ===================================================================
    // SHOWCASE LIVE THEMING — dogfooding the new cf.Theme / set_theme system
    // Instant morph of the full UI (sidebar, cards, text, borders) using CSS vars.
    // Also used by the dedicated Theming section.
    // ===================================================================
    window.SHOWCASE_THEME_PRESETS = {
        default: { mode:'dark', label:'Default', vars:{'--cf-bg':'#0a0a0a','--cf-surface':'#18181b','--cf-surface-2':'#27272a','--cf-border':'#3f3f46','--cf-text':'#e4e4e7','--cf-text-muted':'#a1a1aa','--cf-primary':'#6366f1','--cf-accent':'#10b981'} },
        light:   { mode:'light', label:'Light', vars:{'--cf-bg':'#fafafa','--cf-surface':'#fff','--cf-surface-2':'#f4f4f5','--cf-border':'#e4e4e7','--cf-text':'#18181b','--cf-text-muted':'#52525b','--cf-primary':'#4f46e5','--cf-accent':'#0ea47a'} },
        ocean:   { mode:'dark', label:'Ocean', vars:{'--cf-bg':'#0b1120','--cf-surface':'#0f172a','--cf-surface-2':'#1e2937','--cf-border':'#334155','--cf-text':'#e0f2fe','--cf-text-muted':'#64748b','--cf-primary':'#38bdf8','--cf-accent':'#22d3ee'} },
        forest:  { mode:'dark', label:'Forest', vars:{'--cf-bg':'#0a120f','--cf-surface':'#111c18','--cf-surface-2':'#1a2a24','--cf-border':'#2d443b','--cf-text':'#d1fae5','--cf-text-muted':'#4b5563','--cf-primary':'#34d399','--cf-accent':'#10b981'} },
        sunset:  { mode:'dark', label:'Sunset', vars:{'--cf-bg':'#1a120f','--cf-surface':'#2a1f18','--cf-surface-2':'#3f2a20','--cf-border':'#5c4033','--cf-text':'#fed7aa','--cf-text-muted':'#a78b6b','--cf-primary':'#fb923c','--cf-accent':'#f472b6'} }
    };

    window.applyShowcaseTheme = function(presetName) {
        const root = document.documentElement;
        const preset = window.SHOWCASE_THEME_PRESETS[presetName] || window.SHOWCASE_THEME_PRESETS.default;
        
        if (preset.mode === 'dark') root.classList.add('dark');
        else root.classList.remove('dark');

        Object.entries(preset.vars).forEach(([k, v]) => root.style.setProperty(k, v));

        // Update sidebar + topbar + main surfaces instantly (they already use some zinc but vars help custom parts)
        const sidebar = document.getElementById('sidebar');
        const topbar = document.getElementById('topbar');
        if (sidebar) sidebar.style.background = preset.vars['--cf-surface'] || '';
        if (topbar) topbar.style.background = (preset.vars['--cf-surface'] || '') + 'f2';

        // Beautiful toast
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-6 right-6 px-6 py-3 rounded-2xl text-sm z-[999] shadow-xl border flex items-center gap-x-2';
        toast.style.background = preset.vars['--cf-surface'] || '#18181b';
        toast.style.color = preset.vars['--cf-text'] || '#e4e4e7';
        toast.style.borderColor = preset.vars['--cf-border'] || '#3f3f46';
        toast.innerHTML = `<i class="fa-solid fa-palette"></i> <span>Theme: <strong>${preset.label}</strong></span>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1600);

        // Gentle highlight on theme-sensitive cards if present in the theming section
        document.querySelectorAll('#section-theming .bg-zinc-900').forEach(el => {
            el.style.transitionDuration = '120ms';
            el.style.boxShadow = `0 0 0 1px ${preset.vars['--cf-primary'] || '#6366f1'}30`;
            setTimeout(() => { el.style.boxShadow = ''; }, 650);
        });
    };

    // Make "T" key cycle themes anywhere in the showcase (delightful easter egg)
    let scThemeOrder = ['default','light','ocean','forest','sunset'];
    let scIdx = 0;
    document.addEventListener('keydown', function(e){
        if (e.key.toLowerCase()==='t' && document.activeElement.tagName==='BODY') {
            e.preventDefault();
            scIdx = (scIdx + 1) % scThemeOrder.length;
            window.applyShowcaseTheme(scThemeOrder[scIdx]);
        }
    });

    // Live CSS var inspector for the Theming section — clearly demonstrates the CSS custom properties system
    window.refreshThemeInspector = function() {
        const container = document.getElementById('theme-inspector');
        if (!container) return;
        const rootStyles = getComputedStyle(document.documentElement);
        const keys = ['--cf-bg', '--cf-surface', '--cf-surface-2', '--cf-border', '--cf-text', '--cf-text-muted', '--cf-primary', '--cf-accent'];
        container.innerHTML = keys.map(k => {
            const val = rootStyles.getPropertyValue(k).trim() || '(default)';
            return `<div class="flex items-center justify-between gap-2 px-3 py-1.5 bg-zinc-950 border border-zinc-800 rounded-xl"><span class="text-zinc-400">${k}</span><span class="font-semibold text-emerald-400 tabular-nums">${val}</span></div>`;
        }).join('');
    };

    // Auto refresh inspector when applying theme or when theming section becomes visible
    const origApply = window.applyShowcaseTheme;
    window.applyShowcaseTheme = function(name) {
        origApply(name);
        setTimeout(() => window.refreshThemeInspector(), 80);
    };

    // Explicit exposure (in case not set earlier)
    window.showSection = showSection;
    window.toggleSidebar = toggleSidebar;
    window.expandSidebar = expandSidebar;
    window.bumpDemoUsers = bumpDemoUsers;
    window.logDemoSale = logDemoSale;
    window.submitDemoForm = submitDemoForm;

    // Framework-native bubble enhancer for the real AgentCanvas Research Swarm (agents tab only).
    // Post-processes the live mermaid SVG (produced by the real component) to make nodes rounded "bubbles"
    // and pulse/glow the active ones (thick stroke from component for non-idle + status words in label; now also
    // catches dynamically spawned agents like FactChecker/Visualizer from the long demo).
    // UPGRADED for 'hell yeah' real-time agentic team: 
    // - mermaid.run patch + MutationObserver for auto re-enhance on every live WS re-render / status change / spawn (re-render hooks)
    // - Always-flowing dashed edges + stronger cyan pulse on active handoffs
    // - Jitter + multi-anim pulse via CSS classes for organic alive nodes (beyond basic scale)
    // - Burst flash on tool events / spawns / status transitions (temp .burst class + timeout)
    // - Better working/recent detection: node status label + cross-ref recent entries in .agent-thoughts stream (for 'just acted' .recent)
    // - Adds .active / .recent / .burst to <g.node> so showcase CSS keyframes (pulse + jitter + burst + recent ring) apply beautifully
    // This + the CSS in get_showcase_styles() makes the graph the star of the bad-ass demo while 100% using real AgentCanvas + public API.
    // Called from showSection('agents') + after sidebar mermaid reinit. Live during orchestration thanks to hooks.
    window.enhanceAgentBubbles = function() {
        const root = document.getElementById('section-agents');
        if (!root) return;
        const svg = root.querySelector('.mermaid svg');
        if (!svg) return;
        try {
            // === LIVE RE-RENDER HOOKS (addresses issue where core _refresh_mermaid_and_scroll only does run, no enhance) ===
            // 1. Patch mermaid.run once: every diagram re-render (live updates, sidebar apply, dynamic spawn) will auto-trigger enhance when agents tab visible.
            if (!window.__cfAgentMermaidPatched) {
                window.__cfAgentMermaidPatched = true;
                const _origRun = (window.mermaid && window.mermaid.run) || null;
                if (_origRun && typeof _origRun === 'function') {
                    window.mermaid.run = function(opts) {
                        const res = _origRun.apply(this, arguments);
                        setTimeout(() => {
                            const ael = document.getElementById('section-agents');
                            if (ael && !ael.classList.contains('hidden') && typeof window.enhanceAgentBubbles === 'function') {
                                window.enhanceAgentBubbles();
                            }
                        }, 55);
                        return res;
                    };
                }
            }
            // 2. MutationObserver (safety net for full innerHTML swaps from WS to_html + any pre changes): debounce re-enhance on subtree changes when tab open.
            if (!window.__cfAgentObs && typeof MutationObserver === 'function') {
                window.__cfAgentObs = true;
                try {
                    const mo = new MutationObserver((muts) => {
                        const ael = document.getElementById('section-agents');
                        if (ael && !ael.classList.contains('hidden')) {
                            // only if mermaid svg present or changed
                            if (ael.querySelector('.mermaid svg')) {
                                setTimeout(() => { if (typeof window.enhanceAgentBubbles === 'function') window.enhanceAgentBubbles(); }, 25);
                            }
                        }
                    });
                    // Observe the section (survives; broad but cheap + guarded)
                    mo.observe(root, { childList: true, subtree: true, attributes: false });
                } catch (e) {}
            }

            // === BETTER DETECTION: working agents from node labels (status injected by component) + recent activity from live thought stream ===
            const thoughtsEl = root.querySelector('.agent-thoughts');
            const recentAgents = new Set();
            if (thoughtsEl) {
                // Grab recent agent mentions from last few thought lines (names are bolded or start of text)
                const recentEls = Array.from(thoughtsEl.querySelectorAll('*')).slice(-8);
                recentEls.forEach(el => {
                    const t = (el.textContent || '').trim();
                    // Match common "AgentName ..." or "AgentName: ..." or tool lines with agent
                    const m = t.match(/^([A-Za-z][A-Za-z0-9_-]{2,})\b/);
                    if (m && m[1].length < 18) recentAgents.add(m[1].toLowerCase());
                });
            }

            const activeNodes = new Set();
            let justSpawnedOrTool = false;

            // === PARSE CORE ACTIVITY DATA (recent_activity + color per agent from agent_states) for color-tied effects ===
            let activityData = {};
            try {
                const actContainer = root.querySelector('[data-agent-activity]') || svg.parentNode;
                const actStr = actContainer ? actContainer.getAttribute('data-agent-activity') : null;
                if (actStr) {
                    activityData = JSON.parse(actStr.replace(/&quot;/g, '"'));
                }
            } catch (e) {}

            // Nodes: round bubbles, classes for CSS magic, bursts on tool/spawn, recent from stream
            svg.querySelectorAll('.node').forEach(n => {
                const fullTxt = (n.textContent || '').trim();
                const txt = fullTxt.toLowerCase();
                // name from first line (before br or nl)
                const namePartRaw = fullTxt.split(String.fromCharCode(60))[0].split(String.fromCharCode(10))[0].trim();
                const namePart = namePartRaw.toLowerCase();
                if (namePart) activeNodes.add(namePart);

                const hasStatus = /thinking|researching|tool|critiq|synth|synthesiz|complete/.test(txt);
                const isWorking = hasStatus || /tool|spawn|fact|visual|publish/.test(txt) || recentAgents.has(namePart);
                const isToolish = /tool|spawn|cross|chart|report|verify|fetch/.test(txt) || recentAgents.has(namePart) && txt.includes('tool');

                // Generalized for richer mermaid shapes from core upgrade (rect for rounded/stadium, polygon for diamonds/critique, circle/ellipse possible for hubs)
                // rx/ry only for rects; classes always added to .node g for CSS keyframes (pulse/jitter/burst/recent) to apply to child shapes.
                const shape = n.querySelector('rect, circle, ellipse, polygon, path');
                if (shape) {
                    if (shape.tagName.toLowerCase() === 'rect') {
                        shape.setAttribute('rx', '18');
                        shape.setAttribute('ry', '18');
                    }
                    // Clear inline so CSS .node.active etc fully drive (supports varied shapes + core classDef active)
                    shape.style.animation = '';
                    shape.style.filter = '';

                    n.classList.remove('active', 'recent', 'burst');

                    if (isWorking) {
                        n.classList.add('active');
                    }
                    if (recentAgents.has(namePart)) {
                        n.classList.add('recent');
                    }
                    if (isToolish) {
                        justSpawnedOrTool = true;
                        n.classList.add('burst');
                        setTimeout(() => {
                            if (n && n.classList) n.classList.remove('burst');
                        }, 860);
                    }
                } else {
                    // Fallback: still tag .node for CSS even if no shape child found (defensive for future mermaid)
                    n.classList.remove('active', 'recent', 'burst');
                    if (isWorking) n.classList.add('active');
                    if (recentAgents.has(namePart)) n.classList.add('recent');
                }
            });

            // === ADD SVG RINGS + PARTICLES + COLOR-MORPH FLASH (per task: via added SVG elements on re-render; color tied to agent; synced to activity) ===
            // Clean prior particles/rings (from last enhance after mermaid re-render)
            svg.querySelectorAll('.thinking-ring, .ai-particle').forEach(el => el.parentNode && el.parentNode.removeChild(el));
            svg.querySelectorAll('.node').forEach(n => {
                const fullTxt = (n.textContent || '').trim();
                const namePartRaw = fullTxt.split(String.fromCharCode(60))[0].split(String.fromCharCode(10))[0].trim();
                const lowerName = namePartRaw.toLowerCase();
                const actInfo = activityData[namePartRaw] || activityData[Object.keys(activityData).find(k => k.toLowerCase() === lowerName)] || {};
                const actType = String(actInfo.activity || actInfo.status || '').toLowerCase();
                const agentColor = actInfo.color || '#64748b';
                const isThinking = /thinking|researching/.test(fullTxt.toLowerCase()) || actType.includes('think') || actType === 'thought';
                const isHot = n.classList.contains('active') || n.classList.contains('recent') || actType === 'tool' || actType === 'spawn' || isThinking;
                const shapeEl = n.querySelector('rect, circle, ellipse, polygon');
                if (!shapeEl || !isHot) return;

                let cx = 28, cy = 18, rBase = 20;
                try {
                    const bb = (n.getBBox && n.getBBox()) || (shapeEl.getBBox && shapeEl.getBBox()) || {x:10,y:8,width:36,height:22};
                    cx = bb.x + bb.width / 2;
                    cy = bb.y + bb.height / 2;
                    rBase = Math.max(16, Math.min(bb.width, bb.height) / 2 + 3);
                } catch (e) {}

                const ns = 'http://www.w3.org/2000/svg';
                if (isThinking || actType === 'thought' || actType.includes('research')) {
                    // Thinking ring: expanding aura using agent's color
                    const ring = document.createElementNS(ns, 'circle');
                    ring.setAttribute('class', 'thinking-ring');
                    ring.setAttribute('cx', cx);
                    ring.setAttribute('cy', cy);
                    ring.setAttribute('r', (rBase + 5).toFixed(1));
                    ring.setAttribute('style', `color:${agentColor};`);
                    n.appendChild(ring);
                }
                // Particles for active/tool/spawn/thinking: floating dots, color-morph from agent, staggered, auto-clean
                if (isHot) {
                    const pdirs = [[4.5,-5.5],[-6.5,3.5],[5.5,4],[-3.5,-6]];
                    for (let i = 0; i < 4; i++) {
                        const p = document.createElementNS(ns, 'circle');
                        p.setAttribute('class', `ai-particle p${(i % 3) + 1}`);
                        p.setAttribute('cx', (cx + (i - 1.5) * 1.8).toFixed(1));
                        p.setAttribute('cy', (cy + ((i % 2) ? -1.8 : 1.8)).toFixed(1));
                        p.setAttribute('r', '1.65');
                        p.setAttribute('fill', agentColor);
                        p.style.setProperty('--dx', pdirs[i][0] + 'px');
                        p.style.setProperty('--dy', pdirs[i][1] + 'px');
                        n.appendChild(p);
                        setTimeout(() => { try { if (p && p.parentNode) p.parentNode.removeChild(p); } catch(_) {} }, 920);
                    }
                }
                // Status change flash / color morph tied to this agent's color (on tool/spawn/recent/burst)
                if (actType === 'tool' || actType === 'spawn' || n.classList.contains('burst') || n.classList.contains('recent')) {
                    n.classList.add('flash');
                    n.style.setProperty('--flash-color', agentColor);
                    setTimeout(() => {
                        if (n && n.classList) {
                            n.classList.remove('flash');
                            n.style.removeProperty('--flash-color');
                        }
                    }, 480);
                }
            });

            // === PATHS: always give the graph a subtle alive flow (dash anim); intensify + color for active/recent handoff edges ===
            svg.querySelectorAll('.edgePath').forEach(edge => {
                const edgeTxt = (edge.textContent || '').toLowerCase();
                const path = edge.querySelector('path');
                if (!path) return;

                // Base alive collaboration flow (always on for 'the team is working' feel)
                path.style.strokeDasharray = '9 5';
                path.style.animation = 'cf-edge-flow 1.65s linear infinite';

                const isHotEdge = Array.from(activeNodes).some(a => edgeTxt.includes(a)) ||
                                  Array.from(recentAgents).some(r => edgeTxt.includes(r));

                if (isHotEdge) {
                    edge.classList.add('active');
                    path.style.stroke = '#67e8f9';
                    path.style.strokeWidth = '2.8';
                } else {
                    edge.classList.remove('active');
                    // let base CSS or mermaid style take over for non-hot
                    path.style.stroke = '';
                    path.style.strokeWidth = '';
                }
            });

            // Arrowheads follow the hot edges
            svg.querySelectorAll('.arrowheadPath').forEach(ah => {
                const parentEdge = ah.closest('.edgePath');
                if (parentEdge && parentEdge.classList.contains('active')) {
                    ah.style.fill = '#67e8f9';
                    ah.style.filter = 'drop-shadow(0 0 2.5px rgba(103,232,249,0.7))';
                } else {
                    ah.style.fill = '';
                    ah.style.filter = '';
                }
            });

            // Final pass: ensure CSS-driven jitter/pulse on actives (some browsers need re-touch)
            // (CSS @keyframes now handle the rich multi-anim jitter + pulse; we just ensure classes)
            // Generalized: no assume rect (supports diamond polygons etc from upgraded core mermaid)
            svg.querySelectorAll('.node.active').forEach(n => {
                const sh = n.querySelector('rect, circle, ellipse, polygon');
                if (sh) {
                    // no inline anim here - CSS rules for .node.active * win (see styles below)
                }
            });
        } catch (e) {}
    };

    // Helper: highlight recent activity nodes explicitly (e.g. called from showSection on agents tab enter for 'just landed on live swarm' pop)
    window.highlightRecentGraphActivity = function() {
        const root = document.getElementById('section-agents');
        if (!root) return;
        const svg = root.querySelector('.mermaid svg');
        if (!svg) return;
        try {
            const thoughtsEl = root.querySelector('.agent-thoughts');
            const recents = new Set();
            if (thoughtsEl) {
                Array.from(thoughtsEl.querySelectorAll('*')).slice(-5).forEach(el => {
                    const m = (el.textContent || '').match(/^([A-Za-z][A-Za-z0-9_-]{2,})\b/);
                    if (m) recents.add(m[1].toLowerCase());
                });
            }
            svg.querySelectorAll('.node').forEach(n => {
                const nm = (n.textContent || '').split(String.fromCharCode(60))[0].split(String.fromCharCode(10))[0].trim().toLowerCase();
                const rect = n.querySelector('rect');
                if (recents.has(nm) && rect) {
                    n.classList.add('recent');
                    // flash a stronger one-shot burst on recent highlight
                    rect.style.transition = 'filter 80ms';
                    rect.style.filter = 'drop-shadow(0 0 18px rgba(52,211,153,0.75))';
                    setTimeout(() => {
                        if (rect) {
                            rect.style.filter = '';
                            setTimeout(() => { if (n) n.classList.remove('recent'); }, 1400);
                        }
                    }, 420);
                }
            });
        } catch (e) {}
    };

    // (Pure standalone canvas swarm viz removed — Agent Vision tab now uses the *real* AgentCanvas component embed from the framework.
    // Framework-native re-create (this run): showcase demonstrates its own primitives. Real mermaid + pills + tool cards
    // driven by public API (update_agent_status / add_event per examples/04 + app.py seed). Bubble rendition polish (rounded
    // pulsing nodes + card lift) added via CSS + enhanceAgentBubbles() so it looks close to the cool prior canvas while
    // being 100% buildable with ClayForge (no more "not even buildable with our framework" standalone tab).
    // Mermaid reinit on sidebar resize lives in applySidebarState. enhanceAgentBubbles called on show + after re-runs.
    // Old pure JS/canvas RAF + initSwarmViz cleaned.)

    // ===================================================================
    // BRAND NEW GrokChat visual demo for the dedicated Grok tab ONLY.
    // GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk.
    // Completely different programming from the real GrokChat Element (src/clayforge/grok/components.py):
    // - No dataclass, no messages state in Python, no to_html, no _push_update, no WS, no sub-Elements.
    // - Pure vanilla JS + DOM: transcript array, appendBubble(), typewriter via setTimeout, toolCard pop-in with CSS.
    // - Better looking + demo functions for visuals (user request): pre-seeded nice convo, send simulation,
    //   explicit buttons to trigger "Tool Use Demo", "Long Stream", "Reset". Looks premium, isolated to #section-grok.
    // - This eliminates the "embedded crapbot" risk exactly like the (prior) canvas swarm approach for agents.
    //   The real GrokChat remains 100% for examples/your apps (with real streaming when key provided).
    // initGrokDemoViz called from showSection('grok') and load.
    // ===================================================================
    (function(){
        if (window.__cfGrokDemoInit) return;
        window.__cfGrokDemoInit = true;

        let demoTranscript = []; // local for the viz only
        let demoRunning = false;

        function getMessagesEl() {
            return document.getElementById('grok-demo-messages');
        }

        function appendBubble(role, content, isTool) {
            const container = getMessagesEl();
            if (!container) return;
            const div = document.createElement('div');
            if (role === 'user') {
                div.className = 'flex justify-end';
                div.innerHTML = `
                    <div class="max-w-[78%] group">
                        <div class="bg-indigo-600 text-white px-4 py-2.5 rounded-3xl rounded-br-xl text-[14px] leading-snug shadow-sm grok-demo-bubble">
                            ${content.replace(/</g,'&lt;').replace(/>/g,'&gt;')}
                        </div>
                        <div class="text-right text-[10px] text-zinc-400 mt-1 pr-1 opacity-75 group-hover:opacity-100 transition-opacity">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>
                    </div>`;
            } else if (role === 'tool' || isTool) {
                div.className = 'mx-1 my-0.5';
                div.innerHTML = `
                    <div class="bg-zinc-950 border border-zinc-700 rounded-2xl px-4 py-3 text-sm shadow-inner grok-demo-tool">
                        <div class="flex items-center gap-x-2 text-amber-400 font-medium">
                            <span class="text-base">🔧</span>
                            <span>Using <span class="font-mono text-amber-300">${content.tool || 'tool'}</span></span>
                        </div>
                        <div class="mt-1.5 text-[12px] text-zinc-400 font-mono break-all">${content.args || ''}</div>
                        ${content.result ? `<div class="mt-2 pt-2 border-t border-zinc-700 text-emerald-300/90"><span class="font-medium text-emerald-400">Result:</span><br><span class="font-mono text-xs leading-snug break-words">${content.result}</span></div>` : ''}
                    </div>`;
            } else {
                div.className = 'flex justify-start';
                div.innerHTML = `
                    <div class="max-w-[82%] group">
                        <div class="bg-zinc-800 text-zinc-100 px-4 py-2.5 rounded-3xl rounded-bl-xl text-[14px] leading-snug border border-zinc-700/60 grok-demo-bubble">
                            ${content.replace(/</g,'&lt;').replace(/>/g,'&gt;')}
                        </div>
                        <div class="text-[10px] text-zinc-400 mt-1 pl-1 opacity-75 group-hover:opacity-100 transition-opacity">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>
                    </div>`;
            }
            container.appendChild(div);
            container.scrollTop = 9999;
            return div;
        }

        function typewriterInto(el, text, cb) {
            if (!el) { if(cb) cb(); return; }
            const safeBase = el.innerHTML || '';
            let i = 0;
            const interval = setInterval(() => {
                i++;
                const chunk = text.slice(0, i);
                el.innerHTML = safeBase + chunk.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '<span class="inline-block w-1.5 h-4 align-[-1px] bg-zinc-400 animate-pulse ml-0.5"></span>';
                if (i >= text.length) {
                    clearInterval(interval);
                    el.innerHTML = safeBase + text.replace(/</g,'&lt;').replace(/>/g,'&gt;');
                    if (cb) cb();
                }
            }, 18);
        }

        function updateDemoStatus(msg) {
            const s = document.getElementById('grok-demo-status');
            if (s) s.textContent = msg;
        }

        window.grokDemoSend = function(customText) {
            const container = getMessagesEl();
            if (!container) return;
            const input = document.getElementById('grok-demo-input');
            let text = customText || (input ? input.value.trim() : '');
            if (!text) text = "Tell me about building beautiful AI UIs in pure Python.";
            if (input) input.value = '';

            appendBubble('user', text);
            updateDemoStatus('thinking...');

            // simulate thinking + stream
            setTimeout(() => {
                const assistantWrap = appendBubble('assistant', '');
                if (!assistantWrap) return;
                const contentEl = assistantWrap.querySelector('.grok-demo-bubble');
                const reply = (text.toLowerCase().includes('tool') || text.toLowerCase().includes('search'))
                    ? "Running a quick tool to check the latest patterns... Done. ClayForge + GrokChat gives you exactly this experience with zero boilerplate — real streaming when you wire a key."
                    : "Absolutely — ClayForge makes this trivial. Drop in GrokChat(...) and you get the bubbles, streaming, tool cards, and auto-scroll out of the box. Pure Python, production ready.";
                typewriterInto(contentEl, reply, () => {
                    updateDemoStatus('online');
                    // occasionally auto demo a tool card after certain sends for visual delight
                    if (text.toLowerCase().includes('tool') || Math.random() > 0.7) {
                        setTimeout(() => window.grokDemoTriggerTool(true), 420);
                    }
                });
            }, 260);
        };

        window.grokDemoTriggerTool = function(silent) {
            const container = getMessagesEl();
            if (!container) return;
            appendBubble('tool', {
                tool: 'web_search',
                args: '{"q":"clayforge grokchat demo 2026"}',
                result: 'Top match: beautiful dedicated-tab isolation in showcase. 3 supporting examples found.'
            });
            updateDemoStatus('tool result received');
            if (!silent) {
                // also append a short assistant note
                setTimeout(() => {
                    const w = appendBubble('assistant', '');
                    const c = w ? w.querySelector('.grok-demo-bubble') : null;
                    if (c) typewriterInto(c, "Tool completed. The result is now in context for the next turn.", () => updateDemoStatus('online'));
                }, 380);
            }
        };

        window.grokDemoLongStream = function() {
            const container = getMessagesEl();
            if (!container) return;
            appendBubble('user', 'Give me a detailed walkthrough of a production multi-agent flow.');
            updateDemoStatus('streaming long response...');
            setTimeout(() => {
                const wrap = appendBubble('assistant', '');
                const c = wrap ? wrap.querySelector('.grok-demo-bubble') : null;
                if (!c) return;
                const long = "Step 1: Researcher pulls sources via web_search. Step 2: Parallel Critic reviews for contradictions and quality. Step 3: Synthesizer merges + emits final artifact with citations. All mutations are driven from Python using AgentCanvas + add_event for rich cards, exactly like this demo. GrokChat can steer the team in real time.";
                typewriterInto(c, long, () => updateDemoStatus('online'));
            }, 300);
        };

        window.grokDemoReset = function() {
            const container = getMessagesEl();
            if (container) container.innerHTML = '';
            demoTranscript = [];
            updateDemoStatus('demo ready — try the buttons or type');
            // re-seed a nice starter (includes tool card for beautiful pre-seeded demo conv per spec)
            setTimeout(() => {
                if (container && container.children.length === 0) {
                    appendBubble('assistant', "Hello! I'm Grok — ready to explore, search, code, or just chat. What can I help with?");
                    appendBubble('user', "Show me a beautiful pure-Python UI with live AI.");
                    appendBubble('tool', {tool: 'web_search', args: '{"q":"clayforge grokchat pure python ui 2026"}', result: 'Found ClayForge: zero-boilerplate GrokChat + dedicated showcase tab with pure JS visual demo.'});
                    const w = appendBubble('assistant', '');
                    const ce = w ? w.querySelector('.grok-demo-bubble') : null;
                    if (ce) typewriterInto(ce, "This GrokChat demo (and the real component) makes it trivial. See the controls below for more visual scenarios, or type anything.", ()=>{});
                }
            }, 60);
        };

        window.grokDemoToggleFullScreen = function() {
            const chat = document.querySelector('#section-grok .grok-demo-chat');
            if (!chat) return;
            const isFull = chat.classList.toggle('grok-fs');
            if (isFull) {
                // taller for conversation reading; will be further styled by .grok-fs CSS
                chat.style.height = '75vh';
            } else {
                chat.style.height = '500px';
            }
            // toggle the button label for "back to not full screen"
            const btn = document.getElementById('grok-fs-btn');
            if (btn) {
                btn.textContent = isFull ? 'Exit Fullscreen' : '⛶ Fullscreen';
            }
            // gentle scroll so user sees the expanded area
            setTimeout(() => {
                try { chat.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch(e){}
            }, 50);
        };

        window.initGrokDemoViz = function() {
            const container = getMessagesEl();
            if (!container) return;
            if (container.children.length === 0) {
                window.grokDemoReset();
            }
            // wire the input enter key if present in the viz HTML
            const inp = document.getElementById('grok-demo-input');
            if (inp && !inp._wired) {
                inp._wired = true;
                inp.addEventListener('keydown', function(e){
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        window.grokDemoSend();
                    }
                });
            }
            // ensure FS button starts with correct label
            const btn = document.getElementById('grok-fs-btn');
            if (btn) btn.textContent = '⛶ Fullscreen';
            updateDemoStatus('demo ready — try the buttons or type');
        };

        // auto init on load (harmless)
        window.addEventListener('load', () => setTimeout(() => {
            const c = getMessagesEl();
            if (c) window.initGrokDemoViz();
        }, 140));
    })();

    // Delegation moved early for robustness (see top of scripts). This late block is now a no-op guard (flag already set).
    (function(){ if (window.__cfNavDelegated) return; window.__cfNavDelegated = true; })();

    // Hook into section show for auto init of inspector
    const origShow = window.showSection;
    window.showSection = function(name) {
        origShow(name);
        if (name === 'theming') {
            setTimeout(() => window.refreshThemeInspector && window.refreshThemeInspector(), 120);
        }
    };

    // ------------------------------------------------------------------
    // Dashboard active cool demos wiring (Live Mutation Log + Cross-control)
    // These make the new log stream and cross panel on the Dashboard tab fully functional.
    // The "Live PlotlyChart" active behavior (extend + fallback) is in updateDemoChart above.
    // Seeded on load + when dashboard tab becomes visible.
    // ------------------------------------------------------------------
    (function(){
        function appendLog(msg, kind) {
            const log = document.getElementById('dashboard-log');
            if (!log) return;
            const time = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
            const color = (kind === 'error') ? 'text-red-400' : ((kind === 'tool') ? 'text-amber-400' : 'text-emerald-300');
            const line = document.createElement('div');
            line.className = 'py-px ' + color;
            line.textContent = '[' + time + '] ' + msg;
            log.appendChild(line);
            log.scrollTop = 9999;
            while (log.children.length > 12) log.removeChild(log.firstChild);
        }

        window.emitDashboardEvent = function() {
            const kinds = ['KPI bump', 'viz restyle', 'agent thought', 'form submit', 'tool result'];
            const msg = kinds[Math.floor(Math.random()*kinds.length)] + ' (simulated WS payload)';
            appendLog(msg);

            // lightly drive the pure chart too
            const bars = document.querySelectorAll('#pure-chart-container [id^="bar"]');
            bars.forEach(b => {
                const nw = (30 + Math.random()*55) + '%';
                b.style.width = nw;
                const val = b.parentElement.parentElement.querySelector('[id^="v"]');
                if (val) val.textContent = Math.round(parseFloat(nw)) + '%';
            });
        };

        window.applyCrossControl = function() {
            const metricSel = document.getElementById('cross-metric');
            const deltaIn = document.getElementById('cross-delta');
            if (!metricSel || !deltaIn) return;
            const idx = parseInt(metricSel.value, 10) || 0;
            const delta = parseInt(deltaIn.value, 10) || 0;

            const bar = document.getElementById('bar' + idx);
            const valEl = document.getElementById('v' + idx);
            if (bar && valEl) {
                let cur = parseFloat(bar.style.width) || 50;
                let neu = Math.max(5, Math.min(95, Math.round(cur + delta)));
                bar.style.width = neu + '%';
                valEl.textContent = neu + '%';
            }

            const names = ['CPU','Memory','Disk I/O','Net'];
            appendLog('Cross control: ' + (names[idx]||'Metric') + ' ' + (delta>=0?'+':'') + delta + '%', 'tool');

            const t = document.createElement('div');
            t.className = 'fixed bottom-6 right-6 bg-emerald-600 text-white px-4 py-2 rounded-2xl text-xs z-[999] shadow';
            t.textContent = 'Broadcast: ' + (names[idx]||'Metric') + ' mutated';
            document.body.appendChild(t);
            setTimeout(() => t.remove(), 1600);
        };

        // live slider label
        const deltaIn = document.getElementById('cross-delta');
        const deltaVal = document.getElementById('cross-delta-val');
        if (deltaIn && deltaVal) {
            const sync = () => { deltaVal.textContent = (parseInt(deltaIn.value,10)>=0?'+':'') + deltaIn.value; };
            deltaIn.addEventListener('input', sync);
            sync();
        }

        // seed log when dashboard elements appear (on tab show or initial)
        function seedDashboardDemos() {
            const log = document.getElementById('dashboard-log');
            if (log && log.children.length === 0) {
                appendLog('Dashboard ready — use Emit or Cross control (or other mutate buttons).');
            }
            // also make bump feed the log when we're on dashboard
            const origBump = window.bumpDemoUsers;
            if (typeof origBump === 'function' && !window.__cfBumpWiredForLog) {
                window.__cfBumpWiredForLog = true;
                window.bumpDemoUsers = function() {
                    origBump();
                    if (document.getElementById('dashboard-log')) {
                        appendLog('Users +17 (global KPI mutate)');
                    }
                };
            }
        }

        // run now (if elements already in DOM) and also on section show
        setTimeout(seedDashboardDemos, 60);

        const origShowForDash = window.showSection;
        window.showSection = function(name) {
            origShowForDash(name);
            if (name === 'dashboard') {
                setTimeout(seedDashboardDemos, 30);
                // Auto-trigger one visible live mutation shortly after the tab opens.
                // This delivers "maybe some of it changes when the demo is started" for the
                // Production Viz Components (Live PlotlyChart grows + Live DataTable values flash/add).
                // Delay long enough for section paint + any plotly bootstrap inside the rendered component.
                setTimeout(() => {
                    try {
                        if (typeof window.updateDemoChart === 'function') window.updateDemoChart();
                    } catch (e) {}
                }, 580);
            }
        };
    })();
"""


def render_nav(active: str = "overview") -> str:
    """Generate persistent nav markup. Collapse state handled purely via CSS + #sidebar.collapsed.
    Preserves exact classes and data attrs from the hardened implementation.
    """
    items = [
        ("overview", "Overview", "fa-home"),
        ("theming", "Theming", "fa-palette"),
        ("grok", "GrokChat", "fa-robot"),
        ("dashboard", "Dashboard", "fa-chart-line"),
        ("agents", "Agent Vision", "fa-users-cog"),
        ("forms", "Forms & Tools", "fa-file-invoice"),
    ]
    html = ""
    for key, label, icon in items:
        active_cls = (
            "bg-indigo-600 text-white" if key == active else "hover:bg-zinc-800 text-zinc-300"
        )
        html += f'''
        <a href="#" data-section="{key}"
           class="nav-item flex items-center gap-x-3 px-4 py-2.5 rounded-2xl text-sm font-medium transition-colors {active_cls}">
            <i class="fa-solid {icon} w-4 shrink-0"></i>
            <span class="nav-label">{label}</span>
        </a>'''
    return html


def render_sidebar(nav_html: str) -> str:
    """Exact sidebar markup (including logo, collapse button, nav container).
    Width is now controlled exclusively by the --sidebar-width CSS variable (set by early script + JS).
    This guarantees pixel-perfect sync with main-content padding-left and topbar.
    """
    return f"""<div id="sidebar" class="fixed left-0 top-0 h-screen bg-zinc-950 border-r border-zinc-800 z-50 flex flex-col transition-all duration-300">
            <div class="h-14 px-3 flex items-center justify-center border-b border-zinc-800 relative">
                <div class="sidebar-expanded-only flex items-center gap-x-3 w-full px-1">
                    <div class="w-8 h-8 bg-indigo-600 rounded-2xl flex items-center justify-center shrink-0">
                        <i class="fa-solid fa-layer-group text-white text-lg"></i>
                    </div>
                    <div class="font-display text-xl tracking-tighter font-semibold">clayforge</div>
                </div>
                <div class="hidden sidebar-collapsed-only items-center justify-center">
                    <div class="w-8 h-8 bg-indigo-600 rounded-2xl flex items-center justify-center">
                        <i class="fa-solid fa-layer-group text-white text-lg"></i>
                    </div>
                </div>
                <button onclick="toggleSidebar()" class="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 flex items-center justify-center rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors z-10" title="Toggle sidebar (Ctrl+B)">
                    <i class="fa-solid fa-chevron-left text-xs" id="collapse-icon"></i>
                </button>
            </div>
            <div class="p-3 flex-1 space-y-1 text-sm" id="sidebar-nav">{nav_html}</div>
            <div class="p-3 border-t border-zinc-800 text-[10px] text-zinc-500 sidebar-expanded-only">Pure Python • Live &amp; reactive • <span class="text-indigo-400/80">python -m clayforge showcase</span></div>
        </div>"""


def render_topbar() -> str:
    """Exact topbar markup with title, live badge, menu toggle, reload.
    Left offset now driven purely by --sidebar-width CSS var for perfect sync with sidebar + main content.
    Prominently features the live theme switcher (first-class theming experience).
    """
    return """<div class="fixed top-0 right-0 h-14 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 z-40 flex items-center px-5 justify-between transition-all duration-300" id="topbar">
            <div class="text-sm flex items-center gap-x-3">
                <span class="font-medium text-white">ClayForge Showcase</span>
                <span class="text-[10px] px-2.5 py-px rounded-full bg-zinc-800 border border-zinc-700 text-zinc-400">2026</span>
                <span class="text-[9px] px-1.5 py-px rounded bg-emerald-900/40 text-emerald-300">AI Agents</span>
            </div>
            <div class="flex items-center gap-x-2 text-xs">
                <button onclick="toggleSidebar()" class="px-3 h-7 rounded-2xl border border-zinc-700 hover:bg-zinc-900 flex items-center gap-x-1.5" title="Toggle sidebar (Ctrl/Cmd+B)">
                    <i class="fa-solid fa-bars text-xs"></i>
                    <span>Menu</span>
                </button>

                <!-- Prominent beautiful live theme switcher (dogfooding cf.set_theme / cf.Theme) -->
                <div class="flex items-center gap-x-1 pl-2 border-l border-zinc-800" title="Live theme switcher — transforms the whole UI instantly. Visit Theming section for full demo.">
                    <button onclick="window.applyShowcaseTheme('default')" class="w-3 h-3 rounded border border-zinc-600 hover:scale-125 transition" style="background:#6366f1" title="Default"></button>
                    <button onclick="window.applyShowcaseTheme('light')" class="w-3 h-3 rounded border border-zinc-600 hover:scale-125 transition" style="background:#4f46e5" title="Light"></button>
                    <button onclick="window.applyShowcaseTheme('ocean')" class="w-3 h-3 rounded border border-zinc-600 hover:scale-125 transition" style="background:#38bdf8" title="Ocean"></button>
                    <button onclick="window.applyShowcaseTheme('forest')" class="w-3 h-3 rounded border border-zinc-600 hover:scale-125 transition" style="background:#34d399" title="Forest"></button>
                    <button onclick="window.applyShowcaseTheme('sunset')" class="w-3 h-3 rounded border border-zinc-600 hover:scale-125 transition" style="background:#fb923c" title="Sunset"></button>
                    <a href="#" data-section="theming" class="ml-1 text-[10px] px-2 py-0.5 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 text-zinc-300">Theming</a>
                    <a href="#" onclick="navigator.clipboard.writeText('python -m clayforge showcase').then(() => { const t=document.createElement('div'); t.className='fixed bottom-6 right-6 bg-emerald-600 text-white px-4 py-2 rounded-2xl text-xs z-[999] shadow'; t.innerHTML='Copied! Run <span class=\\'font-mono\\'>python -m clayforge showcase</span>'; document.body.appendChild(t); setTimeout(() => t.remove(), 3800); }); return false" class="ml-1 text-[10px] px-2 py-0.5 rounded-lg bg-zinc-900 border border-emerald-800 hover:bg-emerald-900/60 text-emerald-300" title="Copy showcase command">python -m clayforge showcase</a>
                </div>

                <div class="px-3 py-1 rounded-2xl bg-zinc-900 border border-zinc-800 text-emerald-400 flex items-center gap-x-1.5">
                    <i class="fa-solid fa-broadcast-tower text-xs"></i>
                    <span>Live</span>
                </div>
                <button onclick="window.location.reload()" class="px-3 h-7 rounded-2xl border border-zinc-700 hover:bg-zinc-900 flex items-center gap-x-1.5">
                    <i class="fa-solid fa-redo text-xs"></i>
                </button>
            </div>
        </div>"""


def render_expand_handle() -> str:
    """Exact thin expand affordance bar (visible only in collapsed state via JS).
    Position driven by --sidebar-width var (becomes 4rem when collapsed).
    """
    return """<div id="sidebar-expand-handle" onclick="expandSidebar()" class="hidden fixed top-14 bottom-0 w-2.5 bg-zinc-900/70 hover:bg-indigo-500/30 border-r border-zinc-800/50 cursor-pointer z-[45] flex items-center justify-center" title="Expand sidebar">
            <i class="fa-solid fa-chevron-right text-[10px] text-zinc-300"></i>
        </div>"""


def build_showcase_page(sections_html: str) -> str:
    """Assemble the complete showcase root HTML (styles + full chrome layout + all sections + scripts).

    This is the single entry point used by app.py. It guarantees pixel-perfect fidelity
    with the original monolithic implementation + the hardened var-driven sidebar/main layout
    (no more spacing/overlap issues between collapsible sidebar states).
    """
    nav = render_nav("overview")
    styles = get_showcase_styles()
    sidebar = render_sidebar(nav)
    topbar = render_topbar()
    handle = render_expand_handle()
    scripts = get_showcase_scripts()

    return f"""<style>{styles}</style>

    <!-- Fixed chrome (sidebar, handle, topbar) - positioned relative to viewport -->
    {sidebar}
    {handle}
    {topbar}

    <!-- Adjustable main content area - padding-left matches current sidebar width via --sidebar-width CSS var.
         This + the var-driven sidebar/topbar/handle = zero-overlap, zero-gap, smooth, resize-proof layout.
    -->
    <div id="main-layout" class="transition-all duration-300">
        <div id="main-content">
            {sections_html}
        </div>
    </div>

    <!-- Early sync script: eliminates flash and ensures correct layout BEFORE full paint.
         Sets the single --sidebar-width CSS var (which drives sidebar + topbar + main-content padding + handle).
         This is the foundation of the zero-maintenance polished layout system.
    -->
    <script>
        (function() {{
            try {{
                const hasPref = localStorage.getItem('cf-sidebar-collapsed') !== null;
                const collapsed = hasPref ? (localStorage.getItem('cf-sidebar-collapsed') === 'true') : false;
                const sb = document.getElementById('sidebar');
                const h = document.getElementById('sidebar-expand-handle');

                const val = collapsed ? '0px' : '18rem';
                document.documentElement.style.setProperty('--sidebar-width', val);

                if (sb) {{
                    if (collapsed) {{
                        sb.classList.add('collapsed');
                    }} else {{
                        sb.classList.remove('collapsed');
                    }}
                }}
                if (h) {{
                    if (collapsed) {{
                        h.classList.remove('hidden');
                    }} else {{
                        h.classList.add('hidden');
                    }}
                }}
            }} catch(e) {{}}
        }})();
    </script>

    <script>{scripts}</script>"""


__all__ = [
    "get_showcase_styles",
    "get_showcase_scripts",
    "render_nav",
    "render_sidebar",
    "render_topbar",
    "render_expand_handle",
    "build_showcase_page",
]
