"""
ClayForge Example 04 — Production Multi-Agent Orchestration with AgentCanvas

This is the canonical, copy-paste-ready example for realistic multi-agent teams.

WHAT IT DEMONSTRATES (production patterns):
- AgentCanvas with the full public drive API:
    update_agent_status(), add_thought(), add_event()
- Realistic 4-agent pipeline: Researcher → WebSearch → Critic → Synthesizer
- Live dynamic Mermaid graph + per-agent status pills + rich tool cards
- Fully reactive WS updates — feels identical to GrokChat
- Integrated GrokChat as "Mission Brain" for human-in-the-loop steering
- Orchestration runnable from background threads (realistic for agents)
- Zero extra dependencies. Works beautifully with or without XAI_API_KEY.

Run:
    python examples/04_multi_agent_vision.py
    # or
    clayforge run --app examples.04_multi_agent_vision:app

Then click Launch Mission. Watch the canvas come alive with real status changes,
tool events, and graph highlights. Use the chat or Inject button to steer live.

For the richest live experience of the full public API (multiple simultaneous canvases + Command Center controls), run:
    clayforge gallery
and use the "Demo Full AgentCanvas API" button in the Command Center.

Discoverability in the surfaces:
- `clayforge showcase` — clean dedicated tab: the full interactive Research Swarm (AgentCanvas with update_agent_status + add_event + dynamic graph) appears ONLY in the "Agent Vision" tab (nice title + prose first, full controls). Zero leakage to other sections. GrokChat is isolated to its own tab.
- `clayforge gallery` — deepest (two simultaneous AgentCanvases + cross-mutation from Command Center using the exact production public API).
"""

from __future__ import annotations

import datetime
import os
import threading
import time
from typing import Any

import clayforge as cf
from clayforge.grok import AgentCanvas, GrokChat

app = cf.App(
    title="ClayForge • Multi-Agent Orchestration",
    description="Realistic 4-agent research→critique→synthesize pipeline with live AgentCanvas + GrokChat brain",
)


# ------------------------------------------------------------------
# Shared state + realistic team definition (production pattern)
# ------------------------------------------------------------------
TEAM = [
    {"name": "Researcher", "role": "Deep research & primary sources", "color": "#6366f1"},
    {"name": "WebSearch", "role": "Tool calling & data gathering", "color": "#10b981"},
    {"name": "Critic", "role": "Contradictions, quality & risk", "color": "#f59e0b"},
    {"name": "Synthesizer", "role": "Consensus & final artifacts", "color": "#8b5cf6"},
]

STATE: dict[str, Any] = {
    "mission": "Analyze 2026 AI-native developer tooling landscape and produce a prioritized GTM playbook with 3 launch angles.",
    "running": False,
    "artifacts": [],
}


_live: dict[str, Any] = {}  # canvas + chat cross-wiring


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def _add_artifact(owner: str, title: str, summary: str):
    item = {
        "ts": _now(),
        "owner": owner,
        "title": title,
        "summary": summary[:180],
    }
    STATE["artifacts"].append(item)
    if len(STATE["artifacts"]) > 8:
        STATE["artifacts"] = STATE["artifacts"][-8:]


