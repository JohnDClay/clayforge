"""
ClayForge Example 07 — Multi-Agent Team Workbench (Complete Workflow)

This example demonstrates a production-style, end-to-end multi-agent
orchestration dashboard built around the hero AgentCanvas component.

What makes it advanced & educational:
- Prominent, fully interactive AgentCanvas with live thought streaming,
  collaboration graph (Mermaid), play/pause, human inject, and reset.
- Rich task intake form + configurable team metadata.
- "Launch Mission" drives a realistic, context-aware simulation that
  feeds thoughts into the canvas AND populates a live results DataTable.
- Integrated GrokChat "Mission Control" — chat messages can inject
  guidance directly into the running agent team (human-in-the-loop).
- Deliverables & audit log using DataTable (when available) or elegant
  fallback cards. Everything stays in sync.
- Shows real patterns for: steering agents, capturing structured outputs,
  mixing AgentCanvas + GrokChat + DataTable in one beautiful surface.

This is the kind of interface AI product teams actually ship.

Run:
    python examples/07_agent_team_workbench.py

CLI (recommended for development):
    clayforge run --app examples.07_agent_team_workbench:app

Discoverability:
- `clayforge showcase` — polished marketing view with GrokChat in its own tab and the Research Swarm (AgentCanvas) in the Agent Vision tab only (nice titles first, full interactive, zero pollution of other sections).
- `clayforge gallery` — deepest live experience (Command Center driving multiple simultaneous canvases + Grok instances via the public update_agent_status / add_event API).

No extra dependencies required for the core AgentCanvas + GrokChat experience.
Install "clayforge[viz]" for the optional structured deliverables table.
"""

from __future__ import annotations

import datetime
import random
import threading
from typing import Any

import clayforge as cf
from clayforge.grok import AgentCanvas, GrokChat

# Optional viz for the deliverables table
try:
    from clayforge.components.viz import DataTable

    HAS_VIZ = True
except Exception:
    HAS_VIZ = False
    DataTable = None  # type: ignore


app = cf.App(
    title="ClayForge • Agent Team Workbench",
    description="Full multi-agent orchestration surface with live canvas, steering chat, and structured outputs",
)


# ------------------------------------------------------------------
# Shared live state for the entire workbench
# ------------------------------------------------------------------
STATE: dict[str, Any] = {
    "current_task": "Analyze Q2 2026 competitive landscape for AI-native devtools and produce a prioritized GTM playbook.",
    "team": [
        {"name": "Researcher", "role": "Deep research & sources", "color": "#6366f1"},
        {"name": "WebSearch", "role": "Tool calling & synthesis", "color": "#10b981"},
        {"name": "Critic", "role": "Contradictions & quality", "color": "#f59e0b"},
        {"name": "Synthesizer", "role": "Final playbook & artifacts", "color": "#8b5cf6"},
    ],
    "deliverables": [],
    "activity_log": [],
    "mission_running": False,
}


def _log_activity(agent: str, message: str):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = {"time": ts, "agent": agent, "message": message}
    STATE["activity_log"].append(entry)
    if len(STATE["activity_log"]) > 30:
        STATE["activity_log"] = STATE["activity_log"][-30:]
    return entry


def _add_deliverable(title: str, owner: str, content: str, confidence: float = 0.92):
    item = {
        "id": f"ART-{100 + len(STATE['deliverables'])}",
        "title": title,
        "owner": owner,
        "summary": content[:140] + ("..." if len(content) > 140 else ""),
        "confidence": round(confidence * 100),
        "ts": datetime.datetime.now().strftime("%H:%M"),
    }
    STATE["deliverables"].append(item)
    _log_activity(owner, f"Delivered: {title}")
    return item


# ------------------------------------------------------------------
# Live component references (for cross-component steering)
# ------------------------------------------------------------------
_live: dict[str, Any] = {}  # 'canvas', 'table', 'chat'


def _push_deliverables_table():
    if "table" in _live and _live["table"] and HAS_VIZ:
        try:
            _live["table"].update_data(STATE["deliverables"])
        except Exception:
            pass


