"""
ClayForge Example 03 — GrokChat (Fully Working + Real Streaming)

The crown jewel demo: a production-quality, drop-in Grok chat experience.

Features demonstrated:
- Stunning zinc + indigo chat UI with perfect bubbles, timestamps, and scroll
- Fully wired input + send button with real WebSocket roundtrips
- Instant user message appearance + beautiful typewriter streaming simulation
- Live tool call visualization cards (try messages containing "search", "weather")
- Auto-scroll + smooth streaming updates via native ClayForge WS
- NEW: Real token-by-token streaming from GrokClient when api_key provided
- The on_message hook + direct api_key= / client= props for real Grok
- Graceful fallback: drop-in beauty even with no key (showcase safe)
- Works directly, inside ui.card(), or any layout primitive

Run it:
    python examples/03_grok_chat.py
    # or via the CLI (recommended for reload)
    clayforge run --app examples.03_grok_chat:app

Set XAI_API_KEY (or GROK_API_KEY) env var **before launch** for live Grok streaming.

Quick "try with your key" experience:
    1. export XAI_API_KEY=your_xai_key_here
    2. python examples/03_grok_chat.py
    3. In the "Auto Real Streaming (NEW)" card: chat live with real Grok tokens!

Open http://127.0.0.1:8000 and try messages like:
    - "hello"
    - "search for clayforge"
    - "what's the weather in SF?"

Without a key → stunning built-in simulation (perfect for demos).
With a key → the dedicated card auto-wires real token-by-token streaming via GrokClient.
Both paths deliver identical gorgeous UI, tool cards, and live WS updates.

Discoverability in the surfaces:
- `clayforge showcase` — clean dedicated tab: the full interactive GrokChat appears ONLY in the "GrokChat" tab (nice title + prose first, full composer + tool cards). Zero leakage to other sections.
- `clayforge gallery` — primary rich tester + "Real Grok Streaming Live Tester" (ephemeral key activation for true xAI tokens) + Command Center.
"""

import os

import clayforge as cf
from clayforge.grok import GrokChat, get_grok_client

app = cf.App(
    title="ClayForge • GrokChat",
    description="First-class Grok experience in pure Python. Streaming, tools, zero boilerplate.",
)


# ------------------------------------------------------------------
# Real backend examples (on_message + GrokClient patterns)
# ------------------------------------------------------------------


def my_real_grok_handler(chat: GrokChat, user_message: str) -> None:
    """
    When you pass on_message=..., GrokChat skips its built-in simulation
    and lets you drive everything. Use the public helpers:

        chat.add_tool_call("web_search", {"query": "..."}, "result here")
        chat.stream_append("Thinking...")
        chat.stream_append(" more text")
        chat.flush()

    The exact same pattern works with real GrokClient.stream_chat() yielding chunks.
    """
    # Simple echo-style "real" logic with a tiny delay simulation
    import time

    time.sleep(0.3)  # pretend we're calling the real API

    # Demonstrate the tool + streaming API even in a "real" handler
    if "search" in user_message.lower():
        chat.add_tool_call(
            "web_search",
            {"query": user_message[:60]},
            "ClayForge — the most beautiful AI-native Python web framework of 2026.",
        )

    # Stream an answer back using the component's helpers (this triggers live WS updates)
    reply = (
        f'Received your message via the on_message hook: "{user_message}". '
        "This response was produced by YOUR Python function — the same pattern works with the real GrokClient streaming iterator."
    )

    # Simulate nice streaming from a real backend
    for i in range(0, len(reply), 7):
        chat.stream_append(reply[i : i + 7])
        time.sleep(0.035)
    chat.flush()


