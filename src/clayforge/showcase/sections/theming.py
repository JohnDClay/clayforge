"""
Theming & Custom Components section for the ClayForge Showcase.

Impressive live demonstration of the new first-class theming system:
cf.set_theme(), cf.Theme, cf.register_component, cf.Element.

Keeps the signature beautiful zinc/indigo default while allowing instant live morphs.
"""

from __future__ import annotations

import textwrap


def render_theming(current_server_theme: str = "showcase") -> str:
    """Returns the complete themed section wrapper with delightful interactive demos.
    current_server_theme: value of cf.get_theme().name at render time.
    """
    return textwrap.dedent(f"""\
    <div id="section-theming" class="demo-section hidden">
        <div class="max-w-5xl mx-auto px-6 md:px-8 pt-8 pb-20">  <!-- responsive px + consistent container (exact overview model for even centering on sidebar switches + all viewports); pt-8 + global 4.75rem on #main-content + --showcase-title-gap (50px default) + border guards (per layout.py) = professional breathing, zero top borders/hairlines above titles, no fighting layout. Title block (.mb-6 pt-2) immediately followed by substantial content (live switcher etc). No empty/nothing after title. -->
        <!-- Hero header: .mb-6 header block first inside container (titles + "NEW IN 2026" badge first, pt-2 for extra under new layout padding). Coordinates with 4.75rem + .demo-section > div:first-child .mb-6 guards for clean "titles first" start. No stray elements at top of section. -->
        <div class="mb-6 pt-2">
            <div class="text-center">
                <div class="inline-flex items-center gap-x-2 px-4 h-8 rounded-3xl bg-violet-500/10 text-violet-400 text-xs font-medium tracking-[0.15em] mb-4">
                    <i class="fa-solid fa-magic"></i> NEW IN 2026
                </div>
                <h1 class="font-display text-6xl tracking-tighter font-semibold leading-none">Theming that feels<br>like magic.</h1>
                <p class="mt-4 max-w-2xl text-2xl text-zinc-400">One line of Python (<span class="font-mono text-base align-baseline">cf.set_theme("light")</span> or a full Theme object). Instant live updates across the entire interface + any custom components you build. This showcase is using it right now.</p>
            </div>
        </div>

        <!-- Live switcher showcase (client-morph for instant feedback) — premium clay-card lift + consistent 3xl + heavy var() usage for harmony + enhanced hovers/shadows -->
        <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 mb-10 transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <div class="font-semibold text-2xl tracking-tight flex items-center gap-x-2">
                        <i class="fa-solid fa-palette text-violet-400"></i> Live Theme Switcher
                    </div>
                    <div class="text-sm text-zinc-400" style="color: var(--cf-text-muted);">Click any preset to transform the entire Showcase experience right now — watch surfaces, text, and borders morph live.</div>
                </div>
                <div class="px-4 py-1 text-xs rounded-2xl border border-zinc-700 text-zinc-400" style="border-color:var(--cf-border); color:var(--cf-text-muted);">Powered by cf.Theme + CSS vars</div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                <button onclick="window.applyShowcaseTheme('default')" class="group flex items-center gap-4 px-6 h-20 rounded-3xl border border-zinc-700 hover:border-zinc-400 active:scale-[0.985] bg-zinc-950 hover:bg-zinc-900 transition-all duration-200 shadow-sm hover:shadow ring-1 ring-white/5" style="background-color: var(--cf-surface-2); border-color: var(--cf-border);">
                    <div class="w-9 h-9 rounded-3xl bg-indigo-500 shrink-0 ring-1 ring-inset ring-white/10 group-hover:ring-white/40 transition-all shadow"></div>
                    <div class="text-left"><div class="font-semibold text-[15px] tracking-tight">Default</div><div class="text-xs" style="color:var(--cf-text-muted);">Zinc + Indigo</div></div>
                </button>
                <button onclick="window.applyShowcaseTheme('light')" class="group flex items-center gap-4 px-6 h-20 rounded-3xl border border-zinc-700 hover:border-zinc-400 active:scale-[0.985] bg-zinc-950 hover:bg-zinc-900 transition-all duration-200 shadow-sm hover:shadow ring-1 ring-white/5" style="background-color: var(--cf-surface-2); border-color: var(--cf-border);">
                    <div class="w-9 h-9 rounded-3xl bg-indigo-600 ring-1 ring-zinc-300 shrink-0 group-hover:ring-white/40 transition-all shadow"></div>
                    <div class="text-left"><div class="font-semibold text-[15px] tracking-tight">Light</div><div class="text-xs" style="color:var(--cf-text-muted);">Clean &amp; bright</div></div>
                </button>
                <button onclick="window.applyShowcaseTheme('ocean')" class="group flex items-center gap-4 px-6 h-20 rounded-3xl border border-zinc-700 hover:border-zinc-400 active:scale-[0.985] bg-zinc-950 hover:bg-zinc-900 transition-all duration-200 shadow-sm hover:shadow ring-1 ring-white/5" style="background-color: var(--cf-surface-2); border-color: var(--cf-border);">
                    <div class="w-9 h-9 rounded-3xl bg-sky-400 shrink-0 ring-1 ring-inset ring-white/10 group-hover:ring-white/40 transition-all shadow"></div>
                    <div class="text-left"><div class="font-semibold text-[15px] tracking-tight">Ocean</div><div class="text-xs" style="color:var(--cf-text-muted);">Cool blues</div></div>
                </button>
                <button onclick="window.applyShowcaseTheme('forest')" class="group flex items-center gap-4 px-6 h-20 rounded-3xl border border-zinc-700 hover:border-zinc-400 active:scale-[0.985] bg-zinc-950 hover:bg-zinc-900 transition-all duration-200 shadow-sm hover:shadow ring-1 ring-white/5" style="background-color: var(--cf-surface-2); border-color: var(--cf-border);">
                    <div class="w-9 h-9 rounded-3xl bg-emerald-400 shrink-0 ring-1 ring-inset ring-white/10 group-hover:ring-white/40 transition-all shadow"></div>
                    <div class="text-left"><div class="font-semibold text-[15px] tracking-tight">Forest</div><div class="text-xs" style="color:var(--cf-text-muted);">Deep greens</div></div>
                </button>
                <button onclick="window.applyShowcaseTheme('sunset')" class="group flex items-center gap-4 px-6 h-20 rounded-3xl border border-zinc-700 hover:border-zinc-400 active:scale-[0.985] bg-zinc-950 hover:bg-zinc-900 transition-all duration-200 shadow-sm hover:shadow ring-1 ring-white/5" style="background-color: var(--cf-surface-2); border-color: var(--cf-border);">
                    <div class="w-9 h-9 rounded-3xl bg-orange-400 shrink-0 ring-1 ring-inset ring-white/10 group-hover:ring-white/40 transition-all shadow"></div>
                    <div class="text-left"><div class="font-semibold text-[15px] tracking-tight">Sunset</div><div class="text-xs" style="color:var(--cf-text-muted);">Warm accents</div></div>
                </button>
            </div>

            <div class="mt-5 flex items-center gap-x-3 text-xs text-emerald-400 bg-emerald-950/30 border border-emerald-900/50 px-4 py-2 rounded-2xl">
                <i class="fa-solid fa-bolt"></i>
                <span>All updates instant &amp; reversible. Default always one click. <span class="font-medium">Press <kbd class="font-mono px-1.5 py-px bg-emerald-900/60 rounded text-emerald-300" style="border:1px solid var(--cf-border);">T</kbd> anywhere to cycle themes.</span></span>
            </div>
        </div>

        <!-- Server-side set_theme demo (real Python handlers + cf.Theme) — premium card -->
        <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 mb-10 transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
            <div class="flex items-center justify-between mb-5">
                <div>
                    <div class="font-semibold text-xl tracking-tight flex items-center gap-x-2"><i class="fa-solid fa-server text-emerald-400/80"></i> Server-side Theming (cf.set_theme)</div>
                    <div class="text-sm text-zinc-400" style="color:var(--cf-text-muted);">Clicking these calls real Python handlers that invoke set_theme + Theme objects. Future renders &amp; new clients inherit it.</div>
                </div>
                <div class="text-[10px] px-3 py-1 rounded-full bg-emerald-900/40 text-emerald-400 border border-emerald-800" style="border-color:var(--cf-border);">LIVE WS</div>
            </div>
            <div class="flex flex-wrap gap-3 items-center">
                <button onclick="window.applyShowcaseTheme('default');" class="px-5 h-10 text-sm rounded-2xl border border-zinc-700 hover:bg-zinc-800 transition-all active:scale-[0.985]" style="border-color:var(--cf-border);">Reset to Default</button>
                <span class="text-[10px] px-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-700 text-zinc-400" style="background:var(--cf-bg);border-color:var(--cf-border);">Server sees: <span class="font-mono text-emerald-400">{current_server_theme}</span></span>
            </div>
            <div class="mt-4 text-[10px] text-zinc-500" style="color:var(--cf-text-muted);">In your apps these are powered by real <span class="font-mono text-emerald-400">cf.ui.button</span> + Python <span class="font-mono">.on()</span> handlers dogfooding the stack (see examples/).</div>
        </div>

        <!-- Live CSS Vars Inspector (shows the system in action) + enhanced grid feel via populated items -->
        <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 mb-10 transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
            <div class="flex justify-between items-center mb-5">
                <div class="font-semibold text-xl tracking-tight flex items-center gap-x-2"><i class="fa-solid fa-search text-sky-400/80"></i> Live CSS Variable Inspector</div>
                <button onclick="window.refreshThemeInspector &amp;&amp; window.refreshThemeInspector()" class="text-xs px-4 h-9 rounded-2xl border border-zinc-700 hover:bg-zinc-800 transition-all active:scale-[0.985]" style="border-color:var(--cf-border);">Refresh from :root</button>
            </div>
            <div id="theme-inspector" class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono"></div>
            <div class="mt-4 text-[10px] text-zinc-500" style="color:var(--cf-text-muted);">These are the exact --cf-* tokens driving the entire UI and any custom components using var(). Changes from the switcher above appear instantly here.</div>
        </div>

        <!-- Live morphing custom component preview: actual ThemedPreviewCard sample using ONLY cf vars. Updates live on theme change (harmony). Gets the apply morph highlight too. -->
        <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 mb-10 transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
            <div class="flex items-center justify-between mb-4">
                <div class="font-semibold text-xl tracking-tight flex items-center gap-x-2">
                    <i class="fa-solid fa-eye text-rose-400/80"></i> Live ThemedPreviewCard (Custom Component)
                </div>
                <div class="text-[10px] px-3 py-1 rounded-full bg-rose-900/40 text-rose-400 border" style="border-color:var(--cf-border);">MORPHS LIVE</div>
            </div>
            <p class="text-sm text-zinc-400 mb-5" style="color:var(--cf-text-muted);">Simulated custom Element (like the real ThemedPreviewCard in docs_app). Built with var(--cf-surface-2), --cf-primary, --cf-accent, --cf-text etc. for perfect harmony. Switch themes — it transforms with the UI.</p>

            <div class="rounded-3xl border p-6 shadow-inner transition-all duration-300" style="background-color: var(--cf-surface-2); border-color: var(--cf-border); color: var(--cf-text);">
                <div class="flex items-start gap-x-4 mb-5">
                    <div class="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow" style="background-color: var(--cf-primary); color: var(--cf-primary-foreground);">
                        <i class="fa-solid fa-chart-line text-lg"></i>
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-x-2">
                            <div class="font-semibold tracking-tight text-lg">Revenue Pulse</div>
                            <span class="text-[10px] px-2 py-0.5 rounded-2xl" style="background-color: var(--cf-accent); color: var(--cf-bg);">LIVE</span>
                        </div>
                        <div style="color: var(--cf-text-muted);" class="text-xs">ThemedPreviewCard • cf.register_component + var(--cf-*) only</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
                    <div class="rounded-2xl p-4" style="background-color: var(--cf-bg); border: 1px solid var(--cf-border);">
                        <div style="color:var(--cf-text-muted);" class="text-[10px] uppercase tracking-[1.5px] mb-1">ARR</div>
                        <div class="font-semibold text-2xl tabular-nums" style="color: var(--cf-accent);">$2.41m</div>
                    </div>
                    <div class="rounded-2xl p-4" style="background-color: var(--cf-bg); border: 1px solid var(--cf-border);">
                        <div style="color:var(--cf-text-muted);" class="text-[10px] uppercase tracking-[1.5px] mb-1">Growth</div>
                        <div class="font-semibold text-2xl tabular-nums" style="color: var(--cf-success);">+34%</div>
                    </div>
                    <div class="rounded-2xl p-4" style="background-color: var(--cf-bg); border: 1px solid var(--cf-border);">
                        <div style="color:var(--cf-text-muted);" class="text-[10px] uppercase tracking-[1.5px] mb-1">Active</div>
                        <div class="font-semibold text-2xl tabular-nums">18.4k</div>
                    </div>
                </div>

                <div class="flex items-center gap-x-2 text-xs">
                    <div class="px-4 h-8 rounded-2xl flex items-center font-medium transition-colors" style="background-color: var(--cf-primary); color: var(--cf-primary-foreground);">Primary CTA</div>
                    <div style="color: var(--cf-text-muted);">Uses --cf-primary-foreground, --cf-success, --cf-accent for full live morph</div>
                </div>
            </div>
            <div class="mt-3 text-[10px] text-center" style="color:var(--cf-text-muted);">This preview + all switcher/server/inspector cards above are pure var(--cf-*) driven (plus clay-card lift).</div>
        </div>

        <!-- Custom component + API demo — premium cards with better spacing + 3xl + vars -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
                <div class="uppercase text-xs tracking-[1.5px] text-violet-400 mb-3">CUSTOM COMPONENTS</div>
                <div class="text-2xl font-semibold tracking-tight mb-3">cf.register_component</div>
                <p class="text-sm text-zinc-400 mb-6" style="color:var(--cf-text-muted);">Create any Element subclass. Register it once. It becomes a first-class ui.* citizen with full theming, events, and context support.</p>

                <div class="font-mono text-xs bg-black/50 border border-zinc-800 p-6 rounded-3xl leading-relaxed" style="background-color: var(--cf-bg); border-color: var(--cf-border);">
                    class BrandMetric(Element):<br>
                    &nbsp;&nbsp;def to_html(self):<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;color = get_theme().get("primary")<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;...<br><br>
                    cf.register_component(BrandMetric, "brand_metric")<br><br>
                    # Now works:<br>
                    # ui.brand_metric("42.8k")
                </div>
                <div class="mt-4 text-xs" style="color:var(--cf-accent);">See the full example in docs_app/app.py — the ThemedPreviewCard powers live demos.</div>
            </div>

            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 flex flex-col transition-all duration-300" style="background-color: var(--cf-surface); border-color: var(--cf-border);">
                <div class="uppercase text-xs tracking-[1.5px] text-violet-400 mb-3">SERVER API</div>
                <div class="text-2xl font-semibold tracking-tight mb-3">cf.set_theme() &amp; cf.Theme</div>
                <div class="text-sm text-zinc-400 flex-1" style="color:var(--cf-text-muted);">
                    Call from anywhere — module level, inside @app.page handlers, or when creating your App.
                    The active Theme automatically flows into shells, custom components, and every var(--cf-*) usage.
                </div>
                <div class="mt-6 space-y-2 text-xs font-mono bg-black/40 p-5 rounded-3xl border border-zinc-800" style="background-color: var(--cf-bg); border-color: var(--cf-border);">
                    <div>cf.set_theme("light")</div>
                    <div>cf.set_theme({{"--cf-primary": "#22c55e"}})</div>
                    <div>cf.set_theme(Theme(name="midnight", mode="dark", css_vars=...))</div>
                </div>
            </div>
        </div>

        <div class="mt-10 text-xs text-center text-zinc-500" style="color:var(--cf-text-muted);">
            Switch themes above — watch the sidebar, cards, and typography adapt live.<br>
            This entire experience (including the switcher) is built with the new ClayForge theming primitives.
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
    </div>""")
