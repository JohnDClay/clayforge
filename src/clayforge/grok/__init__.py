"""
ClayForge Grok Integration (First-Class AI-Native Layer)

This is where ClayForge differentiates itself most strongly from every other Python UI framework in 2026.

Public surface:

    from clayforge.grok import GrokChat, AgentCanvas, GrokClient, get_grok_client

    GrokChat(                    # Drop-in, production-quality streaming chat
        model="grok-4.3",
        api_key="xai-...",       # NEW: enables REAL token streaming via GrokClient
        system="You are an expert data analyst...",
    )

    # Or preconfigure
    client = get_grok_client(api_key)
    GrokChat(client=client)

    AgentCanvas(                 # Live multi-agent collaboration visualization
        agents=[researcher, critic, synthesizer],
        live=True,
    )
    # The Live Collaboration Graph (mermaid in to_html) is visually dynamic: shapes by role, phase clusters,
    # labeled swarm edges, alive status pulsing -- centerpiece for real-time agent teams (see components.py doc).
"""

from __future__ import annotations

from typing import Any

from .client import GrokClient, get_grok_client

# Real, fully implemented components (Grok layer is now live)
from .components import AgentCanvas, GrokChat

__all__ = ["GrokChat", "AgentCanvas", "GrokClient", "get_grok_client"]


def __getattr__(name: str) -> Any:
    """
    Graceful stubs for the remaining hero features still in progress.
    GrokChat is now production-ready and imported above.
    """
    if name in {"stream_chat", "create_agent_team"}:
        from rich.console import Console
        from rich.panel import Panel

        def _stub(*args: Any, **kwargs: Any) -> None:
            console = Console()
            console.print(
                Panel(
                    f"[bold cyan]{name}[/bold cyan] is planned for a future release.\n\n"
                    "GrokChat + AgentCanvas are production-grade today:\n"
                    "• GrokChat(api_key=...) → real token streaming\n"
                    "• AgentCanvas → live status, thoughts, tool events, dynamic graph\n"
                    "• Full orchestration examples: examples/04_multi_agent_vision.py and 07\n\n"
                    "For real xAI: export XAI_API_KEY=... and explore the gallery + examples.",
                    title="ClayForge Grok — AgentCanvas & GrokChat are Live",
                    border_style="cyan",
                )
            )

        return _stub

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