# ------------------------------------------------------------------
# Enhanced multi-agent simulation driven by the workbench task
# This is deliberately rich so you see a "real" workflow in action.
# ------------------------------------------------------------------
def _run_agent_mission(canvas: AgentCanvas, task: str):
    """Background simulation that feels like a serious agent swarm."""
    STATE["mission_running"] = True
    _log_activity("System", f"Mission launched: {task[:60]}...")

    steps = [
        ("Researcher", f"Breaking down the query: '{task[:55]}...' into research vectors."),
        ("WebSearch", "Querying recent funding announcements, review sites, and G2 data."),
        ("Researcher", "Found 7 high-signal primary sources from the last 90 days."),
        ("Critic", "Flagged two contradictory claims about pricing models — escalating."),
        ("WebSearch", "Re-querying primary sources with tighter date filters."),
        ("Critic", "Validated data. One claim was marketing spin; corrected in shared context."),
        ("Synthesizer", "Drafting GTM playbook sections: positioning, ICP, channel mix."),
        ("Researcher", "Pulling supporting case studies from similar AI devtool launches."),
        ("Synthesizer", "Finalizing prioritized recommendations + risk matrix."),
    ]

    for agent, text in steps:
        if not STATE["mission_running"]:
            return
        canvas.add_thought(agent, text)

        # Occasionally produce structured deliverables (the real output of the team)
        if "Researcher" in agent and random.random() > 0.55:
            _add_deliverable(
                "Competitive source digest",
                agent,
                "Summarized 14 key data points across 7 vendors.",
            )
        if "Synthesizer" in agent:
            _add_deliverable(
                "Draft GTM narrative",
                agent,
                "Positioning statement + 3 launch angles for the Q3 campaign.",
            )

        _push_deliverables_table()
        # Small human-like pauses
        import time

        time.sleep(0.82 + random.random() * 0.6)

    if STATE["mission_running"]:
        canvas.add_thought(
            "Synthesizer", "All agents aligned. Full playbook + 4 artifacts ready for review."
        )
        _add_deliverable(
            "Final GTM Playbook",
            "Synthesizer",
            "Executive-ready 9-page playbook with OKRs and channel calendar.",
            0.96,
        )
        _push_deliverables_table()
        _log_activity("System", "Mission complete — team awaiting human guidance.")

    STATE["mission_running"] = False
    # The canvas itself manages its own play button label via its internal logic


# ------------------------------------------------------------------
# Handlers wired to the UI controls
# ------------------------------------------------------------------
def _launch_mission():
    canvas = _live.get("canvas")
    if not canvas:
        print("[AgentWorkbench] No canvas reference yet.")
        return

    task = STATE["current_task"]
    canvas.add_thought("System", f"New mission accepted: {task[:70]}...")

    # Start the rich simulation (non-blocking for the UI thread)
    threading.Thread(target=_run_agent_mission, args=(canvas, task), daemon=True).start()

    # Immediately give nice feedback in the chat if present
    chat = _live.get("chat")
    if chat:
        chat.add_assistant_message(
            "Mission launched. The team is now collaborating live. You can inject guidance at any time."
        )


def _inject_guidance(text: str):
    """Used by both the Inject button and the GrokChat mission control."""
    canvas = _live.get("canvas")
    if canvas:
        canvas.add_thought("Human", text)
        canvas.add_thought("Researcher", "Adjusting research scope based on new direction...")
        _log_activity("Human", f"Injected: {text[:80]}")

    # Also surface in deliverables as a human steer record
    _add_deliverable("Human steer recorded", "Human", text)
    _push_deliverables_table()


def _reset_workbench():
    STATE["deliverables"].clear()
    STATE["activity_log"].clear()
    STATE["mission_running"] = False

    canvas = _live.get("canvas")
    if canvas:
        # The canvas has its own reset that also updates the UI
        # We simulate a button press effect by calling its handler logic indirectly
        canvas.thoughts = [
            {
                "agent": "System",
                "text": "Workbench reset. Ready for new mission.",
                "ts": datetime.datetime.now().strftime("%H:%M"),
            }
        ]
        canvas.is_running = False
        if hasattr(canvas, "_play_btn"):
            canvas._play_btn.label = "▶ Start"
        try:
            canvas._push_update()
        except Exception:
            pass

    _push_deliverables_table()
    print("[AgentWorkbench] Workbench fully reset.")


