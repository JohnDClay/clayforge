"""
ClayForge Official Showcase

A single beautiful, self-contained experience that demonstrates what is possible
with pure Python and the ClayForge framework.

Run with:
    python -m clayforge showcase
    # or
    python -m clayforge run --app showcase:app
"""

from . import layout, sections, state
from .app import app

__all__ = ["app", "layout", "state", "sections"]
