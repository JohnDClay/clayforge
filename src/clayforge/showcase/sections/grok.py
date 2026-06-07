"""
Grok section for the ClayForge Showcase.

GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk.
Brand new completely different GrokChat visual demo (re-created like the canvas Research Swarm for Agent Vision):
- Pure client-side HTML/JS only (typewriter streaming, tool cards, demo trigger buttons for visuals).
- NO live GrokChat Element, NO to_html, NO creation/attach in showcase/app.py, NO embed risk/leak like the old swarm.
- ALWAYS starts with the nice title block + prose first (scroll lands here via showSection).
- Uses normalized containers + pt-8 inner for professional centering and immediate content visibility on tab activate.
- 500px chat height (HTML style + JS restore) for ~10% shrink (user: "a hair too tall", want full convo + bottom buttons visible); bubbles text-[14px] (down 1); composer/demo buttons spacing tightened + messages py-4.
- Typewriter ~18ms/char faster in JS (in layout).
- Includes educational "3 GROK SURFACES" callout + source link to examples/03_grok_chat.py (the real component + streaming).
- The real GrokChat (with api_key real tokens or perfect sim + full public API) is untouched and recommended for your apps.
- Demo functions exposed (window.grokDemoSend, grokDemoTriggerTool, grokDemoLongStream, grokDemoReset) for extra visual delight.
- Gallery removed; the showcase is our showcase.
"""

import textwrap