# ------------------------------------------------------------------
# The page — a complete, impressive agent operations surface
# ------------------------------------------------------------------
@app.page("/")
def agent_workbench():
    cf.ui.title("Agent Team Workbench")
    cf.ui.subtitle(
        "Live multi-agent collaboration • Human steering • Structured deliverables — all reactive"
    )

    # Mission briefing header
    with cf.ui.row(gap="4"):
        with cf.ui.card(title="Current Mission", classes="flex-[3]"):
            task_input = cf.ui.text_input(
                "Mission objective",
                value=STATE["current_task"],
                classes="text-base",
            )

            def commit_task():
                STATE["current_task"] = task_input.value or STATE["current_task"]
                print(f"[AgentWorkbench] Task updated: {STATE['current_task'][:50]}")

            cf.ui.button("Update Mission Brief", on_click=commit_task, variant="ghost", size="sm")

        with cf.ui.card(title="Team Status", classes="flex-1"):
            cf.ui.badge("4 agents online", variant="success")
            cf.ui.text("Graph: Mermaid live • Thoughts: streaming", size="sm")
            cf.ui.text("Human-in-the-loop: enabled", size="sm")

    cf.ui.divider()

    # ------------------------------------------------------------------
    # THE STAR: Full-width live AgentCanvas
    # ------------------------------------------------------------------
    with cf.ui.card(classes="p-0 overflow-hidden"):
        canvas = AgentCanvas(
            agents=STATE["team"],
            title="Live Agent Collaboration Canvas",
            height="560px",
        )
        _live["canvas"] = canvas

    # Quick mission controls under the canvas
    with cf.ui.row(gap="4"):
        cf.ui.button(
            "▶ Launch Full Mission", on_click=_launch_mission, variant="primary", classes="px-8"
        )

        inject_input = cf.ui.text_input(
            "Inject guidance for the team...",
            value="Prioritize European funding data from 2025-2026 only",
            classes="flex-1",
        )

        def do_inject():
            _inject_guidance(inject_input.value or "Focus on recent data")

        cf.ui.button("Inject into Team", on_click=do_inject, variant="secondary")

        cf.ui.button("Reset Everything", on_click=_reset_workbench, variant="ghost")

    cf.ui.divider()

    # ------------------------------------------------------------------
    # STRUCTURED OUTPUTS + MISSION CONTROL CHAT (side-by-side)
    # ------------------------------------------------------------------
    with cf.ui.row(gap="6"):
        # Deliverables (the actual artifacts the agents produce)
        with cf.ui.card(
            classes="flex-[1.6] p-0 overflow-hidden",
            title="Agent Deliverables",
            subtitle="Live structured outputs from the swarm",
        ):
            if HAS_VIZ and DataTable:
                table = DataTable(
                    STATE["deliverables"],
                    title="Structured Artifacts (sortable • filterable)",
                    height="320px",
                    searchable=True,
                    sortable=True,
                )
                _live["table"] = table
            else:
                # Elegant fallback using basic components
                if STATE["deliverables"]:
                    for d in STATE["deliverables"][-5:]:
                        with cf.ui.row(gap="3"):
                            cf.ui.badge(d["owner"], variant="info")
                            cf.ui.text(f"{d['title']} — {d['summary']}", size="sm")
                else:
                    cf.ui.text(
                        "Launch a mission to see agents produce structured deliverables here.",
                        size="sm",
                    )
                    cf.ui.markdown(
                        "Each agent can call <b>_add_deliverable()</b> in real code to stream real JSON artifacts."
                    )

        # Human oversight chat — can directly steer the canvas
        with cf.ui.card(
            classes="flex-1 p-0 overflow-hidden",
            title="Mission Control (GrokChat)",
            subtitle="Chat here to inject live guidance",
        ):

            def mission_control_handler(chat: GrokChat, msg: str):
                # This is the powerful pattern: chat drives the agent system
                _inject_guidance(f"[via Chat] {msg}")

                # Give a helpful assistant reply
                import time

                reply = "Guidance injected into the live canvas. The team is re-prioritizing. Watch the Thought Stream."
                for chunk in [reply[i : i + 9] for i in range(0, len(reply), 9)]:
                    chat.stream_append(chunk)
                    time.sleep(0.03)
                chat.flush()

            chat = GrokChat(
                model="grok-mission-control",
                height="320px",
                placeholder="Tell the team to focus on X, ignore Y, add a new angle...",
                on_message=mission_control_handler,
            )
            _live["chat"] = chat

    # ------------------------------------------------------------------
    # Activity / Audit log (another live-updating surface)
    # ------------------------------------------------------------------
    cf.ui.divider()

    with cf.ui.card(
        title="Full Activity Log", subtitle="Every thought, steer, and artifact captured"
    ):
        if STATE["activity_log"]:
            log_text = "<br>".join(
                f"<span class='font-mono text-[10px] text-zinc-500'>{e['time']}</span> "
                f"<span style='color:#64748b'>{e['agent']}:</span> {e['message']}"
                for e in STATE["activity_log"][-12:]
            )
            cf.ui.markdown(log_text)
        else:
            cf.ui.text(
                "Activity will stream here as soon as you launch a mission or inject guidance."
            )

        cf.ui.button(
            "Clear Log",
            on_click=lambda: (STATE["activity_log"].clear(), print("[AgentWorkbench] Log cleared")),
            variant="ghost",
            size="sm",
        )

    # Educational footer
    cf.ui.footer(
        "Example 07 • Complete Agent Team Workflow • AgentCanvas + GrokChat steering + live DataTable outputs • "
        "Threaded simulation + real cross-component communication"
    )

    return cf.ui.column()


if __name__ == "__main__":
    print("Starting ClayForge Multi-Agent Team Workbench...")
    print("Watch the AgentCanvas come alive when you click Launch or Inject.")
    print("The GrokChat on the right can directly steer the running team.")
    app.run()