# ------------------------------------------------------------------
# The real orchestration loop — uses the NEW production AgentCanvas API
# This is the pattern you copy into your own agents.
# ------------------------------------------------------------------
def _orchestrate_mission(canvas: AgentCanvas, task: str, chat: GrokChat | None = None):
    """Realistic sequential + parallel-ish agent swarm with live viz."""
    STATE["running"] = True
    canvas.add_thought("System", f"Mission accepted: {task[:65]}...")

    # === PHASE 1: Researcher (uses status + thoughts + events) ===
    canvas.update_agent_status("Researcher", "thinking", "Decomposing query into vectors")
    canvas.add_thought(
        "Researcher",
        "Breaking task into 4 research vectors: vendors, funding, G2 signals, devex reviews.",
    )
    time.sleep(0.65)

    canvas.update_agent_status("Researcher", "researching", "Pulling 2025-2026 primary sources")
    canvas.add_thought("Researcher", "Identified 9 high-signal sources from last 120 days.")
    time.sleep(0.55)

    # Real tool event (this is what makes it production-grade)
    canvas.add_event(
        "Researcher",
        "tool",
        "Executed targeted search",
        tool_name="web_search",
        args={"query": "AI devtools funding 2025 2026", "limit": 20},
        result="14 curated reports + 3 analyst notes. Confidence 87%.",
    )
    canvas.update_agent_status("Researcher", "complete", "Handed 14 sources to WebSearch")
    _add_artifact(
        "Researcher",
        "Source Digest v1",
        "14 primary sources tagged with signal strength and recency.",
    )

    # === PHASE 2: WebSearch (tool-heavy agent) ===
    canvas.update_agent_status("WebSearch", "tool_use", "Running parallel retrieval")
    canvas.add_thought(
        "WebSearch", "Querying G2, Crunchbase recent rounds, and dev community forums..."
    )
    time.sleep(0.7)

    canvas.add_event(
        "WebSearch",
        "tool",
        "Multi-source retrieval complete",
        tool_name="parallel_fetch",
        args={"sources": ["g2", "crunchbase", "hn", "reddit"]},
        result="Cross-referenced 27 data points. 4 outliers flagged for Critic.",
    )
    canvas.update_agent_status("WebSearch", "complete")
    _add_artifact(
        "WebSearch", "Raw Data Pack", "Structured JSON of vendor metrics + funding events."
    )

    # === PHASE 3: Critic (quality gate) ===
    canvas.update_agent_status("Critic", "critiquing", "Scanning for contradictions")
    canvas.add_thought(
        "Critic", "Found conflicting claims on pricing models between two vendors. Escalating."
    )
    time.sleep(0.6)

    canvas.add_event("Critic", "log", "Re-verified against primary SEC filings and earnings calls.")
    canvas.add_thought("Critic", "One claim was marketing spin. Corrected in shared context.")
    canvas.update_agent_status("Critic", "complete", "Quality gate passed")
    _add_artifact("Critic", "Risk Register", "2 corrected claims + 1 high-priority watch item.")

    # === PHASE 4: Synthesizer (final output) ===
    canvas.update_agent_status("Synthesizer", "synthesizing", "Weaving consensus playbook")
    canvas.add_thought(
        "Synthesizer", "All agents aligned. Drafting executive GTM with 3 concrete launch angles."
    )
    time.sleep(0.75)

    canvas.add_event(
        "Synthesizer",
        "tool",
        "Final artifact generation",
        tool_name="report_writer",
        result="9-page playbook + OKR matrix + channel calendar ready.",
    )
    canvas.update_agent_status("Synthesizer", "complete", "Mission deliverables ready")
    canvas.add_thought(
        "Synthesizer", "Full GTM Playbook + 4 artifacts produced. Ready for human review."
    )

    _add_artifact(
        "Synthesizer",
        "GTM Playbook 2026",
        "Positioning, ICP, 3 launch angles, risk matrix, 90-day calendar.",
    )

    # Notify via chat brain if present (beautiful cross-component pattern)
    if chat:
        chat.add_assistant_message(
            "Orchestration complete. The team produced a full playbook and artifacts. Inject guidance to iterate."
        )

    STATE["running"] = False
    canvas.add_thought(
        "System", "Mission complete — all agents idle. Use chat or inject to steer next run."
    )


def _launch_mission():
    canvas = _live.get("canvas")
    chat = _live.get("chat")
    if not canvas:
        return

    task = STATE["mission"]
    if not STATE["running"]:
        threading.Thread(
            target=_orchestrate_mission,
            args=(canvas, task, chat),
            daemon=True,
        ).start()

    if chat:
        chat.add_user_message(f"[Mission] {task[:55]}...")
        chat.add_assistant_message(
            "Team is now executing the full research → critique → synthesize pipeline. Watch the live canvas."
        )


def _inject_steer(text: str):
    canvas = _live.get("canvas")
    chat = _live.get("chat")
    if canvas:
        canvas.add_thought("Human", text)
        # Show the new API in action
        canvas.update_agent_status("Researcher", "researching", "Re-scoping per human steer")
        canvas.add_event("Critic", "log", f"Human guidance applied: {text[:70]}")
    if chat:
        chat.add_assistant_message("Steer received and injected into live team. Canvas updated.")


def _reset_all():
    STATE["artifacts"].clear()
    STATE["running"] = False
    canvas = _live.get("canvas")
    if canvas:
        canvas.clear_thoughts()
        canvas.add_thought("System", "Full reset. Ready for new mission.")
        for agent in TEAM:
            canvas.update_agent_status(agent["name"], "idle")
    chat = _live.get("chat")
    if chat:
        chat.add_assistant_message("Workbench reset. New mission ready.")


