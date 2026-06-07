"""
Forms & Tools section for the ClayForge Showcase.

Polished with several live interactive demos that show you can build surprisingly sophisticated,
beautiful, reactive UIs with almost zero boilerplate:
- Exact cf.ui.* fidelity static form
- Rich protected auth + DB live simulator (todos with mutations)
- Live Tool Runner
- NEW: Live Reactive Form Studio (real-time validation + payload + rendered preview)
- NEW: Dynamic Form + Upload Composer (add fields live, attachments, export + submit composed package)
All wired with the same live JS mutation patterns as the rest of the showcase.
"""


def render_forms() -> str:
    """Returns the FULL section wrapper for the Forms demo.
    Enhanced with several beautiful live demos (reactive forms, dynamic field builder + uploads,
    protected auth+db, tool runner) to show what cool production UIs you can create with the framework.
    """
    return """<div id="section-forms" class="demo-section hidden">
    <div class="max-w-5xl mx-auto px-6 md:px-8 pt-8 pb-20">  <!-- CONSISTENT px-6 md:px-8 (overview model + force rule for centering) -->
        <div class="mb-6">  <!-- THE .mb-6 is first after container (good, titles-first prose). layout.py .demo-section > div:first-child .mb-6 + GAP var + padding-top guard + 4.75rem provide exact 50px professional breathing above title. No pt-2 (GAP handles). Matches overview. No stray elements before. Right after this: form card + auth sim (tight, no blank space to look empty). -->
            <div class="text-center">
                <div class="text-indigo-400 text-xs tracking-[2px] font-semibold">RICH BUILT-INS + LIVE REACTIVE TOOLS</div>
                <div class="font-display text-4xl tracking-tighter font-semibold mt-1">Forms &amp; Tools</div>
                <p class="text-zinc-400 mt-2 max-w-2xl">Exact cf.ui.* fidelity + surprisingly powerful live demos (reactive validation, dynamic fields, uploads, protected auth+db, tool calling). This is what "beautiful by default, zero boilerplate" actually feels like in production.</p>
            </div>
        </div>

        <!-- Premium "New Engineering Request" form card: clay-card + ring for lift, p-8 generous internal (matches new main-view 4px frame breathing), exact ui.* classes for labels/inputs/select/checkbox/file (uppercase tracking, py-2.5, zinc focus rings, accent indigo checkbox, emerald mono hints), responsive grid for fields, better spacing/shadows/focus, premium dropzone for file. Consistent rounded-3xl zinc/emerald/indigo. -->
        <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 shadow-sm ring-1 ring-white/5">
            <div class="flex items-center gap-x-3 mb-6">
                <div class="w-9 h-9 rounded-2xl bg-indigo-500/10 flex items-center justify-center shrink-0">
                    <i class="fa-solid fa-file-invoice text-indigo-400"></i>
                </div>
                <div>
                    <div class="text-2xl font-semibold tracking-tight">New Engineering Request</div>
                    <div class="text-[10px] text-zinc-500">Exact match to cf.ui.* server output — beautiful by default</div>
                </div>
            </div>
            <div class="grid grid-cols-1 gap-5">
                <!-- Exact TextInput fidelity (label + input classes from core TextInput.to_html) -->
                <div>
                    <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Request title</div>
                    <input placeholder="Request title" value="Migrate vector DB to Grok-accelerated tier" class="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 transition-all">
                </div>

                <!-- Responsive grid for form elements (priority + date) -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <!-- Exact Select fidelity (label + wrapper + select classes from core Select.to_html) -->
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Priority</div>
                        <div class="w-full">
                            <select class="w-full bg-zinc-950 border border-zinc-800 text-sm rounded-2xl px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 transition-all"><option>High Priority</option><option>Normal</option></select>
                        </div>
                    </div>
                    <!-- Date styled to match input family for consistency -->
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Target date</div>
                        <input type="date" value="2026-08-01" class="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm text-zinc-200 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 transition-all">
                    </div>
                </div>

                <!-- Exact Checkbox fidelity (structure + classes from core Checkbox.to_html) + group hint -->
                <div class="pt-1">
                    <label class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">
                        <input type="checkbox" class="w-4 h-4 accent-indigo-500 bg-zinc-950 border border-zinc-700 rounded focus:ring-1 focus:ring-offset-2 focus:ring-offset-zinc-950 focus:ring-indigo-500" checked>
                        <span>Urgent (uses cf.ui.checkbox pattern)</span>
                    </label>
                </div>

                <!-- Premium static FileUpload dropzone visual (inspired by core FileUpload: label + file styling + emerald mono name; static premium dropzone for showcase beauty) -->
                <div>
                    <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Attachment</div>
                    <div class="w-full border border-dashed border-zinc-700 bg-zinc-950/50 rounded-3xl px-5 py-5 text-sm flex flex-col items-center justify-center text-center cursor-not-allowed transition-colors hover:border-zinc-600">
                        <i class="fa-solid fa-cloud-upload-alt text-xl text-zinc-500 mb-1.5"></i>
                        <div class="text-zinc-300">Drop file here or click to browse</div>
                        <div class="text-[10px] text-zinc-500 mt-0.5">(matches cf.ui.file_upload native + preview UX)</div>
                    </div>
                    <div class="text-[10px] mt-1.5 text-emerald-400 font-mono flex items-center gap-x-1"><i class="fa-solid fa-file-pdf text-emerald-500/80"></i> <span>design-spec-v2.pdf (simulated)</span></div>
                </div>

                <!-- Bonus exact-ish TextArea for newly surfaced ui.text_area fidelity (grid spans) -->
                <div>
                    <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Description</div>
                    <textarea rows="2" class="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 transition-all resize-y" placeholder="Details for the platform team...">Migrate the vector store to use Grok embeddings for 3x faster retrieval in the engineering dashboard and agent tooling.</textarea>
                </div>

                <button onclick="window.submitDemoForm()" class="w-full h-11 bg-white text-zinc-950 rounded-2xl font-semibold text-sm mt-1 active:scale-[0.985] transition-all shadow hover:shadow-md flex items-center justify-center gap-x-2">
                    <i class="fa-solid fa-paper-plane"></i>
                    <span>Submit to Platform Team</span>
                </button>
            </div>
        </div>

        <!-- SECTION: Protected Auth + DB -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Protected Auth + Database</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">Real @require_login + Database patterns. One decorator + one Database() call gives you protected pages and queries with zero boilerplate.</p>
            </div>

            <!-- Mini production snippet for this demo -->
            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>from clayforge.auth import require_login
from clayforge.db import Database
from clayforge import ui

@app.page("/todos")
@require_login
def my_todos(user):
    db = Database("app.db")
    rows = db.query("SELECT * FROM todos WHERE user_id=?", (user["id"],))
    # render with cf.ui.* — live updates included</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <!-- The actual interactive demo -->
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-8 shadow-sm ring-1 ring-white/5">
            <div class="flex items-start gap-x-4">
                <div class="w-9 h-9 mt-0.5 rounded-2xl bg-indigo-500/10 flex items-center justify-center shrink-0">
                    <i class="fa-solid fa-shield-halved text-indigo-400 text-lg"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-x-2 flex-wrap">
                        <div class="font-semibold text-xl tracking-tight">Protected page + DB query</div>
                        <span class="text-[10px] px-2.5 py-px rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">LIVE SIM</span>
                        <span class="text-[10px] px-2 py-px rounded-xl bg-emerald-900/40 text-emerald-400 border border-emerald-800/60 flex items-center gap-x-1"><i class="fa-solid fa-lock text-[9px]"></i><span>AUTH+DB</span></span>
                    </div>
                    <div class="text-sm text-zinc-400 mt-1">Real patterns from auth_db_todo.py &amp; internal_crm_with_auth.py — @require_login + Database. Zero-boilerplate.</div>

                    <div class="mt-5 bg-zinc-950 border border-zinc-800 rounded-2xl p-4 shadow-inner">
                        <!-- richer session header w/ icons -->
                        <div class="flex items-center justify-between text-xs mb-3">
                            <div class="flex items-center gap-x-2">
                                <i class="fa-solid fa-user-check text-emerald-400"></i>
                                <span>
                                    <span class="font-medium text-emerald-400">Session active</span>
                                    <span class="text-zinc-400"> — alex@clayforge.dev</span>
                                </span>
                            </div>
                            <div class="px-2 py-px text-[10px] rounded-xl bg-emerald-900/40 text-emerald-400 border border-emerald-800/60 flex items-center gap-x-1">
                                <i class="fa-solid fa-lock text-[9px]"></i>
                                <span>Authenticated</span>
                            </div>
                        </div>

                        <!-- richer code block presentation -->
                        <div class="font-mono text-[11px] bg-black/60 border border-zinc-800 p-3.5 rounded-xl text-zinc-400 leading-snug mb-4 shadow-sm">
                            <div class="text-emerald-400/80 mb-0.5 text-[10px]">// protected handler</div>
                            @require_login<br>
                            def todos(user):<br>
                            &nbsp;&nbsp;db = Database("clayforge_crm.db")<br>
                            &nbsp;&nbsp;rows = db.query("SELECT * FROM todos WHERE user_id = ?", (user.id,))<br>
                            &nbsp;&nbsp;# ... render with cf.ui.*
                        </div>

                        <div class="flex flex-wrap gap-2">
                            <!-- buttons: subtle animations, more icons, hover depth, active scale preserved + enhanced -->
                            <button onclick="window.simulateProtectedQuery()" class="h-9 px-4 text-sm font-semibold rounded-2xl bg-white text-zinc-950 active:scale-[0.985] transition-all duration-150 flex items-center gap-x-2 hover:shadow">
                                <i class="fa-solid fa-database text-xs"></i>
                                <span>Run protected DB query</span>
                            </button>
                            <button onclick="window.addSimTodo()" class="h-9 px-4 text-sm font-semibold rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-200 transition-all active:scale-[0.985] duration-150 flex items-center gap-x-1.5">
                                <i class="fa-solid fa-plus text-xs"></i>
                                <span>Add todo</span>
                            </button>
                            <button onclick="window.clearSimCompleted()" class="h-9 px-4 text-sm font-semibold rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-200 transition-all active:scale-[0.985] duration-150 flex items-center gap-x-1.5">
                                <i class="fa-solid fa-trash text-xs"></i>
                                <span>Clear completed</span>
                            </button>
                            <button onclick="window.showRealUsageCode()" class="h-9 px-4 text-sm font-semibold rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-200 transition-all active:scale-[0.985] duration-150">Real usage code</button>
                        </div>

                        <div id="authdb-result" class="mt-4 hidden"></div>
                    </div>

                    <div class="mt-3 text-[10px] text-emerald-400/90 font-medium flex items-center gap-x-1.5">
                        <i class="fa-solid fa-info-circle"></i>
                        <span>In a real app this is ~10 lines of Python (see the examples). The @require_login decorator + Database() do all the heavy lifting — zero ceremony, production ready.</span>
                    </div>
                </div>
            </div>
            </div> <!-- /section wrapper for Auth+DB -->
        </div>

        <!-- Additional visual demos for ui components (Select / Checkbox group / FileUpload dropzone) — static but premium, using exact core markup classes. Responsive grid. Placed AFTER the form card + the auth sim (right after title/prose) — ensures immediate tight content, no blank space/"look like nothing" after the .mb-6 on tab switch. (Previews are bonus; primary demos are the engineering form + protected auth+db live sim for first-class patterns visibility.) mt-6 provides breathing. -->
        <div class="mt-6">
            <div class="px-1 mb-2">
                <div class="text-[10px] uppercase tracking-[1.5px] text-zinc-500">Exact cf.ui.* fidelity previews</div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Standalone nice Select example -->
                <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5">
                    <div class="text-emerald-400 text-[10px] mb-2 flex items-center gap-x-1.5"><i class="fa-solid fa-list"></i> <span>cf.ui.select(label=..., options=...)</span></div>
                    <div class="w-full">
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Assign team</div>
                        <select class="w-full bg-zinc-950 border border-zinc-800 text-sm rounded-2xl px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-700 transition-all"><option>Platform</option><option>Infra</option><option>AI Research</option><option>Design</option></select>
                    </div>
                    <div class="mt-2 text-[10px] text-zinc-500">Full fidelity to core Select.to_html() wrapper + label + classes.</div>
                </div>
                <!-- Checkbox group visual demo -->
                <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5">
                    <div class="text-emerald-400 text-[10px] mb-2 flex items-center gap-x-1.5"><i class="fa-solid fa-check-square"></i> <span>cf.ui.checkbox(...) group</span></div>
                    <div class="space-y-2.5">
                        <label class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">
                            <input type="checkbox" class="w-4 h-4 accent-indigo-500 bg-zinc-950 border border-zinc-700 rounded focus:ring-1 focus:ring-offset-2 focus:ring-offset-zinc-950 focus:ring-indigo-500" checked>
                            <span>Notify stakeholders</span>
                        </label>
                        <label class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">
                            <input type="checkbox" class="w-4 h-4 accent-indigo-500 bg-zinc-950 border border-zinc-700 rounded focus:ring-1 focus:ring-offset-2 focus:ring-offset-zinc-950 focus:ring-indigo-500">
                            <span>Attach Grok analysis</span>
                        </label>
                        <label class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">
                            <input type="checkbox" class="w-4 h-4 accent-indigo-500 bg-zinc-950 border border-zinc-700 rounded focus:ring-1 focus:ring-offset-2 focus:ring-offset-zinc-950 focus:ring-indigo-500" checked>
                            <span>Schedule follow-up</span>
                        </label>
                    </div>
                    <div class="mt-2 text-[10px] text-zinc-500">Exact label + input classes from Checkbox.to_html().</div>
                </div>
                <!-- Premium FileUpload dropzone visual (static) -->
                <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-5">
                    <div class="text-emerald-400 text-[10px] mb-2 flex items-center gap-x-1.5"><i class="fa-solid fa-paperclip"></i> <span>cf.ui.file_upload(label=...)</span></div>
                    <div class="w-full">
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Supporting docs</div>
                        <div class="border border-dashed border-zinc-700 bg-zinc-950/60 rounded-3xl px-4 py-[13px] text-center">
                            <div class="flex flex-col items-center">
                                <i class="fa-solid fa-upload text-zinc-500 mb-1"></i>
                                <div class="text-xs text-zinc-300">Drop or select file</div>
                                <div class="text-[10px] text-zinc-500 mt-0.5 font-mono">.pdf .fig .md accepted</div>
                            </div>
                        </div>
                        <div class="text-[10px] mt-1.5 text-emerald-400 font-mono">api-spec-v4.pdf (simulated)</div>
                    </div>
                    <div class="mt-2 text-[10px] text-zinc-500">Premium dropzone + exact label + emerald name hint from FileUpload.to_html().</div>
                </div>
            </div>
        </div>

        <!-- SECTION: Live Tool Runner -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Live Tool / Command Runner</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">Simulate protected @app.api tool calls from a form. The real version uses the exact same pattern: ui.* inputs + button that calls a decorated endpoint and returns live UI or data.</p>
            </div>

            <!-- Mini snippet -->
            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>@app.api("/tools/run")
@require_login
def run_tool(user, tool: str, query: str):
    # ... do work, possibly hit DB or Grok
    return {"result": f"Ran {tool}", "data": [...]}

# In page: button(on_click=call_api) + result container that re-renders</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <!-- The actual demo -->
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
            <div class="flex items-center gap-x-3 mb-4">
                <div class="w-8 h-8 rounded-2xl bg-amber-500/10 flex items-center justify-center">
                    <i class="fa-solid fa-terminal text-amber-400"></i>
                </div>
                <div>
                    <div class="font-semibold">Live Tool Runner (cf.ui + @app.api pattern)</div>
                    <div class="text-[10px] text-zinc-500">Simulates calling a protected tool endpoint from a form. Real version uses the same @app.api + ui.* rendering.</div>
                </div>
            </div>
            <div class="flex flex-wrap gap-3 items-end">
                <div class="flex-1 min-w-[180px]">
                    <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Tool</div>
                    <select id="tool-select" class="w-full bg-zinc-950 border border-zinc-800 text-sm rounded-2xl px-4 py-2 text-zinc-200">
                        <option value="web_search">web_search</option>
                        <option value="analyze_code">analyze_code</option>
                        <option value="fact_check">fact_check</option>
                    </select>
                </div>
                <div class="flex-1 min-w-[180px]">
                    <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Query</div>
                    <input id="tool-query" value="latest AI UI frameworks 2026" class="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm">
                </div>
                <button onclick="window.runToolDemo()" class="h-10 px-5 rounded-2xl bg-white text-zinc-950 font-semibold text-sm active:scale-[0.985] flex items-center gap-x-2">
                    <i class="fa-solid fa-play"></i>
                    <span>Run Tool</span>
                </button>
            </div>
            <div id="tool-result" class="mt-3 hidden text-xs"></div>
            </div> <!-- /section wrapper for Tool Runner -->
        </div>

        <!-- SECTION: Live Reactive Form Studio -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Live Reactive Form Studio</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">As-you-type validation, live JSON payload, and a rendered preview that updates instantly. Shows how stateful reactive UIs are trivial with cf.ui + client-side live updates (or real WS).</p>
            </div>

            <!-- Mini snippet -->
            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>title = ui.text_input("Name", on_change=update_preview)
impact = ui.slider("Impact", on_change=update_preview)
# In real app the on_change can trigger _push_update or just client re-render
# The preview div below is a live cf.ui.card equivalent</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <!-- The actual demo -->
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-x-3">
                    <div class="w-8 h-8 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                        <i class="fa-solid fa-magic text-emerald-400"></i>
                    </div>
                    <div>
                        <div class="font-semibold flex items-center gap-x-2">Live Reactive Form Studio <span class="text-[9px] px-1.5 py-px rounded-full bg-emerald-500/10 text-emerald-400 tracking-wider">LIVE</span></div>
                        <div class="text-[10px] text-zinc-500">Real-time validation + live JSON payload + rendered preview. Zero boilerplate reactivity.</div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Inputs that drive everything live -->
                <div class="space-y-4">
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Feature name</div>
                        <input id="rf-name" value="Grok-powered search" oninput="window.updateReactiveForm()" class="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm text-zinc-200 focus:border-emerald-600/60 focus:ring-1 focus:ring-emerald-600/30 transition-all">
                        <div id="rf-name-err" class="text-[10px] text-red-400 mt-0.5 hidden">Name must be at least 3 characters</div>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Type</div>
                            <select id="rf-type" onchange="window.updateReactiveForm()" class="w-full bg-zinc-950 border border-zinc-800 text-sm rounded-2xl px-4 py-2.5 text-zinc-200">
                                <option value="search">Search / Retrieval</option>
                                <option value="agent">Agent Capability</option>
                                <option value="viz">Visualization</option>
                                <option value="tool">Tool / Action</option>
                            </select>
                        </div>
                        <div>
                            <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Impact</div>
                            <input id="rf-impact" type="range" min="1" max="10" value="7" oninput="window.updateReactiveForm()" class="w-full accent-emerald-400">
                            <div class="text-[10px] text-center text-zinc-400"><span id="rf-impact-val">7</span>/10 — high leverage</div>
                        </div>
                    </div>
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Description</div>
                        <textarea id="rf-desc" rows="2" oninput="window.updateReactiveForm()" class="w-full px-4 py-2.5 bg-zinc-950 border border-zinc-800 rounded-2xl text-sm text-zinc-200 resize-y" placeholder="What does this unlock?">Instant semantic search across all previous Grok conversations and design docs.</textarea>
                    </div>
                    <div class="flex items-center gap-2">
                        <label class="inline-flex items-center gap-2 text-sm text-zinc-200 cursor-pointer">
                            <input id="rf-public" type="checkbox" checked onchange="window.updateReactiveForm()" class="w-4 h-4 accent-emerald-500 bg-zinc-950 border border-zinc-700 rounded">
                            <span>Make public in gallery</span>
                        </label>
                    </div>
                    <button onclick="window.submitReactiveForm()" class="w-full h-10 rounded-2xl bg-white text-zinc-950 font-semibold text-sm active:scale-[0.985] flex items-center justify-center gap-x-2">
                        <i class="fa-solid fa-rocket"></i>
                        <span>Submit Feature Request</span>
                    </button>
                </div>

                <!-- Live outputs -->
                <div class="space-y-4">
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-emerald-400 mb-1 flex items-center gap-x-1"><i class="fa-solid fa-code"></i> Live API payload</div>
                        <pre id="rf-payload" class="font-mono text-[10px] bg-black/60 border border-zinc-800 rounded-2xl p-3 text-emerald-300/90 overflow-auto max-h-[108px] leading-snug"></pre>
                    </div>
                    <div>
                        <div class="text-[10px] uppercase tracking-widest text-emerald-400 mb-1 flex items-center gap-x-1"><i class="fa-solid fa-eye"></i> Live preview (what users will see)</div>
                        <div id="rf-preview" class="bg-zinc-950 border border-zinc-800 rounded-2xl p-4 text-sm">
                            <!-- populated by JS -->
                        </div>
                    </div>
                    <div id="rf-success" class="hidden text-xs px-3 py-2 bg-emerald-900/30 border border-emerald-800/60 text-emerald-300 rounded-xl"></div>
                </div>
            </div>
            </div> <!-- /section wrapper for Reactive Studio -->
        </div>

        <!-- SECTION: Dynamic Form + Upload Composer -->
        <div class="mt-8">
            <div class="mb-3">
                <div class="text-sm font-semibold flex items-center gap-x-2">
                    <span>Dynamic Form + Upload Composer</span>
                    <span class="text-[9px] px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 tracking-wider">LIVE DEMO</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-1">Add/remove fields at runtime, attach files with live gallery + progress, export schema, and submit a fully composed package. Demonstrates powerful dynamic UIs that are still pure and simple in ClayForge.</p>
            </div>

            <!-- Mini snippet -->
            <div class="mb-3 relative group">
                <pre class="font-mono text-[9px] bg-zinc-950 border border-zinc-800 rounded-2xl p-2.5 overflow-auto text-zinc-200"><code>fields = []
def add_field(kind):
    fields.append(ui.text_input(...) if kind == "text" else ...)
    # re-render container live
container = ui.div(fields + [ui.button("Submit", on_click=submit)])
# Uploads handled with ui.file_upload + live list state</code></pre>
                <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-1 right-1 text-[8px] px-1.5 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                    <i class="fa-solid fa-copy text-[7px]"></i>
                </button>
            </div>

            <!-- The actual demo -->
            <div class="clay-card bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
            <div class="flex items-center gap-x-3 mb-4">
                <div class="w-8 h-8 rounded-2xl bg-violet-500/10 flex items-center justify-center">
                    <i class="fa-solid fa-wand-magic-sparkles text-violet-400"></i>
                </div>
                <div>
                    <div class="font-semibold">Dynamic Form + Upload Composer <span class="text-[9px] px-1.5 py-px rounded-full bg-violet-500/10 text-violet-400 tracking-wider">LIVE</span></div>
                    <div class="text-[10px] text-zinc-500">Add fields on the fly • attach files with live progress • export schema + submit composed package. Pure client-side power that maps 1:1 to real cf.ui + @app.api.</div>
                </div>
            </div>

            <div class="flex flex-wrap gap-2 mb-4">
                <button onclick="window.addDynamicField('text')" class="px-3 py-1 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 flex items-center gap-x-1.5"><i class="fa-solid fa-font text-xs"></i> Add text field</button>
                <button onclick="window.addDynamicField('select')" class="px-3 py-1 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 flex items-center gap-x-1.5"><i class="fa-solid fa-list text-xs"></i> Add select</button>
                <button onclick="window.addDynamicField('checkbox')" class="px-3 py-1 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 flex items-center gap-x-1.5"><i class="fa-solid fa-check-square text-xs"></i> Add checkbox</button>
                <button onclick="window.addDynamicField('upload')" class="px-3 py-1 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 flex items-center gap-x-1.5"><i class="fa-solid fa-paperclip text-xs"></i> Add attachment slot</button>
                <button onclick="window.clearDynamicForm()" class="ml-auto px-3 py-1 text-xs rounded-2xl border border-zinc-700 text-zinc-400 hover:text-white">Clear all</button>
            </div>

            <!-- The live built form -->
            <div id="dynamic-form-area" class="bg-zinc-950 border border-zinc-800 rounded-2xl p-4 min-h-[92px] mb-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <!-- JS populates live fields here -->
            </div>

            <!-- Uploads gallery -->
            <div class="mb-3">
                <div class="text-[10px] uppercase tracking-widest text-zinc-500 mb-1">Attachments (live)</div>
                <div id="upload-gallery" class="flex flex-wrap gap-2 min-h-[42px]"></div>
                <button onclick="window.simulateUpload()" class="mt-2 text-[11px] px-3 py-1 rounded-xl border border-dashed border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-500 flex items-center gap-x-1.5">
                    <i class="fa-solid fa-upload text-xs"></i> <span>Simulate upload (drag-drop in real app)</span>
                </button>
            </div>

            <div class="flex gap-2">
                <button onclick="window.exportDynamicSchema()" class="flex-1 h-9 rounded-2xl border border-zinc-700 text-sm flex items-center justify-center gap-x-2 hover:bg-zinc-900">Export JSON Schema</button>
                <button onclick="window.submitDynamicComposer()" class="flex-1 h-9 rounded-2xl bg-white text-zinc-950 font-semibold text-sm active:scale-[0.985] flex items-center justify-center gap-x-2">
                    <i class="fa-solid fa-paper-plane"></i> <span>Build &amp; Submit Package</span>
                </button>
            </div>
            <div id="dynamic-result" class="mt-3 text-xs hidden"></div>
            </div> <!-- /section wrapper for Dynamic Composer -->
        </div>

        <!-- Code snippets for forms & tools page (added per request) + production usage. Copyable, consistent style. Ties directly to real @app.api, ui.*, auth patterns. -->
        <div class="mt-6">
            <div class="text-[10px] uppercase tracking-[1.5px] font-semibold text-emerald-400 mb-2">Production code snippets</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Form + handler</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code>import clayforge as cf
from clayforge import ui

@app.page("/request")
def eng_request():
    title = ui.text_input("Title")
    prio = ui.select("Priority", options=["High","Normal"])
    urgent = ui.checkbox("Urgent", checked=True)

    def submit():
        # real handler receives values
        print(title.value, prio.value, urgent.value)
        # can return ui or call @app.api

    ui.button("Submit", on_click=submit)
    # All components participate in live WS updates</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <div class="relative group">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">@app.api + auth + db</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code>from clayforge.auth import require_login
from clayforge.db import Database
from clayforge import ui

@app.api("/tools/run")
@require_login
def run_tool(user, tool: str, query: str):
    db = Database("tools.db")
    # ... log, execute, etc.
    return {"result": f"Ran {tool} for {user['email']}"}

# In page: ui.button(..., on_click=call_api)
# Same pattern powers the live sim above + real examples</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>

                <!-- New snippet for the cool reactive + dynamic demos we just added -->
                <div class="relative group md:col-span-2">
                    <div class="text-[10px] text-zinc-500 mb-1 px-1">Live reactive + dynamic forms (the "pretty cool stuff" demos)</div>
                    <pre class="font-mono text-[10px] bg-zinc-950 border border-zinc-800 rounded-2xl p-3 overflow-auto text-zinc-200 leading-snug"><code># Real-time validation + live preview (no custom JS needed in prod)
title = ui.text_input("Name", on_change=update_preview)
# Dynamic field addition maps directly to lists of ui.* components
fields = []
def add_field(kind):
    fields.append(ui.text_input("New") if kind=="text" else ui.select(...))
    # re-render the containing container — zero boilerplate
container = ui.div([*fields, ui.button("Submit", on_click=submit)])</code></pre>
                    <button onclick="const pre=this.closest('.group').querySelector('pre'); navigator.clipboard.writeText(pre.innerText.trim()); const t=document.createElement('span'); t.className='absolute -top-1 right-1 text-[9px] bg-emerald-600 text-white px-1.5 py-px rounded'; t.textContent='copied'; this.after(t); setTimeout(()=>t.remove(),1200)" class="absolute top-2 right-2 text-[9px] px-2 py-0.5 rounded-xl border border-zinc-700 bg-zinc-900/80 hover:bg-zinc-800 flex items-center gap-x-1 opacity-70 group-hover:opacity-100 transition">
                        <i class="fa-solid fa-copy text-[8px]"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Quick cross-nav buttons (plain window.showSection) so every tab has working navigation CTAs like overview.
             Restores the interconnected "new buttons" feel from the beautiful prior version. Click to jump to any surface.
             Uses same professional small pill style; no layout impact on the title breathing or centering. -->
        <div class="mt-8 pt-5 border-t text-center" style="border-color:var(--cf-border);">
            <div class="text-[10px] uppercase tracking-[1.5px] text-zinc-500 mb-1.5">Jump to other demos</div>
            <div class="flex flex-wrap justify-center gap-1.5">
                <button data-section="overview"  class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Overview</button>
                <button data-section="grok"  class="px-3 h-7 text-xs rounded-2xl border border-emerald-600/50 hover:bg-emerald-900/20 text-emerald-300 active:scale-[0.985] transition">GrokChat</button>
                <button data-section="agents"  class="px-3 h-7 text-xs rounded-2xl border border-emerald-600/50 hover:bg-emerald-900/20 text-emerald-300 active:scale-[0.985] transition">Agent Vision</button>
                <button data-section="dashboard"  class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Dashboard</button>
                <button data-section="theming"  class="px-3 h-7 text-xs rounded-2xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 active:scale-[0.985] transition">Theming</button>
            </div>
        </div>
    </div>
</div>

<script>
(function() {
  // Define once on initial HTML injection (runs during page parse, before load)
  if (window.simulateProtectedQuery) return; // guard against re-injection

  // --- Simple live JS state for realistic interactive simulation (fully contained) ---
  let authDbTodos = [
    {id: 1, title: "Deploy new staging env", done: true},
    {id: 2, title: "Review Grok tool-calling PR", done: false},
    {id: 3, title: "Finalize auth migration docs", done: true}
  ];
  let authDbLastAction = '';

  window.renderAuthDbResults = function() {
    const container = document.getElementById('authdb-result');
    if (!container) return;
    container.classList.remove('hidden');
    const doneCount = authDbTodos.filter(t => t.done).length;
    const rowsHtml = authDbTodos.map(todo => {
      const statusClass = todo.done
        ? 'bg-emerald-900/40 text-emerald-400'
        : 'bg-amber-900/40 text-amber-400';
      const statusText = todo.done ? 'done' : 'pending';
      return `
        <div class="px-3 py-2 flex items-center justify-between group hover:bg-zinc-900/60 transition-colors">
          <span class="text-zinc-300 flex-1 pr-3 text-[13px]">${todo.title}</span>
          <div class="flex items-center gap-x-2 shrink-0">
            <span onclick="window.toggleSimTodo(${todo.id}, event)"
                  class="cursor-pointer select-none text-[10px] px-2.5 py-px rounded-full font-medium transition ${statusClass}">
              ${statusText}
            </span>
            <button onclick="window.toggleSimTodo(${todo.id}, event)"
                    title="Toggle status (simulates protected handler)"
                    class="opacity-70 hover:opacity-100 px-2 py-px text-[10px] rounded-lg border border-zinc-700 hover:bg-zinc-800 text-zinc-400 active:scale-95 transition flex items-center">
              <i class="fa-solid fa-sync text-[9px]"></i>
            </button>
          </div>
        </div>`;
    }).join('');

    // Luxurious result area + live query feel: varying realistic timing + row counts surfaced prominently, deeper surfaces, refined rows, generous padding
    const queryMs = (0.9 + Math.random() * 1.4).toFixed(1);
    container.innerHTML = `
      <div class="border border-emerald-900/60 bg-emerald-950/20 rounded-2xl p-5 shadow-inner">
        <div class="flex items-center justify-between mb-3">
          <div class="font-semibold text-emerald-400 text-sm flex items-center gap-x-2">
            <i class="fa-solid fa-check"></i>
            <span>Protected query succeeded</span>
          </div>
          <div class="font-mono text-[10px] px-2 py-px rounded bg-emerald-900/30 text-emerald-400 border border-emerald-800/50 tabular-nums">${authDbTodos.length} rows • ${queryMs}ms</div>
        </div>
        <div class="text-xs border border-zinc-800 rounded-xl bg-zinc-950 overflow-hidden divide-y divide-zinc-800 shadow-sm">
          ${rowsHtml || '<div class="px-3 py-3 text-zinc-500">No todos</div>'}
        </div>
        <div class="mt-3 flex items-center justify-between text-[10px]">
          <div class="text-zinc-400">Live state • edits simulate <span class="font-mono text-emerald-300">@require_login</span> + <span class="font-mono text-emerald-300">db.execute()</span></div>
          <button onclick="window.resetAuthDbDemo()" class="px-2 py-0.5 rounded-lg border border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition text-[10px]">Reset</button>
        </div>
        ${authDbLastAction ? `<div class="mt-1.5 text-[10px] text-emerald-500/90">Last action: ${authDbLastAction}</div>` : ''}
      </div>
    `;
  };

  window.toggleSimTodo = function(id, ev) {
    if (ev) { ev.preventDefault(); ev.stopImmediatePropagation(); }
    const todo = authDbTodos.find(t => t.id === id);
    if (!todo) return;
    const wasDone = todo.done;
    todo.done = !todo.done;
    authDbLastAction = `Toggled #${id} "${todo.title}" → ${todo.done ? 'done' : 'pending'}`;
    window.renderAuthDbResults();
  };

  window.addSimTodo = function() {
    const container = document.getElementById('authdb-result');
    if (!container || container.classList.contains('hidden')) {
      window.simulateProtectedQuery();
    }
    const candidates = [
      "Sync with design team on tokens",
      "Update changelog for release",
      "Test edge cases on protected routes",
      "Prepare notes for DB migration"
    ];
    const newTitle = candidates[Math.floor(Math.random() * candidates.length)];
    const newId = authDbTodos.length > 0 ? Math.max(...authDbTodos.map(t => t.id)) + 1 : 1;
    authDbTodos.push({id: newId, title: newTitle, done: false});
    authDbLastAction = `Added new todo via protected action: "${newTitle}"`;
    window.renderAuthDbResults();
  };

  window.clearSimCompleted = function() {
    const container = document.getElementById('authdb-result');
    if (!container || container.classList.contains('hidden')) {
      window.simulateProtectedQuery();
    }
    const before = authDbTodos.length;
    authDbTodos = authDbTodos.filter(t => !t.done);
    const removed = before - authDbTodos.length;
    authDbLastAction = removed > 0 ? `Cleared ${removed} completed todo(s) (protected delete)` : 'No completed to clear';
    window.renderAuthDbResults();
  };

  window.resetAuthDbDemo = function() {
    authDbTodos = [
      {id: 1, title: "Deploy new staging env", done: true},
      {id: 2, title: "Review Grok tool-calling PR", done: false},
      {id: 3, title: "Finalize auth migration docs", done: true}
    ];
    authDbLastAction = 'Reset demo to initial server-fetched state';
    window.renderAuthDbResults();
  };

  window.simulateProtectedQuery = function() {
    const container = document.getElementById('authdb-result');
    if (!container) return;
    if (!authDbTodos || authDbTodos.length === 0) {
      authDbTodos = [
        {id: 1, title: "Deploy new staging env", done: true},
        {id: 2, title: "Review Grok tool-calling PR", done: false},
        {id: 3, title: "Finalize auth migration docs", done: true}
      ];
    }
    authDbLastAction = 'Fetched fresh from protected DB query';
    window.renderAuthDbResults();

    const toast = document.createElement('div');
    toast.className = 'fixed bottom-6 right-6 bg-indigo-600 text-white px-5 py-3 rounded-2xl text-sm z-[999] shadow flex items-center gap-x-2';
    toast.innerHTML = '<i class="fa-solid fa-lock"></i> <span>Auth check + DB query executed (exact @require_login + Database pattern)</span>';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2800);
  };

  window.showRealUsageCode = function() {
    const container = document.getElementById('authdb-result');
    if (!container) return;
    container.classList.remove('hidden');
    container.innerHTML = `
      <div class="p-4 bg-zinc-950 border border-zinc-800 rounded-2xl">
        <div class="flex items-center justify-between mb-2">
          <div class="uppercase tracking-[1px] text-indigo-400 text-[10px]">Real production pattern (from auth_db_todo.py)</div>
          <button onclick="window.renderAuthDbResults()" class="text-[10px] px-2.5 py-1 rounded-xl border border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white transition">← Back to live demo</button>
        </div>
        <div class="font-mono text-[11px] text-zinc-200 leading-[1.5] whitespace-pre overflow-x-auto bg-black/60 border border-zinc-800 p-3 rounded-xl">from clayforge.auth import require_login
from clayforge.db import Database
from clayforge import ui

@app.page("/dashboard")
@require_login
def my_todos(user):
    db = Database("clayforge_crm.db")
    todos = db.query(
        "SELECT id, title, done FROM todos " +
        "WHERE user_id = ? ORDER BY created_at DESC",
        (user["id"],)
    )
    # Render with cf.ui.* or return components
    # Decorator auto-injects the authenticated user</div>
        <div class="mt-3 text-[10px] text-zinc-400">Zero boilerplate. The decorator handles the gate; Database manages connections + safe params.</div>
      </div>
    `;
  };

  // New tool runner demo (added for "few more examples")
  window.runToolDemo = function() {
    const sel = document.getElementById('tool-select');
    const qin = document.getElementById('tool-query');
    const res = document.getElementById('tool-result');
    if (!sel || !qin || !res) return;
    res.classList.remove('hidden');
    const tool = sel.value || 'web_search';
    const query = (qin.value || 'demo query').replace(/</g,'&lt;');
    const ms = (60 + Math.random()*80).toFixed(0);
    res.innerHTML = `
      <div class="p-3 border border-amber-900/60 bg-amber-950/20 rounded-xl">
        <div class="flex items-center gap-2 text-amber-400 text-xs font-medium">
          <i class="fa-solid fa-terminal"></i>
          <span>Tool executed: <span class="font-mono">${tool}</span></span>
        </div>
        <div class="mt-1 text-xs text-zinc-300">Query: ${query}</div>
        <div class="mt-1 text-emerald-400 text-xs">Result: 14 high-signal matches • ${ms}ms (simulated — real version calls @app.api + returns cf.ui.* or JSON for live components)</div>
      </div>`;
  };

  // =====================================================
  // NEW LIVE DEMOS JS (Reactive Form Studio + Dynamic Composer)
  // All self-contained, beautiful, and demonstrate "you can make some pretty cool stuff"
  // =====================================================

  // --- Reactive Form Studio ---
  window.updateReactiveForm = function() {
    const nameEl = document.getElementById('rf-name');
    const typeEl = document.getElementById('rf-type');
    const impactEl = document.getElementById('rf-impact');
    const descEl = document.getElementById('rf-desc');
    const publicEl = document.getElementById('rf-public');

    if (!nameEl || !typeEl) return;

    const name = (nameEl.value || '').trim();
    const typ = typeEl.value;
    const impact = impactEl ? parseInt(impactEl.value, 10) : 7;
    const desc = (descEl ? descEl.value : '').trim();
    const isPublic = publicEl ? publicEl.checked : true;

    // live validation
    const err = document.getElementById('rf-name-err');
    const valid = name.length >= 3;
    if (err) err.classList.toggle('hidden', valid);

    // live payload
    const payload = {
      feature: name || '(untitled)',
      type: typ,
      impact,
      description: desc || '(no description)',
      public: isPublic,
      submitted_at: new Date().toISOString().slice(0,19)
    };
    const payloadEl = document.getElementById('rf-payload');
    if (payloadEl) payloadEl.textContent = JSON.stringify(payload, null, 2);

    // live preview card (looks like a real rendered ClayForge card)
    const preview = document.getElementById('rf-preview');
    if (preview) {
      const typeLabel = typ === 'search' ? 'Search' : typ === 'agent' ? 'Agent' : typ === 'viz' ? 'Viz' : 'Tool';
      preview.innerHTML = `
        <div class="flex items-start justify-between">
          <div>
            <div class="font-semibold text-zinc-100">${name || 'New feature'}</div>
            <div class="text-[10px] text-emerald-400 mt-0.5">${typeLabel} • Impact ${impact}/10</div>
          </div>
          ${isPublic ? '<span class="text-[9px] px-1.5 py-px rounded bg-emerald-900/40 text-emerald-400 border border-emerald-800/50">PUBLIC</span>' : ''}
        </div>
        <div class="mt-2 text-xs text-zinc-400 leading-snug">${desc ? desc.slice(0, 110) + (desc.length > 110 ? '…' : '') : 'Add a description to see it here.'}</div>
        <div class="mt-3 text-[10px] text-zinc-500">This preview updates live as you type — exactly what a real cf.ui form + client state would produce.</div>
      `;
    }

    // also sync the impact number label if present
    const valEl = document.getElementById('rf-impact-val');
    if (valEl) valEl.textContent = impact;
  };

  window.submitReactiveForm = function() {
    const nameEl = document.getElementById('rf-name');
    const success = document.getElementById('rf-success');
    if (!success) return;

    const name = nameEl ? (nameEl.value || 'Untitled feature') : 'Untitled feature';
    success.classList.remove('hidden');
    success.innerHTML = `
      <div class="flex items-center gap-x-2">
        <i class="fa-solid fa-check-circle text-emerald-400"></i>
        <span>Feature request <span class="font-mono text-emerald-300">"${name}"</span> submitted! (simulated @app.api call — real version would persist via Database + notify team)</span>
      </div>
    `;

    // nice toast + optionally drive other demo surfaces if present
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-6 right-6 bg-emerald-600 text-white px-5 py-3 rounded-2xl text-sm z-[999] flex items-center gap-x-2';
    toast.innerHTML = `<i class="fa-solid fa-rocket"></i> <span>Request sent — live state updated</span>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2400);

    // bonus: if the dashboard log exists in the same page, feed it (composition win)
    const log = document.getElementById('dashboard-log');
    if (log) {
      const line = document.createElement('div');
      line.className = 'py-px text-emerald-300/90';
      line.textContent = `[${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}] Feature request submitted: ${name}`;
      log.appendChild(line);
      log.scrollTop = 9999;
    }
  };

  // bootstrap the reactive preview once
  setTimeout(() => { if (typeof window.updateReactiveForm === 'function') window.updateReactiveForm(); }, 60);

  // --- Dynamic Form + Upload Composer ---
  if (!window.__dynamicState) {
    window.__dynamicState = { fields: [], uploads: [] };
  }

  window.addDynamicField = function(kind) {
    const area = document.getElementById('dynamic-form-area');
    if (!area) return;

    const state = window.__dynamicState;
    const id = 'dyn-' + Date.now();

    let html = '';
    if (kind === 'text') {
      html = `<div data-dyn-id="${id}" class="clay-card bg-zinc-900 border border-zinc-700 rounded-2xl p-3 text-xs">
        <div class="flex justify-between mb-1"><span class="text-zinc-400">Text field</span><button onclick="window.removeDynamicField('${id}')" class="text-zinc-500 hover:text-red-400">×</button></div>
        <input placeholder="Enter value..." class="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-3 py-1.5 text-sm">
      </div>`;
      state.fields.push({id, kind: 'text'});
    } else if (kind === 'select') {
      html = `<div data-dyn-id="${id}" class="clay-card bg-zinc-900 border border-zinc-700 rounded-2xl p-3 text-xs">
        <div class="flex justify-between mb-1"><span class="text-zinc-400">Select</span><button onclick="window.removeDynamicField('${id}')" class="text-zinc-500 hover:text-red-400">×</button></div>
        <select class="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-3 py-1.5 text-sm"><option>Option A</option><option>Option B</option></select>
      </div>`;
      state.fields.push({id, kind: 'select'});
    } else if (kind === 'checkbox') {
      html = `<div data-dyn-id="${id}" class="clay-card bg-zinc-900 border border-zinc-700 rounded-2xl p-3 text-xs flex items-center gap-2">
        <input type="checkbox" class="accent-violet-400">
        <span class="text-zinc-300 flex-1">New checkbox option</span>
        <button onclick="window.removeDynamicField('${id}')" class="text-zinc-500 hover:text-red-400">×</button>
      </div>`;
      state.fields.push({id, kind: 'checkbox'});
    } else if (kind === 'upload') {
      html = `<div data-dyn-id="${id}" class="clay-card bg-zinc-900 border border-zinc-700 rounded-2xl p-3 text-xs">
        <div class="flex justify-between mb-1"><span class="text-zinc-400">Attachment slot</span><button onclick="window.removeDynamicField('${id}')" class="text-zinc-500 hover:text-red-400">×</button></div>
        <div class="border border-dashed border-zinc-700 rounded-xl px-3 py-2 text-center text-[10px] text-zinc-500">Drop file for this field</div>
      </div>`;
      state.fields.push({id, kind: 'upload'});
    }

    area.insertAdjacentHTML('beforeend', html);
  };

  window.removeDynamicField = function(id) {
    const el = document.querySelector(`[data-dyn-id="${id}"]`);
    if (el) el.remove();
    if (window.__dynamicState) {
      window.__dynamicState.fields = window.__dynamicState.fields.filter(f => f.id !== id);
    }
  };

  window.clearDynamicForm = function() {
    const area = document.getElementById('dynamic-form-area');
    const gallery = document.getElementById('upload-gallery');
    const res = document.getElementById('dynamic-result');
    if (area) area.innerHTML = '';
    if (gallery) gallery.innerHTML = '';
    if (res) res.classList.add('hidden');
    if (window.__dynamicState) {
      window.__dynamicState.fields = [];
      window.__dynamicState.uploads = [];
    }
  };

  window.simulateUpload = function() {
    const gallery = document.getElementById('upload-gallery');
    if (!gallery) return;
    const state = window.__dynamicState || (window.__dynamicState = {fields:[], uploads:[]});

    const names = ['design-mock.fig', 'grok-prompts.md', 'metrics-2026.csv', 'architecture.png'];
    const name = names[Math.floor(Math.random()*names.length)];
    const uid = 'up-' + Date.now();

    const item = document.createElement('div');
    item.className = 'flex items-center gap-2 text-xs bg-zinc-950 border border-zinc-800 rounded-2xl px-3 py-1';
    item.dataset.uploadId = uid;
    item.innerHTML = `
      <i class="fa-solid fa-file text-violet-400"></i>
      <span class="flex-1 font-mono text-zinc-300">${name}</span>
      <div class="w-16 h-1.5 bg-zinc-800 rounded overflow-hidden"><div class="h-1.5 bg-violet-400 transition-all" style="width:100%"></div></div>
      <button onclick="window.removeUpload('${uid}', this)" class="text-zinc-500 hover:text-red-400 px-1">×</button>
    `;
    gallery.appendChild(item);
    state.uploads.push({id: uid, name});

    // fake progress pulse (looks alive)
    setTimeout(() => {
      const bar = item.querySelector('.bg-violet-400');
      if (bar) bar.style.width = '100%';
    }, 80);
  };

  window.removeUpload = function(uid, btn) {
    const item = btn ? btn.closest('[data-upload-id]') : document.querySelector(`[data-upload-id="${uid}"]`);
    if (item) item.remove();
    if (window.__dynamicState) {
      window.__dynamicState.uploads = window.__dynamicState.uploads.filter(u => u.id !== uid);
    }
  };

  window.exportDynamicSchema = function() {
    const state = window.__dynamicState || {fields: [], uploads: []};
    const schema = {
      fields: state.fields.map(f => ({kind: f.kind})),
      attachments: state.uploads.map(u => u.name),
      generated_at: new Date().toISOString()
    };
    const res = document.getElementById('dynamic-result');
    if (!res) return;
    res.classList.remove('hidden');
    res.innerHTML = `
      <div class="p-3 border border-violet-900/60 bg-violet-950/20 rounded-xl">
        <div class="text-violet-400 text-xs mb-1 font-medium">Exported schema (ready for @app.api)</div>
        <pre class="font-mono text-[10px] text-violet-300/90 whitespace-pre-wrap">${JSON.stringify(schema, null, 2)}</pre>
      </div>
    `;
  };

  window.submitDynamicComposer = function() {
    const state = window.__dynamicState || {fields: [], uploads: []};
    const res = document.getElementById('dynamic-result');
    if (!res) return;
    res.classList.remove('hidden');

    const fieldCount = state.fields.length;
    const uploadCount = state.uploads.length;

    res.innerHTML = `
      <div class="p-3 border border-emerald-900/60 bg-emerald-950/20 rounded-xl">
        <div class="flex items-center gap-x-2 text-emerald-400 text-xs font-medium">
          <i class="fa-solid fa-check"></i>
          <span>Package built &amp; submitted</span>
        </div>
        <div class="mt-1 text-xs text-zinc-300">${fieldCount} dynamic fields • ${uploadCount} attachments • schema validated</div>
        <div class="mt-1.5 text-[10px] text-emerald-300/90">Real version would POST to a protected @app.api, persist via Database, and return a cf.ui success fragment or redirect.</div>
      </div>
    `;

    const toast = document.createElement('div');
    toast.className = 'fixed bottom-6 right-6 bg-violet-600 text-white px-5 py-3 rounded-2xl text-sm z-[999]';
    toast.textContent = `Composer package sent (${fieldCount} fields, ${uploadCount} files)`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2200);
  };

  // initial seed for the composer so it doesn't look empty
  setTimeout(() => {
    const area = document.getElementById('dynamic-form-area');
    if (area && area.children.length === 0 && typeof window.addDynamicField === 'function') {
      window.addDynamicField('text');
      window.addDynamicField('select');
    }
  }, 120);
})();
</script>"""
