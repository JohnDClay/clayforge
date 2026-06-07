# minimal_starter.py
# ClayForge Minimal Starter (copy-paste ready foundation)
#
# Run:
#   python minimal_starter.py
#
# Or after `pip install clayforge`:
#   clayforge showcase          # <-- THE hero demo (real full beautiful showcase)
#   clayforge new myapp && cd myapp && clayforge run

import os

import clayforge as cf
from clayforge.grok import AgentCanvas, GrokChat

app = cf.App(
    title="My ClayForge App",
    description="Beautiful reactive UIs with zero boilerplate — powered by ClayForge + Grok",
)

@app.page("/")
def main_page():
    cf.ui.title("Welcome to My ClayForge App")
    cf.ui.subtitle("Pure Python • Stunning defaults • First-class Grok")

    cf.ui.markdown(
        "Edit this file, save, and the UI updates instantly over WebSocket. "
        "No HTML, CSS, or JavaScript required for most apps."
    )

    cf.ui.divider()

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="Quick Interactive Demo", classes="flex-1"):
            cf.ui.text("Click the button — server roundtrip + live UI update.", size="sm")

            counter = {"value": 0}

            def bump():
                counter["value"] += 1
                cf.ui.success(f"Clicked {counter['value']} times!")

            cf.ui.button("Click me", on_click=bump, variant="primary")

            cf.ui.divider(classes="my-3")
            cf.ui.text("Try the Grok surfaces in the full showcase:", size="sm")
            cf.ui.markdown("`clayforge showcase` — dedicated tabs for GrokChat + real AgentCanvas Research Swarm.")

        with cf.ui.card(title="Live Grok Chat", classes="flex-1"):
            GrokChat(
                api_key=os.getenv("XAI_API_KEY"),
                placeholder="Ask Grok anything...",
                height="420px",
            )

    cf.ui.divider()

    with cf.ui.card(title="Multi-Agent Canvas (real AgentCanvas component)"):
        # This uses the exact public API you get in your own apps (see examples/04_multi_agent_vision.py)
        canvas = AgentCanvas(
            agents=[
                {"name": "Researcher", "role": "Deep research & sources", "color": "#6366f1"},
                {"name": "Coder", "role": "Implementation", "color": "#10b981"},
                {"name": "Reviewer", "role": "Quality & critique", "color": "#f59e0b"},
            ],
            title="Agent Team",
            height="420px",
            show_controls=True,
        )
        # Seed a little activity using the public API (exactly like production usage)
        canvas.update_agent_status("Researcher", "researching", "3 sources")
        canvas.add_thought("Researcher", "Found strong signals on modern Python UI patterns.")

    cf.ui.footer("ClayForge • MIT • Pure Python • 2026")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)