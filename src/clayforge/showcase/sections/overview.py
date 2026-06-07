"""
Overview section for the ClayForge Showcase.
"""

from __future__ import annotations

import textwrap


def render_overview() -> str:
    """Returns the FULL section wrapper for Overview (initially visible).
    First-visitor optimized: punchy hero, instant "this is pure Python" proof,
    prominent one-click CTAs for the two best next actions (new + see examples),
    clear value badges, and strong "this could be your app in minutes" messaging.
    Premium polish iteration: titles-first .mb-6, clay-card harmony, cf vars for
    light/dark, upgraded hierarchy/hovers/icons/breathing, subtle delights.
    """
    return textwrap.dedent("""\
<div id="section-overview" class="demo-section">
    <div class="max-w-5xl mx-auto px-6 md:px-8 pt-8 pb-20">  <!-- responsive px + consistent container for symmetrical scrolling + bottom breathing -->
        <div class="mb-6">  <!-- THE VERY FIRST THING inside container after pt- : .mb-6 header block (titles-first). Enforces layout.py guards (.demo-section > div:first-child .mb-6 + #main-content 4.75rem + border nuke) so no top border/hairline, no leaked controls, generous breathing room under topbar. No stray elements before this. -->
            <!-- HERO - even punchier premium typography hierarchy (better sizes/leading/tracking), dual badges, responsive, cf-text for light/dark harmony, gradient pop -->
            <div class="text-center">
                <div class="flex flex-wrap items-center justify-center gap-2 mb-6">
                    <div class="inline-flex items-center gap-x-2 px-4 h-8 rounded-3xl bg-emerald-500/10 text-emerald-400 text-xs font-semibold tracking-[1.5px] transition-colors">
                        <i class="fa-solid fa-bolt"></i>
                        BUILT IN PURE PYTHON
                    </div>
                    <div class="inline-flex items-center gap-x-2 px-4 h-8 rounded-3xl bg-indigo-500/10 text-indigo-400 text-xs font-semibold tracking-[1.5px] transition-colors">
                        <i class="fa-solid fa-magic"></i>
                        REACTIVE BY DEFAULT
                    </div>
                </div>
                <h1 class="font-display text-5xl sm:text-6xl md:text-7xl tracking-[-0.03em] font-semibold leading-[0.9]" style="color:var(--cf-text);">
                    Beautiful AI apps.<br>
                    Zero boilerplate.<br>
                    <span class="bg-gradient-to-r from-indigo-400 via-violet-400 to-emerald-400 bg-clip-text text-transparent">Just Python.</span>
                </h1>
                <p class="mt-6 max-w-3xl mx-auto text-lg sm:text-xl md:text-2xl text-zinc-400" style="color:var(--cf-text-muted);">
                    The 2026 way to ship production-grade reactive interfaces, GrokChat, and live multi-agent systems — all from pure Python. Stunning by default. Reactive by design. Grok-first.
                </p>
            </div>
        </div>

        <!-- Instant "I can do this" CTAs - beautifully spaced (mt-9 + gap-4), micro-interactions (scale, icon transforms), consistent with clay-card language (added clay-card for lift/transition base + ring/shadow), premium h-14 rounded-3xl zinc/indigo harmony -->
        <div class="mt-9 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button data-section="grok"
                    class="group clay-card inline-flex items-center justify-center gap-x-3 px-9 sm:px-10 h-14 rounded-3xl bg-white text-zinc-950 font-semibold text-lg shadow-xl shadow-white/10 ring-1 ring-white/20 hover:bg-zinc-100 hover:shadow-2xl active:scale-[0.985] transition-all duration-200">
                <i class="fa-solid fa-robot group-hover:scale-110 transition-transform"></i>
                <span>See GrokChat in action</span>
            </button>
            <button data-section="agents"
                    class="group clay-card inline-flex items-center justify-center gap-x-3 px-9 sm:px-10 h-14 rounded-3xl border border-emerald-500/60 hover:bg-emerald-900/20 hover:border-emerald-400 text-emerald-300 font-semibold text-lg active:scale-[0.985] transition-all duration-200">
                <i class="fa-solid fa-users-cog group-hover:rotate-12 transition-transform"></i>
                <span>See live Agent Vision</span>
            </button>
        </div>

        <!-- Prominent beautiful quick start pill (command bar style, more delightful + prominent, cf vars for theming harmony) -->
        <div class="mt-5 text-center">
            <div class="inline-flex items-center gap-x-3 px-5 py-2.5 rounded-3xl border border-zinc-700 bg-zinc-950/90 shadow-sm text-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
                <span class="text-zinc-400 font-medium">Quick start:</span>
                <code class="font-mono text-emerald-300 bg-zinc-950 px-3 py-0.5 rounded-2xl text-xs border border-zinc-800" style="background:var(--cf-bg);border-color:var(--cf-border);">clayforge new myapp &amp;&amp; cd myapp &amp;&amp; clayforge run</code>
                <button onclick="(function(){var t=document.createElement('div');t.className='fixed bottom-6 right-6 bg-emerald-600 text-white px-4 py-2 rounded-2xl text-xs z-[999] shadow';t.innerHTML='See examples/ directory for full demos + Command Center patterns';document.body.appendChild(t);setTimeout(function(){t.remove()},3800);})();return false"
                        class="ml-1 text-xs px-3.5 py-1 rounded-2xl border border-emerald-500/50 hover:border-emerald-400 bg-emerald-500/5 hover:bg-emerald-500/15 text-emerald-300 hover:text-emerald-200 transition-all inline-flex items-center gap-x-1.5 font-medium active:scale-[0.985]">
                    <i class="fa-solid fa-play text-[10px]"></i>
                    <span>see examples/</span>
                </button>
            </div>
        </div>

        <!-- Proof badges - upgraded for lift (clay-card + hover:-translate-y-px), hover, icons, consistent padding/rounding/borders (px-5 rounded-3xl), light/dark via cf vars where possible, subtle ring/shadow for premium feel, zinc/indigo -->
        <div class="mt-10 flex flex-wrap justify-center gap-x-3 gap-y-2 text-sm">
            <div class="clay-card px-5 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 flex items-center gap-x-2 transition-all duration-200 hover:-translate-y-px hover:border-emerald-500/40 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);"><i class="fa-solid fa-check text-emerald-400"></i> <span>Zero HTML / CSS / JS</span></div>
            <div class="clay-card px-5 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 flex items-center gap-x-2 transition-all duration-200 hover:-translate-y-px hover:border-emerald-500/40 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);"><i class="fa-solid fa-check text-emerald-400"></i> <span>Real-time WebSocket updates</span></div>
            <div class="clay-card px-5 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 flex items-center gap-x-2 transition-all duration-200 hover:-translate-y-px hover:border-emerald-500/40 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);"><i class="fa-solid fa-check text-emerald-400"></i> <span>First-class Grok + Agents</span></div>
            <div class="clay-card px-5 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 flex items-center gap-x-2 transition-all duration-200 hover:-translate-y-px hover:border-emerald-500/40 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);"><i class="fa-solid fa-check text-emerald-400"></i> <span>Auth + DB in one line</span></div>
            <div class="clay-card px-5 h-8 rounded-3xl bg-zinc-900 border border-zinc-800 flex items-center gap-x-2 transition-all duration-200 hover:-translate-y-px hover:border-emerald-500/40 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);"><i class="fa-solid fa-check text-emerald-400"></i> <span>Live theming &amp; custom components</span></div>
        </div>

        <!-- Structured Live Counter Demo: description above, code snippet, then the interactive demo.
             Buttons now use clean window helpers + initial seed so the demo is immediately live and visible. -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Live Reactive Counter + Event Stream</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">A tiny self-contained reactive UI. Buttons mutate a live counter and append real-time events to a log — exactly the pattern used by @app.api handlers, Grok thoughts, and Agent updates in real ClayForge apps. Zero HTML/CSS/JS in your Python code.</p>
            </div>

            <!-- Code snippet for the counter pattern -->
            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code># Real Python equivalent (the demo below is the live result)
count = 1248
def bump(n=1):
    global count
    count += n
    # In real app: mutate Element state then _push_update() or re-render
    # log.append( f"[{ts}] +{n} users (WS mutation)" )</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <!-- The actual interactive demo -->
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5 ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface);border-color:var(--cf-border);">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                        <div class="font-semibold">Live counter + event stream</div>
                        <div class="text-[11px] text-zinc-400">Click buttons — counter and log update instantly (pure client simulation of WS push).</div>
                    </div>
                    <div class="flex items-center gap-x-2">
                        <button onclick="window.ovBump(1)" class="px-3 h-8 rounded-2xl bg-white text-zinc-950 text-xs font-semibold active:scale-[0.985] flex items-center gap-x-1.5">+1</button>
                        <button onclick="window.ovBump(10)" class="px-3 h-8 rounded-2xl border border-zinc-700 text-xs active:scale-[0.985] flex items-center gap-x-1.5">+10</button>
                        <button onclick="window.ovReset()" class="px-3 h-8 rounded-2xl border border-zinc-700 text-xs active:scale-[0.985]">Reset</button>
                        <button onclick="window.ovGrokUpdate()" class="px-3 h-8 rounded-2xl border border-indigo-500/50 text-xs active:scale-[0.985] flex items-center gap-x-1"><i class="fa-solid fa-robot text-xs"></i><span>Grok update</span></button>
                    </div>
                </div>
                <div class="mt-3 flex items-baseline gap-x-2">
                    <div class="text-xs text-zinc-500">Current:</div>
                    <div id="ov-count" class="font-mono text-3xl font-semibold tabular-nums tracking-tighter" style="color:var(--cf-text);">1248</div>
                    <div class="text-emerald-400 text-xs">users</div>
                </div>
                <div id="ov-log" class="mt-2 max-h-[72px] overflow-auto text-[10px] font-mono bg-black/40 border border-zinc-800 rounded-2xl p-2 text-zinc-400 leading-tight">
                    <div class="text-emerald-300/90">[12:34:56] Server state loaded: 1248 users</div>
                    <div class="text-indigo-300/90">[12:34:57] Grok thought: user growth signal detected</div>
                </div>
                <div class="mt-2 text-[9px] text-center text-zinc-500">Real version: @app.api handler mutates shared state → WS push → UI updates (same as GrokChat thoughts, Agent events, viz mutations).</div>
            </div>
        </div>

        <script>
        (function(){
          if (window.ovBump) return; // guard
          window.ovBump = function(n) {
            var c = document.getElementById('ov-count');
            var l = document.getElementById('ov-log');
            if (!c || !l) return;
            var val = parseInt(c.textContent) || 1248;
            c.textContent = val + n;
            var d = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
            var entry = document.createElement('div');
            entry.className = 'text-emerald-300/90';
            entry.textContent = '[' + d + '] +' + n + ' users (real mutation)';
            l.insertBefore(entry, l.firstChild);
            while (l.children.length > 6) l.removeChild(l.lastChild);
          };
          window.ovReset = function() {
            var c = document.getElementById('ov-count');
            var l = document.getElementById('ov-log');
            if (!c || !l) return;
            c.textContent = '1248';
            var d = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
            l.innerHTML = '<div class="text-zinc-400">[' + d + '] reset to server state</div>';
          };
          window.ovGrokUpdate = function() {
            var l = document.getElementById('ov-log');
            if (!l) return;
            var d = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
            var entry = document.createElement('div');
            entry.className = 'text-indigo-300/90';
            entry.textContent = '[' + d + '] Grok thought: new insight added';
            l.insertBefore(entry, l.firstChild);
            while (l.children.length > 6) l.removeChild(l.lastChild);
          };
          // ensure initial seed is visible even if HTML was minimal
          setTimeout(function(){
            var l = document.getElementById('ov-log');
            if (l && l.children.length < 2) {
              l.innerHTML = '<div class="text-emerald-300/90">[12:34:56] Server state loaded: 1248 users</div><div class="text-indigo-300/90">[12:34:57] Grok thought: user growth signal detected</div>';
            }
          }, 50);
        })();
        </script>

        <!-- Quick nav teasers (Grok + Dashboard) upgraded: icon circles for visual parity with stacked teasers, clay-card + ring-1/shadow-sm for premium lift, cf vars, better hover, consistent p-6/rounded-3xl, colored accents preserved -->
        <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            <button data-section="grok" class="clay-card group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-emerald-500/40 hover:border-emerald-400 rounded-3xl p-6 text-left transition-all duration-200 hover:-translate-y-px ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
                <div class="flex items-center gap-x-4">
                    <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                        <i class="fa-solid fa-robot text-emerald-400 text-xl"></i>
                    </div>
                    <div>
                        <div class="font-semibold text-xl group-hover:text-emerald-400 transition-colors">GrokChat</div>
                        <div class="text-sm text-zinc-400">Real streaming + tool calling UI</div>
                    </div>
                </div>
                <i class="fa-solid fa-arrow-right text-xl text-zinc-600 group-hover:text-emerald-300 group-hover:translate-x-0.5 transition-all"></i>
            </button>
            <button data-section="dashboard" class="clay-card group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-indigo-400/60 rounded-3xl p-6 text-left transition-all duration-200 hover:-translate-y-px ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
                <div class="flex items-center gap-x-4">
                    <div class="w-10 h-10 rounded-2xl bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
                        <i class="fa-solid fa-chart-line text-indigo-400 text-xl"></i>
                    </div>
                    <div>
                        <div class="font-semibold text-xl group-hover:text-indigo-400 transition-colors">Live Dashboard</div>
                        <div class="text-sm text-zinc-400">Real-time KPI updates</div>
                    </div>
                </div>
                <i class="fa-solid fa-arrow-right text-xl text-zinc-600 group-hover:text-indigo-300 group-hover:translate-x-0.5 transition-all"></i>
            </button>
        </div>

        <!-- Teasers for the brand-new first-class features (upgraded clay-card + consistent polish: icon circles, p-6 breathing, mt-4 spacing for better internal flow, ring/shadow lift, cf vars for light/dark, subtle hover delights, no JS breakage) -->
        <div data-section="theming" class="clay-card mt-6 cursor-pointer group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-violet-500/40 hover:border-violet-500/70 rounded-3xl p-6 text-left transition-all duration-200 hover:-translate-y-px ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
            <div class="flex items-center gap-x-4">
                <div class="w-11 h-11 rounded-2xl bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                    <i class="fa-solid fa-palette text-violet-400 text-xl"></i>
                </div>
                <div>
                    <div class="font-semibold text-lg tracking-tight group-hover:text-violet-300 transition-colors">Theming &amp; Custom Components</div>
                    <div class="text-sm text-zinc-400">cf.Theme • set_theme • live CSS vars • custom components that react automatically. Click to explore the full live demo.</div>
                </div>
            </div>
            <i class="fa-solid fa-arrow-right text-xl text-zinc-600 group-hover:text-violet-300 group-hover:translate-x-0.5 transition-all"></i>
        </div>

        <div data-section="forms" class="clay-card mt-4 cursor-pointer group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-indigo-500/50 rounded-3xl p-6 text-left transition-all duration-200 hover:-translate-y-px ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
            <div class="flex items-center gap-x-4">
                <div class="w-11 h-11 rounded-2xl bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
                    <i class="fa-solid fa-key text-indigo-400 text-xl"></i>
                </div>
                <div>
                    <div class="font-semibold text-lg tracking-tight group-hover:text-indigo-300 transition-colors">Auth + Database — first-class</div>
                    <div class="text-sm text-zinc-400">Clean new examples: auth_db_todo.py &amp; internal_crm_with_auth.py • @require_login + Database patterns. Zero-boilerplate production auth.</div>
                </div>
            </div>
            <i class="fa-solid fa-arrow-right text-xl text-zinc-600 group-hover:text-indigo-300 group-hover:translate-x-0.5 transition-all"></i>
        </div>

        <!-- Prominent AI Agents focus (the hero capability) -->
        <div data-section="agents" class="clay-card mt-4 cursor-pointer group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 border border-emerald-500/50 hover:border-emerald-400 rounded-3xl p-6 text-left transition-all duration-200 hover:-translate-y-px ring-1 ring-white/5 shadow-sm" style="background-color:var(--cf-surface); border-color:var(--cf-border);">
            <div class="flex items-center gap-x-4">
                <div class="w-11 h-11 rounded-2xl bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                    <i class="fa-solid fa-robot text-emerald-400 text-xl"></i>
                </div>
                <div>
                    <div class="font-semibold text-lg tracking-tight group-hover:text-emerald-300 transition-colors">AI Agents — Production Ready</div>
                    <div class="text-sm text-zinc-400">Real AgentCanvas + public API (update_agent_status, add_event, dynamic spawns). 3x longer live orchestration with tool cards &amp; beautiful graph. The "hell yeah" agentic experience.</div>
                </div>
            </div>
            <i class="fa-solid fa-arrow-right text-xl text-zinc-600 group-hover:text-emerald-300 group-hover:translate-x-0.5 transition-all"></i>
        </div>

        <!-- NEW EXAMPLE 1: Live Theming Preview (structured: desc + snippet + demo) -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Live Theming Preview</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">ClayForge themes are just CSS custom properties. Change the active theme and a live preview instantly updates its background, borders, text, and accents — exactly what cf.Theme + set_theme() + custom components do in a real app.</p>
            </div>

            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>import clayforge as cf
cf.set_theme(cf.Theme(name="ocean", mode="dark"))
# or per-app: App(theme="forest")
# Components read var(--cf-bg), var(--cf-surface), var(--cf-accent) etc.
# Everything re-renders with the new palette automatically.</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5" id="theme-preview" style="background-color:var(--cf-surface);border-color:var(--cf-border);">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <div class="font-semibold">Preview card</div>
                        <div class="text-xs text-zinc-400" id="theme-label">Current: default (dark)</div>
                    </div>
                    <div class="flex gap-1.5">
                        <button onclick="window.applyOverviewTheme('default', this)" class="text-[10px] px-2 py-1 rounded-xl border border-zinc-700 hover:bg-zinc-800">Default</button>
                        <button onclick="window.applyOverviewTheme('ocean', this)" class="text-[10px] px-2 py-1 rounded-xl border border-cyan-700 hover:bg-cyan-900/20 text-cyan-300">Ocean</button>
                        <button onclick="window.applyOverviewTheme('forest', this)" class="text-[10px] px-2 py-1 rounded-xl border border-emerald-700 hover:bg-emerald-900/20 text-emerald-300">Forest</button>
                        <button onclick="window.applyOverviewTheme('sunset', this)" class="text-[10px] px-2 py-1 rounded-xl border border-orange-700 hover:bg-orange-900/20 text-orange-300">Sunset</button>
                    </div>
                </div>
                <div class="p-3 rounded-2xl border" style="background:var(--cf-bg); border-color:var(--cf-border);">
                    <div class="text-sm font-medium" style="color:var(--cf-text);">Sample heading</div>
                    <div class="text-xs mt-1" style="color:var(--cf-text-muted);">This text and the card below react to the theme variables in real time.</div>
                    <button class="mt-2 text-xs px-3 py-1 rounded-xl" style="background:var(--cf-accent); color:#0a0a0a;">Action button</button>
                </div>
            </div>
        </div>

        <script>
        (function(){
          if (window.applyOverviewTheme) return;
          var preview = null;
          window.applyOverviewTheme = function(name, btn) {
            preview = preview || document.getElementById('theme-preview');
            if (!preview) return;
            var label = document.getElementById('theme-label');
            var vars = {
              'default': {'--cf-bg':'#0a0a0a','--cf-surface':'#18181b','--cf-border':'#3f3f46','--cf-text':'#e4e4e7','--cf-text-muted':'#a1a1aa','--cf-accent':'#10b981'},
              'ocean':   {'--cf-bg':'#0b1120','--cf-surface':'#0f172a','--cf-border':'#334155','--cf-text':'#e0f2fe','--cf-text-muted':'#64748b','--cf-accent':'#22d3ee'},
              'forest':  {'--cf-bg':'#0a120f','--cf-surface':'#111c18','--cf-border':'#2d443b','--cf-text':'#d1fae5','--cf-text-muted':'#4b5563','--cf-accent':'#10b981'},
              'sunset':  {'--cf-bg':'#1a120f','--cf-surface':'#2a1f18','--cf-border':'#5c4033','--cf-text':'#fed7aa','--cf-text-muted':'#a78b6b','--cf-accent':'#f472b6'}
            };
            var v = vars[name] || vars.default;
            Object.keys(v).forEach(function(k){ preview.style.setProperty(k, v[k]); });
            if (label) label.textContent = 'Current: ' + name;
            // flash the preview to show change
            preview.style.transition = 'box-shadow .15s';
            preview.style.boxShadow = '0 0 0 2px rgba(99,102,241,.3)';
            setTimeout(function(){ if(preview) preview.style.boxShadow = ''; }, 280);
          };
        })();
        </script>

        <!-- NEW EXAMPLE 2: Live Protected API Simulator (desc + snippet + demo) -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Live Protected API Action</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">One @require_login decorator + Database() gives you production auth + queries with almost no code. Click the button to simulate the full flow: auth gate → protected handler → live result + event log.</p>
            </div>

            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>from clayforge.auth import require_login
from clayforge.db import Database
from clayforge import ui

@app.api("/api/protected")
@require_login
def protected(user):
    db = Database("app.db")
    rows = db.query("SELECT * FROM items WHERE owner=?", (user["id"],))
    return {"ok": True, "count": len(rows), "user": user["email"]}</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5">
                <button onclick="window.simOverviewProtected()" class="w-full h-9 rounded-2xl bg-white text-zinc-950 text-sm font-semibold active:scale-[0.985]">Run protected query</button>
                <div id="ov-protected-status" class="mt-2 text-xs text-center text-zinc-400"></div>
                <div id="ov-protected-result" class="mt-2 hidden text-xs border border-emerald-900/60 bg-emerald-950/20 rounded-2xl p-3"></div>
                <div id="ov-protected-log" class="mt-2 max-h-[60px] overflow-auto text-[10px] font-mono bg-black/40 border border-zinc-800 rounded-2xl p-2 text-zinc-400"></div>
            </div>
        </div>

        <script>
        (function(){
          if (window.simOverviewProtected) return;
          window.simOverviewProtected = function() {
            var status = document.getElementById('ov-protected-status');
            var res = document.getElementById('ov-protected-result');
            var log = document.getElementById('ov-protected-log');
            if (!status || !res || !log) return;
            status.textContent = 'Checking auth...';
            res.classList.add('hidden');
            setTimeout(function(){
              status.textContent = 'Authenticated as demo@clayforge.dev • querying DB...';
              setTimeout(function(){
                status.textContent = '';
                res.classList.remove('hidden');
                res.innerHTML = '<div class="text-emerald-400 font-medium">Query succeeded</div><div class="mt-1">3 items found for user. (simulated @require_login + Database result)</div>';
                var d = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});
                log.innerHTML = '<div>['+d+'] Protected action completed</div>' + log.innerHTML;
                while(log.children.length > 4) log.removeChild(log.lastChild);
              }, 420);
            }, 380);
          };
        })();
        </script>

        <!-- Cross-surface cohesion: easy path from beautiful multi-section demo to your code -->
        <div class="mt-8 text-center">
            <a href="#" onclick="(function(){var t=document.createElement('div');t.className='fixed bottom-6 right-6 bg-emerald-600 text-white px-4 py-2 rounded-2xl text-xs z-[999] shadow';t.innerHTML='See examples/ for full demos and Command Center patterns in your code';document.body.appendChild(t);setTimeout(function(){t.remove()},3800);})();return false" class="inline-flex items-center gap-2 text-xs px-4 h-9 rounded-2xl border border-zinc-700 hover:bg-zinc-900 text-zinc-400 hover:text-emerald-300 transition-all duration-200" style="border-color:var(--cf-border);">
                <span>See examples/ for full demos →</span>
            </a>
            <div class="mt-1.5 text-[10px] text-zinc-600">examples/ — deep demos, Command Center patterns (live cross-mutated Grok + multiple Agents), real streaming. (Showcase = polished marketing demo with dedicated tabs.)</div>
        </div>

        <div class="mt-8 text-center text-[10px] text-zinc-500 tracking-[2px]" style="color:var(--cf-text-muted);">
            THIS ENTIRE EXPERIENCE (THE SHOWCASE) IS BUILT WITH CLAYFORGE — THE PREMIER FRAMEWORK FOR PRODUCTION AI AGENT INTERFACES
        </div>

        <!-- Powerful unifying closer - beautifully responsive stack, consistent polish, cf vars, better dividers, delightful CTAs without breaking existing onclick="showSection" or demo JS -->
        <div class="mt-10 max-w-2xl mx-auto text-center border-t border-zinc-800 pt-8" style="border-color:var(--cf-border);">
            <div class="text-sm text-zinc-400">ClayForge gives you everything you need to ship production AI agent applications that look and feel world-class — in minutes, not days.</div>
            <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3 text-xs">
                <a href="#" onclick="(function(){var t=document.createElement('div');t.className='fixed bottom-6 right-6 bg-emerald-600 text-white px-4 py-2 rounded-2xl text-xs z-[999] shadow';t.innerHTML='Deep interactive demos + Command Center patterns in examples/ and your code';document.body.appendChild(t);setTimeout(function(){t.remove()},3800);})();return false" class="px-5 py-2 rounded-2xl border border-zinc-700 hover:bg-zinc-900 hover:border-zinc-600 text-zinc-300 transition-all inline-flex items-center justify-center" style="border-color:var(--cf-border);">See examples/ for full demos + patterns</a>
                <a href="#" data-section="agents" class="px-5 py-2 rounded-2xl border border-emerald-600/60 hover:bg-emerald-900/30 hover:border-emerald-500/70 text-emerald-300 transition-all inline-flex items-center justify-center">See live multi-agent orchestration</a>
            </div>
        </div>

        <!-- Code snippets on overview (per request): clean, copyable minimal examples right before Jump. Shows the zero-boilerplate power for humans and AI agents evaluating the framework. Styled consistently with dashboard/agents (pre + copy button). Added a third for live mutation pattern + short desc above as requested for scannability. -->
        <div class="mt-8">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2 text-center">Code at a glance</div>
            <p class="text-center text-[11px] text-zinc-400 max-w-xl mx-auto mb-3">Copy-paste these into a new app and you have a working production UI in seconds. All the live demos above are built the same way.</p>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
                <!-- Snippet 1: basic page + ui -->
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Minimal page</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code>import clayforge as cf
from clayforge import ui

app = cf.App("My AI App")

@app.page("/")
def home():
    ui.title("Hello from ClayForge")
    with ui.card():
        ui.text("Build reactive UIs in pure Python.")
        ui.button("Click me", on_click=lambda: print("hi"))
    return ui.text("... or just return components")</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <!-- Snippet 2: api + reactive -->
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">@app.api + live state</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code>@app.api("/update")
def update(data: dict):
    # mutate live components or state
    # WS pushes updates to any connected UIs
    return {"status": "ok", "received": data}

# In a page or component:
# ui.button("Call API", on_click=call_my_api)
# GrokChat / AgentCanvas / viz all use the same pattern</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <!-- Snippet 3: live mutation (ties to the micro-demo we added) -->
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Live mutation (the demo above)</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code># In your page:
count = 1248
def bump(n=1):
    global count
    count += n
    # real version: mutate a PlotlyChart/DataTable/custom Element
    # then component._push_update() or return fresh ui.*
ui.button("+1 users", on_click=lambda: bump(1))
# Overview micro-demo + dashboard + forms use this exact flow.</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>
            </div>
            <div class="text-center mt-2 text-[10px] text-zinc-500">See examples/ for complete runnable apps (auth, agents, viz, streaming Grok...)</div>
        </div>

        <!-- Jump to other demos block at bottom of every page (nice touch for navigation, consistent with other sections) -->
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
</div>""")
