"""
showcase_demo.py
================

This file is automatically created for you by `clayforge showcase`
when you run it after a plain `pip install clayforge`.

It launches the **full, official ClayForge Showcase** — the exact rich,
beautiful, multi-tab hero demo that the ClayForge team uses and maintains.

What you get:
- Dedicated GrokChat tab (real component + self-contained visual demo)
- Agent Vision tab with the real framework-native Research Swarm
  (AgentCanvas + public API: update_agent_status, add_event, add_thought,
   exactly as shown in examples/04_multi_agent_vision.py)
- Live dashboards with mutations, forms, theming explorer, etc.
- All the "wow" we want people to see first.

No separate gallery. The showcase *is* our showcase.

How to run:
    python showcase_demo.py
    # or simply: clayforge showcase   (it will (re)create this file + launch)

You can edit this file, commit it, or copy patterns into your own apps.
The heavy lifting (layout, sections, pre-seeded AgentCanvas, custom JS/CSS
enhancements, etc.) lives in the installed package under clayforge.showcase.

For the absolute latest source version of this demo, clone the repo and run
from the source tree:
    python -m clayforge showcase

Enjoy — this is what ClayForge can do out of the box.
"""

import os
import sys
from pathlib import Path

from clayforge.core.server import set_current_app

# Import the real, full, maintained showcase app from the package.
# This is the exact same rich experience you get when running from a git clone.
try:
    from clayforge.showcase import app as showcase_app
except ImportError as e:
    print(
        "ERROR: Could not load the full ClayForge Showcase from the installed package.\n"
        "Make sure you have a recent `pip install clayforge` (or `pip install -e .` from source).\n"
        f"Original error: {e}"
    )
    sys.exit(1)

# Optional: let the user override the title/description locally if they want.
# showcase_app.title = "My Custom Showcase"
# showcase_app.description = "The full ClayForge experience, customized."

# Mount the rich app so the central server + WebSocket machinery is used.
set_current_app(showcase_app)

# Also set the env var so reloader child processes (if any) pick it up.
os.environ["CLAYFORGE_APP"] = str(Path(__file__).with_suffix("")) + ":showcase_app"

if __name__ == "__main__":
    # Direct run support (python showcase_demo.py)
    # For the normal `clayforge showcase` or `clayforge run --app ...` path,
    # the CLI already handles mounting + uvicorn.
    showcase_app.run(host="127.0.0.1", port=8000)
