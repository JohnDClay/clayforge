"""
Showcase Sections

Each file here is responsible for rendering one major demo experience.
They should prefer real ClayForge components (cf.ui.*, GrokChat, AgentCanvas, PlotlyChart, etc.)
over raw strings wherever possible.
"""

from .agents import render_agents
from .dashboard import render_dashboard
from .forms import render_forms
from .grok import render_grok
from .overview import render_overview
from .theming import render_theming

__all__ = [
    "render_overview",
    "render_grok",
    "render_dashboard",
    "render_agents",
    "render_forms",
    "render_theming",
]
