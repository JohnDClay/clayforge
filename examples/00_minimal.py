"""
ClayForge Minimal Starter (examples/00_minimal.py)

The absolute smallest "hello world" that still shows the two signature Grok features:
- GrokChat (real streaming when XAI_API_KEY is set, otherwise beautiful simulation)
- AgentCanvas (real component + public API: update_agent_status / add_thought / add_event)

Run directly:
    python examples/00_minimal.py

Or after pip install:
    pip install "clayforge[viz,grok]"
    python -m clayforge run --app examples.00_minimal:app

See also:
- clayforge showcase          # the full polished multi-tab hero demo
- examples/03_grok_chat.py
- examples/04_multi_agent_vision.py   # production 4-agent patterns + rich tool cards
"""

import os

import clayforge as cf
from clayforge.grok import AgentCanvas, GrokChat

app = cf.App(
    title="ClayForge Minimal",
    description="The smallest possible app that still demonstrates real GrokChat + AgentCanvas",
)


@app.page("/")
def main_page():
    cf.ui.title("ClayForge — Minimal Starter")
    cf.ui.subtitle("Pure Python. Zero boilerplate. Grok-native.")

    cf.ui.markdown(
        "This is the smallest file that still gives you the two headline Grok experiences "
        "in a real reactive UI. Edit anything and save — the browser updates live."
    )

    cf.ui.divider()

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="GrokChat", classes="flex-1"):
            cf.ui.text(
                "Drop-in component. Set XAI_API_KEY for real token-by-token streaming from xAI.",
                size="sm",
            )
            GrokChat(
                api_key=os.getenv("XAI_API_KEY"),
                placeholder="Ask anything...",
                height="420px",
            )

        with cf.ui.card(title="AgentCanvas (real component)", classes="flex-1"):
            cf.ui.text(
                "Uses the exact public API you will use in your own apps (see examples/04).",
                size="sm",
            )

            canvas = AgentCanvas(
                agents=[
                    {"name": "Researcher", "role": "Gathering data", "color": "#6366f1"},
                    {"name": "Synthesizer", "role": "Turning data into artifacts", "color": "#8b5cf6"},
                ],
                title="Tiny Agent Team",
                height="420px",
                show_controls=True,
            )

            # Demonstrate the production public API right here (exactly like examples/04)
            canvas.update_agent_status("Researcher", "researching", "2 sources")
            canvas.add_thought("Researcher", "Found strong 2026 Python UI patterns.")
            canvas.add_event(
                "Researcher",
                "tool",
                "search",
                tool_name="web_search",
                result="High signal results on reactive Python frameworks.",
            )

    cf.ui.divider()

    with cf.ui.card(title="Next steps (copy these commands)"):
        cf.ui.markdown(
            """
**Explore the real showcase (recommended first thing):**
```bash
pip install clayforge
clayforge showcase          # the full beautiful hero demo (real AgentCanvas Research Swarm, GrokChat, etc.)
```

**Scaffold a full project:**
```bash
clayforge new myapp
cd myapp
clayforge run
```

**Production patterns:**
- `examples/03_grok_chat.py` — real streaming + on_message handlers
- `examples/04_multi_agent_vision.py` — full 4-agent pipeline with rich tool cards
"""
        )

    cf.ui.footer("ClayForge • MIT • 2026")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