def make_grokclient_streaming_handler(api_key: str | None = None):
    """Factory returning an async on_message handler that uses real GrokClient when key present.

    Demonstrates the canonical "full control" path.
    When api_key present → real streaming from GrokClient.stream_chat().
    No key → friendly fallback (identical UI contract).
    """
    grok = get_grok_client(api_key=api_key) if api_key else None

    async def handler(chat: GrokChat, user_message: str):
        if grok and grok.api_key:
            # --- REAL STREAMING via GrokClient (the new integration) ---
            # This shows the advanced path; most users will prefer the simple api_key= prop on GrokChat.
            chat.add_tool_call("grok_stream", {"note": "live xAI call"}, None)  # optional visual

            api_messages = [{"role": "user", "content": user_message}]
            try:
                async for chunk in grok.stream_chat(api_messages):
                    if chunk.get("content"):
                        chat.stream_append(chunk["content"])
                    if chunk.get("done"):
                        chat.flush()
                        break
            except Exception as e:
                chat.stream_append(f" (streaming error: {e})")
                chat.flush()
            return

        # Fallback inside the hook (no key)
        import asyncio

        await asyncio.sleep(0.25)
        chat.stream_append("Real GrokClient not configured (no XAI_API_KEY). ")
        chat.stream_append(
            "This fallback response came through the on_message + GrokClient-ready handler."
        )
        chat.flush()

    return handler


@app.page("/")
def grok_chat_page():
    cf.ui.title("GrokChat")
    cf.ui.subtitle(
        "Drop-in streaming chat with tool visualization. Type below and watch the magic."
    )

    xai_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")

    with cf.ui.row(gap="6"):
        # === Primary demo: standalone GrokChat (the hero usage) ===
        with cf.ui.card(
            title="Live GrokChat",
            subtitle="Default high-fidelity simulation (try 'search', 'weather', 'clayforge')",
            classes="p-0 flex-1 overflow-hidden",
        ):
            GrokChat(
                model="grok-4.3",
                height="580px",
                placeholder="Ask Grok anything — search, weather, code, philosophy...",
            )

        # === Second column: on_message + NEW real streaming cards ===
        with cf.ui.column(gap="6", classes="flex-1"):
            with cf.ui.card(
                title="Real Backend Hook (on_message)",
                subtitle="Your handler (GrokClient pattern ready)",
                classes="p-0 overflow-hidden",
            ):
                GrokChat(
                    model="grok-4.3-hook",
                    height="260px",
                    placeholder="Uses on_message + optional GrokClient...",
                    on_message=make_grokclient_streaming_handler(xai_key),
                )

            # === THE NEW INTEGRATION: direct api_key prop for automatic real streaming ===
            # This is the easiest path for users: pass api_key (from env or direct) and GrokChat
            # handles client creation + real stream_chat() internally, with perfect graceful fallback.
            real_sub = (
                "REAL streaming from Grok (XAI_API_KEY detected)"
                if xai_key
                else "Real streaming (set XAI_API_KEY env to activate)"
            )
            with cf.ui.card(
                title="Auto Real Streaming (NEW)",
                subtitle=real_sub,
                classes="p-0 overflow-hidden",
            ):
                GrokChat(
                    model="grok-4.3",
                    api_key=xai_key
                    or None,  # <--- MAGIC LINE: wires real GrokClient streaming automatically
                    height="260px",
                    placeholder="Real Grok tokens when key present — falls back to sim gracefully",
                )

            with cf.ui.card(
                title="How to use real streaming",
                subtitle="Two easy paths (api_key auto-wires real Grok; falls back to sim)",
            ):
                cf.ui.markdown(
                    "from clayforge.grok import GrokChat, get_grok_client<br><br>"
                    "# Path 1 — Automatic (RECOMMENDED — easiest discoverable path)<br>"
                    "GrokChat(api_key=os.getenv('XAI_API_KEY'))   # real tokens or graceful sim<br><br>"
                    "# Path 2 — Full control via on_message (for custom logic)<br>"
                    "client = get_grok_client(api_key=os.getenv('XAI_API_KEY'))<br>"
                    "GrokChat(on_message=your_handler_using_client)<br><br>"
                    "No key? Both paths deliver the exact same beautiful simulation UI."
                )

    cf.ui.footer(
        "Example 03 • GrokChat now supports REAL streaming via GrokClient when api_key present • Pure Python"
    )


if __name__ == "__main__":
    app.run()