# ------------------------------------------------------------------
# The page — stunning, self-documenting, production-ready surface
# ------------------------------------------------------------------
@app.page("/")
def multi_agent_orchestration():
    cf.ui.title("Multi-Agent Orchestration — Live")
    cf.ui.subtitle(
        "Research → Critique → Synthesize pipeline with real-time AgentCanvas + GrokChat brain"
    )

    # Mission briefing
    with cf.ui.card(title="Current Mission Brief", classes="mb-4"):
        task_input = cf.ui.text_input(
            "Objective",
            value=STATE["mission"],
            classes="text-sm",
        )

        def save_task():
            STATE["mission"] = task_input.value or STATE["mission"]

        cf.ui.button("Update Brief", on_click=save_task, variant="ghost", size="sm")

    # THE STAR: Live AgentCanvas (using the new rich API under the hood)
    with cf.ui.card(classes="p-0 overflow-hidden"):
        canvas = AgentCanvas(
            agents=TEAM,
            title="Live 4-Agent Research Swarm",
            height="540px",
        )
        _live["canvas"] = canvas

    # Launch + steer controls
    with cf.ui.row(gap="3", classes="mt-3"):
        cf.ui.button(
            "🚀 Launch Full Mission", on_click=_launch_mission, variant="primary", classes="px-6"
        )

        steer_input = cf.ui.text_input(
            "Inject human guidance...",
            value="Emphasize European Series-B activity and devex NPS signals",
            classes="flex-1",
        )

        def do_steer():
            val = steer_input.value or "Focus on recent European activity"
            _inject_steer(val)

        cf.ui.button("Inject into Team", on_click=do_steer, variant="secondary")
        cf.ui.button("Reset", on_click=_reset_all, variant="ghost")

    cf.ui.divider()

    # Side-by-side: GrokChat as brain + live artifacts
    with cf.ui.row(gap="5"):
        # Mission Control GrokChat — real steering brain (api_key path if present)
        with cf.ui.card(
            classes="flex-1 p-0 overflow-hidden",
            title="Mission Brain (GrokChat)",
            subtitle="Chat here — messages steer the live agent canvas",
        ):
            xai = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")

            def brain_handler(chat: GrokChat, msg: str):
                _inject_steer(f"[via Brain] {msg}")
                # Simple helpful reply (real streaming if key present via default path)
                reply = "Guidance injected into the swarm. Watch Researcher and Critic re-prioritize on the canvas."
                chat.add_assistant_message(reply)

            chat = GrokChat(
                model="grok-4.3",
                api_key=xai,
                height="280px",
                placeholder="Tell the team to focus on X, ignore Y, add a new data source...",
                on_message=brain_handler,
                system="You are the mission commander for a 4-agent research team visualized on an AgentCanvas. Your chat messages are injected live as human steer events.",
            )
            _live["chat"] = chat

        # Live artifacts (what real agents actually produce)
        with cf.ui.card(
            classes="flex-1",
            title="Live Agent Artifacts",
            subtitle="Structured outputs streamed by the swarm",
        ):
            if STATE["artifacts"]:
                for art in STATE["artifacts"][-5:]:
                    with cf.ui.row(gap="2"):
                        cf.ui.badge(art["owner"], variant="info")
                        cf.ui.text(f"{art['title']}: {art['summary']}", size="sm")
            else:
                cf.ui.text(
                    "Launch a mission to see the agents produce real structured artifacts.",
                    size="sm",
                )
                cf.ui.markdown(
                    "In production code you would call <b>_add_artifact()</b> (or write to your DB) "
                    "from inside the real agent implementations while simultaneously calling the "
                    "canvas.update_* / add_* methods for visualization."
                )

    # Educational copy-paste block
    cf.ui.divider()
    with cf.ui.card(title="Copy-Paste Pattern: Real Orchestration Loop"):
        cf.ui.markdown(
            "```python\n"
            "canvas = AgentCanvas(agents=your_team)\n\n"
            "def my_agent_loop(task):\n"
            "    canvas.update_agent_status('Researcher', 'thinking', 'Planning...')\n"
            "    canvas.add_thought('Researcher', 'Starting deep research...')\n"
            "    # ... call GrokClient or your tools ...\n"
            "    canvas.add_event('Researcher', 'tool', ..., tool_name='search', args=..., result=...)\n"
            "    canvas.update_agent_status('Researcher', 'complete')\n"
            "    # continue pipeline for Critic, Synthesizer etc.\n"
            "```"
        )
        cf.ui.text(
            "All three methods (update_agent_status, add_thought, add_event) trigger instant WS updates. "
            "Call them from any thread or async context. This is the 'it just works' bar for multi-agent UIs.",
            size="sm",
        )

    cf.ui.footer(
        "Example 04 • Production Multi-Agent Orchestration • AgentCanvas new API (status + events + dynamic graph) + GrokChat brain • Pure Python, zero hard deps"
    )

    return cf.ui.column()


if __name__ == "__main__":
    print("Starting ClayForge Multi-Agent Orchestration demo...")
    if os.getenv("XAI_API_KEY"):
        print("  ✓ XAI_API_KEY detected — GrokChat brain will stream real tokens.")
    else:
        print("  i  No XAI key — GrokChat runs in high-fidelity simulation (still gorgeous).")
    app.run()