def render_grok(grok_component=None, real_grok=None, has_real_key: bool = False) -> str:
    """GrokChat tab content.

    render_grok signature kept with optional grok_component param for backward compat in tests (test just instantiates GrokChat for public API check).
    Inside: IGNORE the component (never call .to_html, never interp) and ALWAYS return the new pure demo HTML + prose.
    (The light path is now the only one; heavy path simplified away since showcase no longer passes component.)
    GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk.

    - Always emits proper .demo-section wrapper (no pt-16; layout sets padding-top:0) so showSection('grok') + load logic work. Content visible immediately on activate.
    - Nice titles + explanatory prose FIRST (coordinates with layout 3.5rem + tightened mb-4/mt-3 + 50px GAP for gorgeous breathing + title to top; 500px chat height chosen for ~10% shrink so bottom composer/demo buttons + full convo area visible on tab without extra page scroll).
    - Container normalized to px-6 md:px-8 (like overview) for even professional centering / no off-center regression. max-w-5xl mx-auto + pt-8 inner.
    - The viz is a self-contained better-looking demo (bubbles, composer, typewriter streaming, tool cards, extra demo buttons for visuals).
      Completely different code from the real GrokChat Element (no internal state, no WS, vanilla JS DOM + timeouts). Different classes/ids (grok-demo-*).
    - Bubbles use text-[14px] (down 1 size), messages py-4 (tightened), header py-3 for polish on shrink.
    - Includes educational "3 GROK SURFACES" callout.
    - Uses textwrap.dedent. Sidebar natural (text content). Jumps at bottom.
    - Real GrokChat component in src/clayforge/grok/ is untouched and fully functional for users/examples.
    """
    # Always the new pure demo HTML + prose (grok_component param accepted/ignored for test compat only; no .to_html() path remains here).
    # GrokChat tab now uses brand new pure JS demo viz (completely different, no live component like the swarm fix). No embed risk.
    # This mirrors exactly the swarm un-embed approach so we never have the setback again.
    # The demo is intentionally nicer for first-time visitors + has explicit "demo function for visuals" buttons.
    # Height 500px (HTML+JS) for ~10% shrink per feedback (see buttons+convo visible); text down to [14px]; surrounding spacing tightened for fit.
    # (If a component were passed it would be ignored; real component untouched.)
    return textwrap.dedent("""
<div id="section-grok" class="demo-section hidden">
    <div class="max-w-5xl mx-auto px-6 md:px-8 pt-8">
        <div class="mb-4 pt-2">
            <div class="text-center">
                <div class="text-indigo-400 text-xs tracking-[2px] font-semibold">FIRST-CLASS AI</div>
                <div class="font-display text-4xl tracking-tighter font-semibold mt-1">GrokChat</div>
                <p class="text-zinc-400 mt-2 max-w-2xl mx-auto">The drop-in foundation for AI agent conversations. Real token streaming from Grok (or perfect simulation) with identical beautiful UI. This is the <span class="font-semibold text-indigo-300">exact public API</span> — instantiate with GrokChat(...) then drive live from any Python code.</p>
            </div>
        </div>

        <div class="prose prose-invert max-w-none text-zinc-300 space-y-4 mb-4">
            <p>GrokChat is a production-ready, fully interactive streaming chat component built specifically for AI agent systems. Drop it in and get gorgeous message bubbles, live typewriter streaming, rich tool-call cards, and auto-scroll — zero HTML, zero JS, zero boilerplate.</p>
            <p class="font-medium text-indigo-300">This is the exact public API (your own agents / backends call these from Python):</p>
            <div class="bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs font-mono text-indigo-300/90">
                GrokChat(model="grok-4.3", api_key=..., on_message=...)  # real tokens or perfect sim<br>
                .add_user_message(text) • .add_assistant_message(text) • .add_tool_call(name, args, result)<br>
                .stream_append(chunk) • .flush()
            </div>
            <p class="text-sm">This dedicated tab demonstrates a stunning visual replica (better looking + interactive demo controls). Provide a real key in your own code and you get live Grok streaming + tool results the instant you type. The full multi-instance Command Center experience is in your apps.</p>
            <!-- Small educational 3 Grok surfaces callout -->
            <div class="mt-2 inline-flex items-center gap-x-2 text-[10px] px-3 py-1 rounded-2xl bg-zinc-950 border border-zinc-800 text-zinc-400">
                <span class="font-semibold text-indigo-300/90 tracking-[0.5px]">3 GROK SURFACES</span>
                <span class="text-zinc-600">•</span>
                <span>showcase tab (this visual demo)</span>
                <span class="text-zinc-600">•</span>
                <span>your code (full Command Center + real streaming)</span>
            </div>
        </div>

        <!-- Brand new completely different GrokChat visual demo (pure HTML/JS, no Element, no to_html, no roots).
             Looks premium, different structure/classes from the real component so no guard/ leak issues.
             Includes composer + demo trigger buttons for "better looking" + "demo function for visuals".
             Height tuned to 500px (10% shrink), header py-3 + messages py-4 + tightened mt/mb around block so entire chat (convo scroll area + bottom buttons + demo row) visible on tab activate without page scroll. -->
        <div class="mt-3">
            <div class="mb-1.5 text-center px-0.5 space-y-0.5">
                <div class="uppercase text-[10px] tracking-[1.5px] font-semibold text-indigo-400/90">GrokChat Visual Demo — brand new pure JS (showcase only)</div>
                <div class="text-[10px] text-zinc-500">real GrokChat(...) in examples/03 + your apps (with key for live tokens)</div>
            </div>
            <div class="grok-demo-chat rounded-3xl overflow-hidden shadow-[0_20px_60px_-15px_rgb(0,0,0,0.65)] ring-1 ring-white/5 border border-zinc-800 bg-zinc-950 flex flex-col" style="height: 500px;">
                <!-- Demo header (enhanced vs real for visual pop + demo status; "Grok / grok-4.3" as requested, with extra demo flair; py-3 for compact on 500px shrink) -->
                <div class="flex items-center justify-between px-5 py-3 bg-zinc-950/70 border-b border-zinc-800">
                    <div class="flex items-center gap-x-3">
                        <div class="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 via-violet-500 to-fuchsia-500 flex items-center justify-center shadow-inner ring-1 ring-white/20">
                            <i class="fa-solid fa-robot text-white text-lg"></i>
                        </div>
                        <div>
                            <div class="font-semibold tracking-tighter text-white text-lg leading-none">Grok <span class="text-zinc-600">/</span> <span class="text-emerald-300">grok-4.3</span></div>
                            <div class="text-[10px] font-mono text-zinc-500 tracking-[0.5px] mt-0.5">SHOWCASE VISUAL DEMO</div>
                        </div>
                    </div>
                    <div class="flex items-center gap-x-2">
                        <div id="grok-demo-status" class="inline-flex items-center gap-x-1.5 px-3 py-1 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium tracking-wider">demo ready — try the buttons or type</div>
                        <button id="grok-fs-btn" onclick="window.grokDemoToggleFullScreen &amp;&amp; window.grokDemoToggleFullScreen()" class="ml-1 text-[10px] px-2 py-0.5 rounded-lg border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition" title="Toggle fullscreen for better conversation view">⛶ Fullscreen</button>
                    </div>
                </div>

                <!-- Scrollable messages (pre-seeded beautiful demo conv with tool card for instant visuals on paint; JS can reset/append more. Different class names from real component for isolation: grok-demo-*) -->
                <div id="grok-demo-messages"
                     class="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-[radial-gradient(#27272a_0.8px,transparent_1px)] bg-[length:3px_3px] custom-scroll"
                     style="scroll-behavior: smooth;">
                    <!-- Pre-seeded starter (static for beauty before JS init; includes tool card as requested) -->
                    <div class="flex justify-start">
                        <div class="max-w-[82%] group">
                            <div class="bg-zinc-800 text-zinc-100 px-4 py-2.5 rounded-3xl rounded-bl-xl text-[14px] leading-snug border border-zinc-700/60 grok-demo-bubble">
                                Hello! I'm Grok — ready to explore, search, code, or just chat. What can I help with?
                            </div>
                            <div class="text-[10px] text-zinc-400 mt-1 pl-1 opacity-75 group-hover:opacity-100 transition-opacity">14:02</div>
                        </div>
                    </div>
                    <div class="flex justify-end">
                        <div class="max-w-[78%] group">
                            <div class="bg-indigo-600 text-white px-4 py-2.5 rounded-3xl rounded-br-xl text-[14px] leading-snug shadow-sm grok-demo-bubble">
                                Show me a pure-Python reactive UI with live Grok streaming and tool cards.
                            </div>
                            <div class="text-right text-[10px] text-zinc-400 mt-1 pr-1 opacity-75 group-hover:opacity-100 transition-opacity">14:02</div>
                        </div>
                    </div>
                    <div class="mx-1 my-0.5">
                        <div class="bg-zinc-950 border border-zinc-700 rounded-2xl px-4 py-3 text-sm shadow-inner grok-demo-tool">
                            <div class="flex items-center gap-x-2 text-amber-400 font-medium">
                                <span class="text-base">🔧</span>
                                <span>Using <span class="font-mono text-amber-300">web_search</span></span>
                            </div>
                            <div class="mt-1.5 text-[12px] text-zinc-400 font-mono break-all">{"q": "clayforge grokchat pure python ui 2026"}</div>
                            <div class="mt-2 pt-2 border-t border-zinc-700 text-emerald-300/90">
                                <span class="font-medium text-emerald-400">Result:</span><br>
                                <span class="font-mono text-xs leading-snug break-words">Found ClayForge: zero-boilerplate GrokChat + dedicated showcase tab with pure JS visual demo.</span>
                            </div>
                        </div>
                    </div>
                    <div class="flex justify-start">
                        <div class="max-w-[82%] group">
                            <div class="bg-zinc-800 text-zinc-100 px-4 py-2.5 rounded-3xl rounded-bl-xl text-[14px] leading-snug border border-zinc-700/60 grok-demo-bubble">
                                Exactly — the real GrokChat component gives you this in one line of Python (plus streaming when you pass a key). The demo below has more controls.
                            </div>
                            <div class="text-[10px] text-zinc-400 mt-1 pl-1 opacity-75 group-hover:opacity-100 transition-opacity">14:03</div>
                        </div>
                    </div>
                </div>

                <!-- Composer (wired to window.grokDemoSend; enter key supported in JS) -->
                <div class="border-t border-zinc-800 bg-zinc-900 p-3">
                    <div class="flex items-center gap-2">
                        <input id="grok-demo-input" type="text" placeholder="Ask about anything — research, code, ideas..." class="flex-1 bg-zinc-950 border border-zinc-700 focus:border-indigo-500/60 text-sm text-zinc-200 placeholder:text-zinc-500 rounded-3xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 transition-all" />
                        <button onclick="window.grokDemoSend &amp;&amp; window.grokDemoSend()" class="rounded-3xl px-6 font-semibold flex-shrink-0 shadow-sm active:scale-[0.985] transition-all bg-white text-zinc-950 h-11 text-sm">Send</button>
                    </div>
                    <!-- Demo functions for visuals (user request): 4 buttons, typewriter, tool cards etc. -->
                    <div class="mt-1.5 flex flex-wrap gap-2 justify-center">
                        <button onclick="window.grokDemoTriggerTool &amp;&amp; window.grokDemoTriggerTool()" class="px-3 h-7 text-[10px] rounded-2xl border border-amber-600/50 hover:bg-amber-900/20 text-amber-300 active:scale-[0.985] transition">🔧 Simulate Tool Call</button>
                        <button onclick="window.grokDemoLongStream &amp;&amp; window.grokDemoLongStream()" class="px-3 h-7 text-[10px] rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Run Long Streaming Demo</button>
                        <button onclick="window.grokDemoSend &amp;&amp; window.grokDemoSend('Demonstrate a multi-turn exchange with Grok.')" class="px-3 h-7 text-[10px] rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Add Multi-turn Exchange</button>
                        <button onclick="window.grokDemoReset &amp;&amp; window.grokDemoReset()" class="px-3 h-7 text-[10px] rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-400 active:scale-[0.985] transition">Reset Conversation</button>
                    </div>
                    <div class="text-center mt-0.5">
                        <div class="text-[10px] text-zinc-500/70 tracking-tight">This is a visual demo only. Real GrokChat(...) in your code / examples/03_grok_chat.py for streaming + tools.</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-3 text-center text-xs text-zinc-500">
            Full source: <span class="font-mono">examples/03_grok_chat.py</span> • Rich multi-instance + Command Center + real keys in your apps
        </div>

        <!-- Quick cross-nav buttons (plain window.showSection) so every tab has working navigation CTAs like overview.
             Restores the interconnected "new buttons" feel from the beautiful prior version. Click to jump to any surface.
             Uses same professional small pill style; no layout impact on the title breathing or centering. -->
        <div class="mt-4 pt-4 border-t text-center" style="border-color:var(--cf-border);">
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
