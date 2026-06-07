"""
ClayForge Grok Components — Production-grade AI UI primitives.

This module delivers the hero "it just works" experience:
- GrokChat: a drop-in, stunning, fully interactive streaming chat component
  with beautiful message bubbles, typewriter streaming, and rich tool call
  visualization — all wired with real WebSocket updates and zero boilerplate.
  Supports REAL token-by-token streaming from GrokClient when api_key (or client=) supplied
  (or XAI_API_KEY in env for the 03 example / showcase / gallery tester);
  otherwise identical gorgeous high-fidelity simulation (perfect discoverable "try it" experience).

Design goals:
- Follows exact Element + dataclass + Tailwind zinc/indigo patterns from basic.py
- Zero new dependencies for core; real streaming via soft openai import + existing GrokClient
- Fully usable directly in @app.page or nested inside ui.card() / ui.row()
- api_key / client props enable real Grok streaming; on_message for full custom control
- Self-contained: owns its input, state, and live updates
- Perfect graceful degradation: stunning simulation when no key (demo / showcase friendly)
"""

from __future__ import annotations

import asyncio
import datetime
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..core.element import Element
from ..core.elements.basic import Button, TextInput


def _now_ts() -> str:
    """Compact human timestamp for chat bubbles."""
    return datetime.datetime.now().strftime("%H:%M")


@dataclass
class GrokChat(Element):
    """
    A first-class, production-ready Grok chat interface.

    Drop it anywhere:

        from clayforge.grok import GrokChat

        @app.page("/")
        def chat_demo():
            GrokChat(model="grok-4.3", height="620px")

        # or beautifully nested
        with ui.card(classes="p-0 overflow-hidden"):
            GrokChat(placeholder="Ask about anything...", height="480px")

    Props:
        model: str          — Display label (also passed to GrokClient for real calls)
        system: Optional[str] — System prompt (used for real GrokClient calls + on_message)
        height: str         — CSS height (e.g. "520px", "70vh", "600px")
        placeholder: str    — Input placeholder text
        api_key: Optional[str] — THE EASY PATH for real streaming.
                                 Provide your xAI key (or env value). GrokChat wires GrokClient
                                 automatically and streams real tokens. If missing or invalid,
                                 silently falls back to the stunning built-in simulation (no errors).
        client: Optional[GrokClient] — Prebuilt GrokClient instance (full control over model/key).
        on_message: Optional[Callable[[GrokChat, str], Any]]
                            — Hook for real backends. Called with (self, user_message).
                              Return or await to drive assistant responses.
                              Use the public helpers below (add_*, stream_*) inside it.
                              Takes precedence over api_key/client auto-streaming.

    Public helpers for real integrations & simulation:
        .add_user_message(text)
        .add_assistant_message(text)
        .add_tool_call(name, args, result=None)
        .stream_append(chunk)   — appends to last assistant msg + live update
        .flush()                — force a full re-render + auto-scroll via WS

    Real streaming vs Simulation Fallback (crystal clear):
        • api_key="xai-..." or XAI_API_KEY → GrokChat auto-wires GrokClient for real
          token-by-token from xAI (api.x.ai/v1) via soft openai dep.
        • client=...         → Preconfigured GrokClient for full control.
        • on_message=...     → Highest precedence: drive everything yourself (still
          usable with real client inside handler for hybrid setups).
        • No key / no openai → 100% graceful high-fidelity simulation (typewriter,
          tool cards, perfect UI). Ideal for demos & showcases.

        Identical gorgeous bubbles, auto-scroll, and tool viz for BOTH paths.

    Quick example in your app:
        from clayforge.grok import GrokChat
        import os
        GrokChat(api_key=os.getenv("XAI_API_KEY"))   # real or sim — just works

    The component automatically:
    - Renders gorgeous message bubbles (user right/indigo, assistant left/zinc)
    - Shows beautiful "🔧 Using tool..." cards when tool calls occur
    - Streams assistant replies (real chunks when key present, typewriter sim otherwise)
    - Auto-scrolls the conversation
    - Supports instant UI feedback on send (user bubble appears before thinking)
    - Falls back to high-fidelity simulation when no API key (showcase / demo friendly)
    """

    model: str = "grok-4.3"
    system: str | None = None
    height: str = "560px"
    placeholder: str = "Message Grok..."
    api_key: str | None = None
    client: Any | None = None  # GrokClient instance (typed at runtime via import)
    on_message: Callable[[GrokChat, str], Any] | None = None
    show_input: bool = (
        True  # set False in polished demos to hide the input bar + send button for a cleaner visual
    )

    # --- Internal live state (never shown in repr) ---
    messages: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _input_el: TextInput | None = field(default=None, repr=False)
    _send_btn: Button | None = field(default=None, repr=False)
    _client_ref: Any | None = field(default=None, repr=False)  # last known client for helpers

    def __post_init__(self) -> None:
        super().__post_init__()

        # Enable beautiful direct usage: GrokChat(...) works at top level of @app.page
        # and also correctly nests when called inside `with ui.card():`, `with ui.row():` etc.
        try:
            from ..core.ui import _maybe_attach_or_root

            _maybe_attach_or_root(self)
        except Exception:
            pass  # graceful — still works if attached manually

        # Persistent live sub-elements for event routing (registered via our children list)
        # Their .to_html() is injected manually into our custom chat layout.
        if self.show_input:
            self._input_el = TextInput(
                placeholder=self.placeholder,
                value="",
                classes=(
                    "flex-1 bg-zinc-950 border border-zinc-700 focus:border-indigo-500/60 "
                    "text-sm text-zinc-200 placeholder:text-zinc-500 rounded-3xl px-4 py-3 "
                    "focus:outline-none focus:ring-1 focus:ring-indigo-500/30 transition-all"
                ),
            )
            self._input_el.on("change", self._handle_draft_change)

            self._send_btn = Button(
                label="Send",
                variant="primary",
                size="md",
                classes=(
                    "rounded-3xl px-6 font-semibold flex-shrink-0 shadow-sm "
                    "active:scale-[0.985] transition-all"
                ),
            )
            self._send_btn.on("click", self._handle_send)

            # Add to children so render_page() + traverse registers them for WS events.
            # Visual placement is 100% controlled by our to_html() — this is only for registration.
            if self._input_el not in self.children:
                self.children.append(self._input_el)
            if self._send_btn not in self.children:
                self.children.append(self._send_btn)

        # Real streaming client wiring (api_key or explicit client) — lazy + graceful
        self._grok_client: Any | None = None
        if self.client is not None:
            self._grok_client = self.client
        elif self.api_key:
            try:
                # Absolute import is robust across src-layout / editable / direct python runs
                from clayforge.grok.client import get_grok_client

                self._grok_client = get_grok_client(api_key=self.api_key, model=self.model)
            except Exception:
                self._grok_client = None  # will fall back to simulation automatically

        # Beautiful welcome message on first mount (only if empty)
        if not self.messages:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": "Hello! I'm Grok — ready to explore, search, code, or just chat. What can I help with?",
                    "ts": _now_ts(),
                }
            )

    # ------------------------------------------------------------------
    # Public API for real backends + advanced usage (the "hook")
    # ------------------------------------------------------------------

    def add_user_message(self, content: str) -> None:
        """Add a user message to the transcript (instant local state)."""
        if not content or not content.strip():
            return
        self.messages.append({"role": "user", "content": content.strip(), "ts": _now_ts()})

    def add_assistant_message(self, content: str) -> None:
        """Add a completed assistant message."""
        self.messages.append({"role": "assistant", "content": content.strip(), "ts": _now_ts()})
        self._push_update()

    def add_tool_call(
        self,
        name: str,
        args: dict[str, Any] | None = None,
        result: str | None = None,
    ) -> None:
        """Insert a rich tool call visualization card into the transcript."""
        self.messages.append(
            {
                "role": "tool",
                "tool_name": name,
                "args": args or {},
                "result": result,
                "ts": _now_ts(),
            }
        )
        self._push_update()

    def stream_append(self, chunk: str) -> None:
        """
        Append text to the current streaming assistant message (or create one).
        Call this repeatedly from a real streaming backend, then .flush() when done.
        """
        if not chunk:
            return
        # Find or create a streaming assistant bubble at the end
        if not self.messages or self.messages[-1].get("role") != "assistant":
            self.messages.append(
                {"role": "assistant", "content": "", "ts": _now_ts(), "streaming": True}
            )
        last = self.messages[-1]
        last["content"] = (last.get("content", "") + chunk).lstrip()
        last["streaming"] = True
        self._push_update()

    def flush(self) -> None:
        """Force a full re-render of the chat (and auto-scroll). Use after streams."""
        # Clean any streaming cursor flags
        for m in self.messages:
            if m.get("streaming"):
                m.pop("streaming", None)
        self._push_update()

    # ------------------------------------------------------------------
    # Internal event handlers (wired to real WS roundtrips)
    # ------------------------------------------------------------------

    def _handle_draft_change(self, data: dict[str, Any]) -> None:
        """Keep the TextInput's value in sync on every change (live draft)."""
        if self._input_el is not None:
            self._input_el.value = data.get("value", "")

    def _handle_send(self, data: dict[str, Any]) -> None:
        """The heart of the interactive experience — fully wired today."""
        if self._input_el is None or self._send_btn is None:
            return

        content = (self._input_el.value or "").strip()
        if not content:
            return

        # 1. Optimistic UI: user message appears instantly
        self.add_user_message(content)
        self._input_el.value = ""

        # Capture the live client (server temporarily sets _client on the event target)
        client = getattr(self._send_btn, "_client", None)
        if client is not None:
            self._client_ref = client

        # 2. Immediate re-render so user sees their bubble + input cleared
        self._push_update(client)

        # 3. Drive the assistant side
        if self.on_message:
            # Real backend hook — user is fully in control (highest precedence)
            try:
                result = self.on_message(self, content)
                if asyncio.iscoroutine(result):
                    # Schedule real async work (user's responsibility to call stream_* / flush inside)
                    loop = asyncio.get_event_loop()
                    loop.create_task(result)
            except Exception:
                # Never let a bad callback crash the chat
                self.add_assistant_message("Sorry — something went wrong processing that.")
        else:
            # Default path: real Grok streaming (when api_key or client was passed) or simulation
            try:
                loop = asyncio.get_event_loop()
                if self._grok_client and getattr(self._grok_client, "api_key", None):
                    # Real streaming integration — token-by-token from GrokClient
                    loop.create_task(self._stream_from_grok_client(client, content))
                else:
                    # High-fidelity built-in simulation (the original beautiful experience)
                    loop.create_task(self._simulate_grok_response(client, content))
            except Exception:
                # Last-resort fallback (sync path)
                self._simulate_grok_response_sync(content)

    # ------------------------------------------------------------------
    # Simulation engine (delivers the "magic" feeling out of the box)
    # ------------------------------------------------------------------

    def _get_simulated_reply(self, user_msg: str) -> str:
        """Grok-flavored canned but charming responses."""
        msg = user_msg.lower()
        if any(x in msg for x in ["hello", "hi ", "hey"]):
            return "Hey! Great to meet you. I'm powered by xAI and ready to help with anything — research, code, ideas, or wild what-if questions."
        if "weather" in msg or "forecast" in msg:
            return "I can look that up for you. Right now I'm simulating a tool call to web_search + a live weather service. In a real integration this would be live data."
        if "search" in msg or "look up" in msg or "find" in msg:
            return "Absolutely — running a web search for that right now. The results are coming back with high relevance. Want me to dig into any particular source?"
        if any(x in msg for x in ["how are you", "what's up"]):
            return "Doing fantastic — the weights are warm and the context window is wide open. How can I make your day more interesting?"
        if "clayforge" in msg or "framework" in msg:
            return "ClayForge is the beautiful Python web framework you're already inside. Pure Python elements, native WebSockets, and first-class Grok components. You're living the future."
        if "tool" in msg or "function" in msg:
            return "Tool calling is one of my favorite superpowers. I can use web_search, code execution, image generation, and your own custom Python functions — all visualized right here in the UI."
        return (
            "That's a fascinating question. In a production setup I would stream a thoughtful answer while possibly calling tools in parallel. "
            "For now this is a high-fidelity simulation that already feels magical — the real GrokClient wiring is the very next layer."
        )

    async def _simulate_grok_response(self, client: Any, user_msg: str) -> None:
        """Full async streaming simulation with tool cards + typewriter."""
        # Small "thinking" pause
        await asyncio.sleep(0.22)

        # Occasionally surface a beautiful tool call visualization
        use_tool = any(
            kw in user_msg.lower()
            for kw in ["search", "weather", "news", "price", "find", "look up", "tool"]
        )

        if use_tool:
            tool_name = "web_search" if "weather" not in user_msg.lower() else "get_weather"
            args = {"query": user_msg[:80]}

            self.messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "args": args,
                    "result": None,
                    "ts": _now_ts(),
                }
            )
            self._push_update(client)
            await asyncio.sleep(0.65)

            # Complete the tool result live
            result_text = (
                "Top result: ClayForge + Grok integration patterns. "
                "Confidence 94%. 2 supporting sources found."
                if tool_name == "web_search"
                else "Currently 72°F, clear skies. Wind 4mph from the west."
            )
            for m in reversed(self.messages):
                if m.get("role") == "tool" and m.get("result") is None:
                    m["result"] = result_text
                    break
            self._push_update(client)
            await asyncio.sleep(0.35)

        # Create streaming assistant placeholder
        assistant_entry: dict[str, Any] = {
            "role": "assistant",
            "content": "",
            "ts": _now_ts(),
            "streaming": True,
        }
        self.messages.append(assistant_entry)
        self._push_update(client)

        # Typewriter simulation (word chunks feel more natural than letters)
        reply = self._get_simulated_reply(user_msg)
        words = reply.split(" ")
        buffer = ""

        for word in words:
            buffer += (" " if buffer else "") + word
            assistant_entry["content"] = buffer + "▌"
            self._push_update(client)
            # Variable speed for realism
            delay = 0.028 if len(word) < 6 else 0.042
            await asyncio.sleep(delay)

        # Finalize (remove cursor)
        assistant_entry["content"] = buffer
        assistant_entry.pop("streaming", None)
        self._push_update(client)

        # The magic auto-scroll via existing run_js primitive
        self._scroll_to_bottom(client)

    def _simulate_grok_response_sync(self, user_msg: str) -> None:
        """Fallback when no event loop available (rare)."""
        reply = self._get_simulated_reply(user_msg)
        self.messages.append({"role": "assistant", "content": reply, "ts": _now_ts()})
        self._push_update()

    # ------------------------------------------------------------------
    # Real streaming integration (the new core path when api_key present)
    # ------------------------------------------------------------------

    async def _stream_from_grok_client(self, ws_client: Any, user_msg: str) -> None:
        """Drive real token-by-token (or chunked) streaming from GrokClient.

        Keeps 100% of the existing beautiful UI, tool cards (if surfaced), auto-scroll etc.
        Only replaces the source of tokens when a real client/key is configured.
        """
        if not self._grok_client:
            self.add_assistant_message("GrokClient not available for real streaming.")
            return

        # Reconstruct API-grade message history (system + prior turns + latest user)
        api_messages: list[dict[str, str]] = []
        if self.system:
            api_messages.append({"role": "system", "content": self.system})
        for m in self.messages:
            role = m.get("role")
            if role in ("user", "assistant") and m.get("content"):
                api_messages.append({"role": role, "content": m.get("content", "")})

        # Optimistic streaming assistant bubble (identical style to simulation)
        assistant_entry: dict[str, Any] = {
            "role": "assistant",
            "content": "",
            "ts": _now_ts(),
            "streaming": True,
        }
        self.messages.append(assistant_entry)
        self._push_update(ws_client)

        try:
            async for chunk in self._grok_client.stream_chat(
                messages=api_messages,
                # tools=... future: GrokChat could grow a tools= prop and forward here
            ):
                content = chunk.get("content") or ""
                if content:
                    # Append live — exact same UX contract as stream_append
                    assistant_entry["content"] = (
                        assistant_entry.get("content", "") + content
                    ).lstrip()
                    # Push frequently for true streaming feel (WS is efficient)
                    self._push_update(ws_client)

                if chunk.get("done"):
                    # Optional: future surface of tool_calls from final chunk
                    # e.g. if chunk.get("tool_calls"): self.add_tool_call(...)
                    break

            # Clean streaming flag + final render + scroll (same as sim path)
            assistant_entry.pop("streaming", None)
            self._push_update(ws_client)
            self._scroll_to_bottom(ws_client)

        except Exception as exc:
            # Never break the chat UI
            assistant_entry["content"] = f"Sorry, Grok streaming hit an error: {type(exc).__name__}"
            assistant_entry.pop("streaming", None)
            self._push_update(ws_client)
            self._scroll_to_bottom(ws_client)

    # ------------------------------------------------------------------
    # Update + scroll helpers (the reactivity core for this component)
    # ------------------------------------------------------------------

    def _push_update(self, client: Any = None) -> None:
        """Schedule a targeted WS update of the entire chat component + scroll."""
        if client is None:
            client = self._client_ref or getattr(self._send_btn, "_client", None)

        if client is None:
            return

        try:
            loop = asyncio.get_event_loop()
            html = self.to_html()
            loop.create_task(client.send_update(self.id, html))
            # Scroll shortly after the DOM patch lands
            loop.create_task(self._delayed_scroll(client, delay=0.06))
        except RuntimeError:
            # No running loop (very early render) — ignore; initial HTML is fine
            pass

    async def _delayed_scroll(self, client: Any, delay: float = 0.05) -> None:
        await asyncio.sleep(delay)
        self._scroll_to_bottom(client)

    def _scroll_to_bottom(self, client: Any) -> None:
        """Use the existing send_run_js primitive for perfect auto-scroll."""
        if client is None:
            return
        js = f"""
            (function() {{
                const container = document.getElementById('{self.id}-messages');
                if (container) {{
                    container.scrollTo({{ top: container.scrollHeight + 80, behavior: 'smooth' }});
                }}
            }})();
        """
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(client.send_run_js(js))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Rendering — stunning out-of-the-box Tailwind zinc/indigo aesthetic
    # ------------------------------------------------------------------

    def to_html(self) -> str:
        """Renders the complete modern chat UI with live subcomponents injected."""
        h = self.height
        messages_html = self._render_messages()

        # Inject the live input + button (they carry their own ids + event wiring)
        input_html = self._input_el.to_html() if self._input_el else ""
        send_html = self._send_btn.to_html() if self._send_btn else ""

        # Main component shell — feels premium and "just works"
        return f'''
<div id="{
            self.id
        }" class="flex flex-col bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-2xl ring-1 ring-white/5 {
            self.classes or ""
        }" style="height: {h};">
    <!-- Premium header -->
    <div class="flex items-center justify-between px-5 py-3.5 bg-zinc-950/70 border-b border-zinc-800">
        <div class="flex items-center gap-x-3">
            <div class="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 via-violet-500 to-fuchsia-500 flex items-center justify-center shadow-inner ring-1 ring-white/20">
                <i class="fa-solid fa-robot text-white text-lg"></i>
            </div>
            <div>
                <div class="font-semibold tracking-tighter text-white text-lg leading-none">Grok</div>
                <div class="text-[10px] font-mono text-zinc-500 tracking-[0.5px] mt-0.5">{
            self.model
        }</div>
            </div>
        </div>

        <div class="flex items-center gap-x-2">
            <div class="inline-flex items-center gap-x-1.5 px-3 py-1 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <div class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                <span class="text-xs font-medium tracking-wider">ONLINE</span>
            </div>
            <div class="text-[10px] text-zinc-500 font-mono px-1.5 hidden sm:block">• real-time</div>
        </div>
    </div>

    <!-- Scrollable conversation -->
    <div id="{self.id}-messages"
         class="flex-1 overflow-y-auto px-4 py-5 space-y-4 bg-[radial-gradient(#27272a_0.8px,transparent_1px)] bg-[length:3px_3px] custom-scroll"
         style="scroll-behavior: smooth;">
        {messages_html}
    </div>

    {
            f"""
    <!-- Composer -->
    <div class="border-t border-zinc-800 bg-zinc-900 p-3">
        <div class="flex items-center gap-2">
            {input_html}
            {send_html}
        </div>
        <div class="text-center mt-2">
            <div class="text-[10px] text-zinc-500/70 tracking-tight">
                Grok can make mistakes. Consider verifying important information.
            </div>
        </div>
    </div>
    """
            if self.show_input
            else ""
        }
</div>
<style>
/* Scoped chat scrollbar — feels native and beautiful */
#{self.id}-messages::-webkit-scrollbar {{
    width: 6px;
}}
#{self.id}-messages::-webkit-scrollbar-thumb {{
    background-color: #3f3f46;
    border-radius: 20px;
}}
#{self.id}-messages::-webkit-scrollbar-thumb:hover {{
    background-color: #52525b;
}}
.custom-scroll {{
    scrollbar-width: thin;
    scrollbar-color: #3f3f46 transparent;
}}
</style>
        '''.strip()

    def _render_messages(self) -> str:
        """Renders every message + tool card with gorgeous bubble styling."""
        if not self.messages:
            return (
                '<div class="flex h-full items-center justify-center text-zinc-500 text-sm">'
                "The conversation will appear here."
                "</div>"
            )

        parts: list[str] = []
        for msg in self.messages:
            role = msg.get("role", "assistant")
            ts = msg.get("ts", "")

            if role == "user":
                content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
                parts.append(
                    f"""
                    <div class="flex justify-end">
                        <div class="max-w-[78%] group">
                            <div class="bg-indigo-600 text-white px-4 py-2.5 rounded-3xl rounded-br-xl text-[15px] leading-snug shadow-sm">
                                {content}
                            </div>
                            <div class="text-right text-[10px] text-zinc-400 mt-1 pr-1 opacity-75 group-hover:opacity-100 transition-opacity">{ts}</div>
                        </div>
                    </div>
                    """
                )

            elif role == "tool":
                name = msg.get("tool_name", "tool")
                args = msg.get("args", {})
                result = msg.get("result")
                args_str = json.dumps(args, ensure_ascii=False)[:120]
                result_html = ""
                if result:
                    safe_result = str(result).replace("<", "&lt;").replace(">", "&gt;")[:280]
                    result_html = f"""
                        <div class="mt-2 pt-2 border-t border-zinc-700 text-emerald-300/90">
                            <span class="font-medium text-emerald-400">Result:</span><br>
                            <span class="font-mono text-xs leading-snug break-words">{safe_result}</span>
                        </div>
                    """

                parts.append(
                    f"""
                    <div class="mx-1 my-0.5">
                        <div class="bg-zinc-950 border border-zinc-700 rounded-2xl px-4 py-3 text-sm shadow-inner">
                            <div class="flex items-center gap-x-2 text-amber-400 font-medium">
                                <span class="text-base">🔧</span>
                                <span>Using <span class="font-mono text-amber-300">{name}</span></span>
                            </div>
                            <div class="mt-1.5 text-[12px] text-zinc-400 font-mono break-all">
                                {args_str}
                            </div>
                            {result_html}
                        </div>
                    </div>
                    """
                )

            else:  # assistant (including streaming)
                content = msg.get("content", "")
                streaming = msg.get("streaming", False)
                safe = content.replace("<", "&lt;").replace(">", "&gt;")

                # Subtle streaming cursor
                cursor = (
                    '<span class="inline-block w-1.5 h-4 align-[-1px] bg-zinc-400 animate-pulse ml-0.5"></span>'
                    if streaming
                    else ""
                )

                parts.append(
                    f"""
                    <div class="flex justify-start">
                        <div class="max-w-[82%] group">
                            <div class="bg-zinc-800 text-zinc-100 px-4 py-2.5 rounded-3xl rounded-bl-xl text-[15px] leading-snug border border-zinc-700/60">
                                {safe}{cursor}
                            </div>
                            <div class="text-[10px] text-zinc-400 mt-1 pl-1 opacity-75 group-hover:opacity-100 transition-opacity">{ts}</div>
                        </div>
                    </div>
                    """
                )

        return "\n".join(parts)

    def _html_tag(self) -> str:
        return "div"


# ------------------------------------------------------------------
# AgentCanvas - Live multi-agent visualization (Hero AI feature)
# ------------------------------------------------------------------


@dataclass
class AgentCanvas(Element):
    """
    Production-grade live multi-agent collaboration canvas with reactive WS updates.

    Drop-in beautiful visualization for real agent orchestration loops:

        from clayforge.grok import AgentCanvas
        import threading
        import time

        canvas = AgentCanvas(
            agents=[
                {"name": "Researcher", "role": "Deep research & sources", "color": "#6366f1"},
                {"name": "Critic",     "role": "Contradictions & quality", "color": "#f59e0b"},
                {"name": "Synthesizer","role": "Final synthesis", "color": "#8b5cf6"},
            ],
            title="Research Swarm",
            height="520px",
        )

        def run_real_orchestration():
            # Realistic research → critique → synthesize pipeline
            canvas.update_agent_status("Researcher", "thinking", "Decomposing query into vectors")
            canvas.add_thought("Researcher", "Planning targeted searches for 2026 data...")
            time.sleep(0.8)

            canvas.add_event("Researcher", "tool", "web_search",
                             tool_name="web_search", args={"q": "AI devtools 2026"},
                             result="12 high-signal sources found")
            canvas.update_agent_status("Researcher", "complete")

            canvas.update_agent_status("Critic", "thinking", "Cross-checking claims")
            canvas.add_thought("Critic", "Flagged tension in two vendor claims — escalating to re-verify.")
            # ... call GrokClient or your real agents here ...
            canvas.add_event("Critic", "log", "Validated via primary sources")
            canvas.update_agent_status("Critic", "complete")

            canvas.update_agent_status("Synthesizer", "synthesizing", "Drafting consensus")
            canvas.add_thought("Synthesizer", "All agents aligned. Producing executive report.")
            canvas.update_agent_status("Synthesizer", "complete", "Playbook ready")

        threading.Thread(target=run_real_orchestration, daemon=True).start()

    The canvas feels as live and reactive as GrokChat:
    - Call update_agent_status / add_thought / add_event from sync threads, async, or direct.
    - Full WS push on every mutation (no manual refresh).
    - **Upgraded Live Collaboration Graph** (the impressive centerpiece): richer Mermaid with varied shapes (stadium for coordinators, diamond for critique/fact, rounded for roles), dynamic phase subgraphs/clusters (research/critique/synthesis/specialists -- pop even on add_agent spawns), emoji+role+detail labels, hub-and-spoke swarm topology with |handoff| / |tool flow| edge labels + parallel branches, classDefs + status-tied colors/strokes for real-time 'alive' pulsing. Core agent_states now carries 'alive' flag + last_ts for viz. Backward-compatible; zero boilerplate.
    - Rich status pills + tool-aware thought stream.
    - Human-in-the-loop ready (inject guidance anytime).

    Public drive API (use these from your orchestration code):
        .update_agent_status(name, status, detail=None)
        .add_thought(agent, text)
        .add_event(agent, event_type="thought"|"tool"|"log", message="", tool_name=..., args=..., result=...)
        .add_agent(name, role="", color=None)  # spawn additional agents live at runtime (node "pops up" in graph + pills + can be driven; now with distinct shape/edge)
        .clear_thoughts()
        (existing play controls still work for quick demos; internal demo sim now uses dynamic spawn + is ~3x longer for wow effect)

    Zero hard dependencies. Pure Python + existing WS primitives.
    """

    agents: list[dict[str, Any]] = field(default_factory=list)
    title: str = "Multi-Agent Team"
    height: str = "580px"
    live: bool = True
    show_controls: bool = True  # set False in polished demos to hide the demo buttons

    thoughts: list[dict[str, Any]] = field(default_factory=list, repr=False)
    agent_states: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)
    is_running: bool = False
    _mermaid_id: str = field(default="", repr=False)
    _client_ref: Any | None = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()

        try:
            from ..core.ui import _maybe_attach_or_root

            _maybe_attach_or_root(self)
        except Exception:
            pass

        self._mermaid_id = f"mermaid_{self.id}"

        if not self.agents:
            self.agents = [
                {"name": "Researcher", "role": "Deep research", "color": "#6366f1"},
                {"name": "WebSearch", "role": "Tool calling", "color": "#10b981"},
                {"name": "Critic", "role": "Quality & contradictions", "color": "#f59e0b"},
                {"name": "Synthesizer", "role": "Final output", "color": "#8b5cf6"},
            ]

        # Snapshot initial team for _handle_reset (so dynamic add_agent spawns during long demos can be trimmed back for repeatable runs)
        if not hasattr(self, "_initial_agents") or not self._initial_agents:
            self._initial_agents = [dict(a) for a in self.agents]

        # Initialize rich per-agent live state (drives pills + dynamic graph)
        # 'recent_activity' exposes 'activity' data for AI-native viz (status/thought/tool/spawn) so JS enhancer
        # can drive real-time effects (data-flows, particles/rings, color flashes) synced to thoughts/tools/status.
        # This makes the live collab chart feel alive for research swarm / agentic team visualization.
        if not self.agent_states:
            for a in self.agents:
                name = a["name"]
                self.agent_states[name] = {
                    "status": "idle",
                    "detail": "",
                    "color": a.get("color", "#64748b"),
                    "last_ts": _now_ts(),
                    "alive": False,
                    "recent_activity": "idle",
                    "activity_ts": _now_ts(),
                }

        if not self.thoughts:
            self.thoughts = [
                {
                    "agent": "Researcher",
                    "text": "Starting deep research on the query...",
                    "ts": _now_ts(),
                    "type": "thought",
                },
            ]

        # Controls (registered for WS routing, layout controlled in to_html)
        if self.show_controls:
            self._play_btn = Button(
                label="▶ Start", variant="primary", classes="rounded-2xl text-sm px-4"
            )
            self._play_btn.on("click", self._handle_play_pause)

            self._inject_btn = Button(
                label="Inject Guidance", variant="secondary", classes="rounded-2xl text-sm px-4"
            )
            self._inject_btn.on("click", self._handle_inject)

            self._reset_btn = Button(
                label="Reset", variant="ghost", classes="rounded-2xl text-sm px-4"
            )
            self._reset_btn.on("click", self._handle_reset)

            for btn in (self._play_btn, self._inject_btn, self._reset_btn):
                if btn not in self.children:
                    self.children.append(btn)

    # ------------------------------------------------------------------
    # Public orchestration API — drive this from real agent loops (the key upgrade)
    # Fully reactive: every call pushes live over WS, just like GrokChat.
    # Safe to call from background threads (schedules on the main loop).
    # ------------------------------------------------------------------

    def add_thought(self, agent: str, text: str) -> None:
        """Append a plain thought to the live stream. Use for high-level progress."""
        if not agent or not text:
            return
        self._ensure_agent(agent)
        ts = _now_ts()
        self.thoughts.append({"agent": agent, "text": text.strip(), "ts": ts, "type": "thought"})
        if len(self.thoughts) > 30:
            self.thoughts = self.thoughts[-30:]
        # Also surface in agent state detail for the pills
        if agent in self.agent_states:
            self.agent_states[agent]["detail"] = text.strip()[:80]
            self.agent_states[agent]["last_ts"] = ts
            self.agent_states[agent]["recent_activity"] = "thought"
            self.agent_states[agent]["activity_ts"] = ts
        self._push_update()

    def update_agent_status(self, agent: str, status: str, detail: str | None = None) -> None:
        """
        Update live visual status for one agent.

        Recommended statuses (drives colors + graph):
            "idle", "thinking", "researching", "tool_use", "critiquing",
            "synthesizing", "complete", "error"

        This is the primary hook for real orchestration loops.
        """
        self._ensure_agent(agent)
        if agent not in self.agent_states:
            # Auto-create for unknown agents (flexible usage; _ensure_agent also added to .agents for viz)
            self.agent_states[agent] = {
                "status": "idle",
                "detail": "",
                "color": "#64748b",
                "last_ts": _now_ts(),
                "alive": False,
                "recent_activity": "status",
                "activity_ts": _now_ts(),
            }

        st = self.agent_states[agent]
        st["status"] = status
        if detail:
            st["detail"] = detail.strip()[:90]
        st["last_ts"] = _now_ts()
        st["recent_activity"] = "status"
        st["activity_ts"] = st["last_ts"]
        st["alive"] = status not in ("idle", "complete")

        # Also log a compact status change as thought
        self.thoughts.append(
            {
                "agent": agent,
                "text": f"→ {status}" + (f": {detail}" if detail else ""),
                "ts": st["last_ts"],
                "type": "status",
                "status": status,
            }
        )
        if len(self.thoughts) > 30:
            self.thoughts = self.thoughts[-30:]

        self._push_update()

    def add_event(
        self,
        agent: str,
        event_type: str = "log",
        message: str = "",
        *,
        tool_name: str | None = None,
        args: dict[str, Any] | None = None,
        result: str | None = None,
    ) -> None:
        """
        Rich event for tool calls, errors, structured logs. Renders as beautiful
        cards in the thought stream (identical spirit to GrokChat tool viz).

        Example from real agent code:
            canvas.add_event("WebSearch", "tool", "Executed search",
                             tool_name="web_search", args={"query": q}, result="Found 14 papers")
        """
        self._ensure_agent(agent)
        ts = _now_ts()
        entry: dict[str, Any] = {
            "agent": agent,
            "text": message.strip() if message else (tool_name or event_type),
            "ts": ts,
            "type": event_type,
        }
        if tool_name:
            entry["tool_name"] = tool_name
            entry["args"] = args or {}
            entry["result"] = result
        self.thoughts.append(entry)
        if len(self.thoughts) > 30:
            self.thoughts = self.thoughts[-30:]

        if agent in self.agent_states:
            self.agent_states[agent]["last_ts"] = ts
            if tool_name:
                self.agent_states[agent]["detail"] = f"tool:{tool_name}"
            # expose recent activity for viz (tool events are high-signal for data-flow/particles)
            act = "tool" if tool_name or event_type == "tool" else event_type
            self.agent_states[agent]["recent_activity"] = act
            self.agent_states[agent]["activity_ts"] = ts

        self._push_update()

    def clear_thoughts(self) -> None:
        """Reset the thought/event stream (keeps agent states)."""
        self.thoughts = []
        self._push_update()

    def _ensure_agent(self, name: str, role: str = "", color: str | None = None) -> None:
        """Internal: ensure agent exists in .agents list (for pills + mermaid) so unknown names from public calls appear live."""
        if not name or name == "System":
            return
        if not any(a.get("name") == name for a in self.agents):
            self.add_agent(name, role, color)

    def add_agent(self, name: str, role: str = "", color: str | None = None) -> None:
        """Dynamically spawn a new agent into the live team (appears instantly in status pills + collaboration graph).

        Use from real orchestration when agents self-assemble or fork sub-agents. The new node 'pops up' in the
        mermaid (with edges via dynamic builder), gets its own pill, and subsequent calls to update_*/add_* work.
        Triggers WS push + re-render so viewer sees the team grow organically — perfect 'hell yeah' visual for
        agentic systems.
        """
        if not name or any(a.get("name") == name for a in self.agents):
            return
        color = color or "#64748b"
        role = role or name
        self.agents.append({"name": name, "role": role, "color": color})
        if name not in self.agent_states:
            self.agent_states[name] = {
                "status": "idle",
                "detail": "",
                "color": color,
                "last_ts": _now_ts(),
                "alive": True,  # newly spawned starts alive for immediate viz pop in collab chart
                "recent_activity": "spawn",
                "activity_ts": _now_ts(),
            }
        # Direct thought append for "System" meta to avoid _ensure_agent("System") polluting the visible team list
        ts = _now_ts()
        self.thoughts.append(
            {
                "agent": "System",
                "text": f"New agent spawned: {name} ({role}) — dynamic team expansion",
                "ts": ts,
                "type": "thought",
            }
        )
        if len(self.thoughts) > 30:
            self.thoughts = self.thoughts[-30:]
        self._push_update()

    def _push_update(self, client: Any = None) -> None:
        """Robust live WS push + mermaid refresh. Mirrors GrokChat quality."""
        if client is None:
            client = (
                self._client_ref
                or getattr(self, "_client", None)
                or getattr(getattr(self, "_play_btn", None), "_client", None)
            )

        if client is None:
            return

        try:
            loop = asyncio.get_event_loop()
            html = self.to_html()
            loop.create_task(client.send_update(self.id, html))
            # After patch, re-init Mermaid (scripts don't auto-run on innerHTML) + scroll thoughts
            loop.create_task(self._refresh_mermaid_and_scroll(client, delay=0.04))
            self._client_ref = client
        except RuntimeError:
            # No running loop (very early) — initial HTML is fine
            pass
        except Exception:
            pass

    async def _refresh_mermaid_and_scroll(self, client: Any, delay: float = 0.04) -> None:
        await asyncio.sleep(delay)
        # Re-render mermaid on the live node (critical for dynamic graph on every mutation)
        # Build JS safely to avoid any \n / quote pitfalls inside the Python f-string
        nl = "\n"  # actual newline char for JS source we emit
        js = (
            "(function() {"
            "  const root = document.getElementById('" + self.id + "');"
            "  if (!root || !window.mermaid) return;"
            "  const pre = root.querySelector('.mermaid');"
            "  if (!pre) return;"
            "  let original = pre.getAttribute('data-diagram');"
            "  if (original) {"
            "    original = original.split('\\\\n').join('" + nl + "');"
            "    pre.textContent = original;"
            "  }"
            "  try { pre.removeAttribute('data-processed'); mermaid.run({nodes:[pre]}).catch(()=>{}); } catch(e){}"
            "  const thoughts = root.querySelector('.agent-thoughts');"
            "  if (thoughts) thoughts.scrollTo({top: thoughts.scrollHeight, behavior:'smooth'});"
            "})();"
        )
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(client.send_run_js(js))
        except Exception:
            pass

    def _handle_play_pause(self, data):
        play_btn = getattr(self, "_play_btn", None)
        client = getattr(play_btn, "_client", None) if play_btn else None
        if client:
            self._client_ref = client
        self.is_running = not self.is_running

        if self.is_running:
            if play_btn:
                play_btn.label = "⏸ Pause"
            self.add_thought("System", "Collaboration started — live orchestration mode")
            # Use new status API even in demo sim
            if self.agents:
                first = self.agents[0]["name"]
                self.update_agent_status(first, "thinking", "Demo simulation running")
            if client:
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(self._run_simulation(client))
                except Exception:
                    pass
        else:
            if play_btn:
                play_btn.label = "▶ Resume"
            self.add_thought("System", "Paused by user")

        self._push_update(client)

    def _handle_inject(self, data):
        inject_btn = getattr(self, "_inject_btn", None)
        client = getattr(inject_btn, "_client", None) if inject_btn else None
        if client:
            self._client_ref = client
        self.add_thought("Human", "Please focus on 2026 sources only")
        if self.agents:
            self.update_agent_status(self.agents[0]["name"], "researching", "Human steer applied")
        self.add_thought("Researcher", "Adjusting search strategy based on human input...")
        self._push_update(client)

    def _handle_reset(self, data):
        client = getattr(self, "_reset_btn", None)
        client = getattr(client, "_client", None) if client else None
        if client:
            self._client_ref = client
        self.thoughts = [
            {
                "agent": "System",
                "text": "Team reset. Ready for new orchestration.",
                "ts": _now_ts(),
                "type": "thought",
            }
        ]
        self.is_running = False
        if hasattr(self, "_play_btn") and self._play_btn:
            self._play_btn.label = "▶ Start"
        # Restore to initial team (trim any dynamically added agents from long demo) so re-runs are clean + repeatable.
        # This makes the "3x longer + new agents pop up" experience re-playable without reload.
        if getattr(self, "_initial_agents", None):
            self.agents = [dict(a) for a in self._initial_agents]
        # Rebuild clean states for (now reset) agent list
        self.agent_states = {}
        for a in self.agents:
            self.agent_states[a["name"]] = {
                "status": "idle",
                "detail": "",
                "color": a.get("color", "#64748b"),
                "last_ts": _now_ts(),
                "alive": False,
                "recent_activity": "idle",
                "activity_ts": _now_ts(),
            }
        self._push_update(client)

    async def _run_simulation(self, client):
        """Extended ~3x longer demo simulation (per user request for 'good effect on the viewer').

        Showcases the full public API + dynamic agent spawning (new agents pop up mid-run as if the
        swarm is intelligently self-assembling more specialists). This produces a rich, living
        'hell yeah, this is the agentic flow I want visually' experience for first-time viewers
        considering building their own AI agent teams.

        New agents appear in pills + grow the mermaid graph live (with connecting edges), receive
        statuses/thoughts/tool cards, and trigger the bubble pulse styles.
        """
        if not self.agents:
            return
        names = [a["name"] for a in self.agents]
        # Much longer sequence of phases (~3x original) with varied activity, tool cards, and
        # explicit dynamic spawns of FactChecker, Visualizer, Publisher partway through.
        # Sleeps tuned for satisfying pacing (overall significantly longer but still demo-friendly).
        steps = [
            (names[0], "thinking", "Decomposing the question into research vectors..."),
            (
                names[1] if len(names) > 1 else names[0],
                "tool_use",
                "Querying recent high-signal sources...",
            ),
            (
                names[2] if len(names) > 2 else names[0],
                "critiquing",
                "Found tension between two papers — escalating.",
            ),
            (names[0], "researching", "Re-querying with tighter 2026 scope..."),
            (
                names[-1] if len(names) > 3 else names[0],
                "synthesizing",
                "Drafting initial consensus outline...",
            ),
            # === DYNAMIC SPAWN 1: FactChecker joins the swarm live ===
            # This demonstrates runtime agent creation; node will pop in graph + get pill + activity.
        ]
        for agent, status, text in steps:
            if not self.is_running:
                return
            self.update_agent_status(agent, status, text)
            self.add_thought(agent, text)
            if "tool" in status or "search" in text.lower():
                self.add_event(
                    agent,
                    "tool",
                    "Primary source query executed",
                    tool_name="web_search",
                    args={"scope": "2026", "limit": 15},
                    result="14 curated sources + 3 contradictions flagged",
                )
            await asyncio.sleep(0.75)

        # Spawn FactChecker (will appear in UI immediately via push inside add_agent + updates)
        if not any(a["name"] == "FactChecker" for a in self.agents):
            self.add_agent("FactChecker", "Verify claims & sources", "#ef4444")
            await asyncio.sleep(0.3)
        self.update_agent_status(
            "FactChecker", "thinking", "Cross-referencing primary sources & claims..."
        )
        self.add_thought(
            "FactChecker",
            "Flagged 2 potential over-claims; pulling original docs for verification.",
        )
        self.add_event(
            "FactChecker",
            "tool",
            "source_verify",
            tool_name="cross_check",
            args={"claims": 2, "mode": "strict"},
            result="1 corrected, 1 high-confidence",
        )
        await asyncio.sleep(1.0)

        # Continue long flow with more agents active
        more_steps = [
            ("FactChecker", "critiquing", "Re-validated 3 key stats against SEC filings."),
            (
                names[1] if len(names) > 1 else names[0],
                "tool_use",
                "Parallel fetch from G2, Crunchbase, HN threads...",
            ),
            (
                names[2] if len(names) > 2 else names[0],
                "critiquing",
                "Noted marketing spin vs. actual NPS deltas.",
            ),
            ("FactChecker", "researching", "Deep link trace on funding round claims..."),
            (
                names[-1] if len(names) > 3 else names[0],
                "synthesizing",
                "Merging verified data into structured playbook draft...",
            ),
            # === DYNAMIC SPAWN 2: Visualizer joins ===
        ]
        for agent, status, text in more_steps:
            if not self.is_running:
                return
            self.update_agent_status(agent, status, text)
            self.add_thought(agent, text)
            if "tool" in status or "search" in text.lower() or "fetch" in text.lower():
                self.add_event(
                    agent,
                    "tool",
                    "multi_source",
                    tool_name="parallel_fetch",
                    args={"sources": ["g2", "crunchbase", "hn"]},
                    result="27 data points, 4 outliers surfaced",
                )
            await asyncio.sleep(0.8)

        if not any(a["name"] == "Visualizer" for a in self.agents):
            self.add_agent("Visualizer", "Charts, tables & visual summary", "#06b6d4")
            await asyncio.sleep(0.3)
        self.update_agent_status(
            "Visualizer", "synthesizing", "Building comparison matrix + trend sparkline..."
        )
        self.add_thought(
            "Visualizer", "Produced 4 charts + 1 executive table from verified signals."
        )
        self.add_event(
            "Visualizer",
            "tool",
            "chart_gen",
            tool_name="viz_render",
            args={"charts": 4},
            result="Interactive matrix + trend views ready",
        )
        await asyncio.sleep(1.1)

        # More work + final spawn
        final_steps = [
            ("Visualizer", "tool_use", "Rendering final comparison visuals for the report..."),
            (
                names[0] if len(names) > 0 else names[0],
                "researching",
                "Pulling last 48h signals for freshness...",
            ),
            ("FactChecker", "complete", "All claims now source-backed with confidence scores."),
            (
                names[-1] if len(names) > 3 else names[0],
                "synthesizing",
                "Weaving consensus GTM playbook v1.3...",
            ),
            # === DYNAMIC SPAWN 3: Publisher/Editor joins for final mile ===
        ]
        for agent, status, text in final_steps:
            if not self.is_running:
                return
            self.update_agent_status(agent, status, text)
            self.add_thought(agent, text)
            if "tool" in status or "render" in text.lower():
                self.add_event(
                    agent,
                    "tool",
                    "report_pack",
                    tool_name="artifact_writer",
                    args={"format": "md+viz"},
                    result="9-page playbook + OKR matrix + 90-day calendar",
                )
            await asyncio.sleep(0.7)

        if not any(a["name"] == "Publisher" for a in self.agents):
            self.add_agent("Publisher", "Polish narrative & package deliverable", "#f472b6")
            await asyncio.sleep(0.3)
        self.update_agent_status(
            "Publisher", "synthesizing", "Applying final voice + formatting pass..."
        )
        self.add_thought(
            "Publisher", "Executive summary tightened; visuals embedded; ready for human review."
        )
        self.add_event(
            "Publisher",
            "log",
            "final_pack",
            tool_name="deliverable",
            args={"type": "playbook"},
            result="Clean artifact + citation appendix produced",
        )
        await asyncio.sleep(1.0)

        if self.is_running:
            final = names[-1] if names else "Synthesizer"
            self.update_agent_status(final, "complete", "All agents aligned. Full artifacts ready.")
            self.add_thought(
                final,
                "Mission complete — extended swarm produced playbook, charts, verified claims + packaged deliverable.",
            )
            self.add_event(
                final, "log", "Orchestration complete — ready for next mission or human steer"
            )
            # Also mark the spawned ones nicely
            for spawned in ("FactChecker", "Visualizer", "Publisher"):
                if spawned in self.agent_states:
                    self.update_agent_status(spawned, "complete", "Contributed to final artifacts")
            self.is_running = False
            self._play_btn.label = "▶ Restart"
            self._push_update(client)

    def to_html(self) -> str:
        # Live status pills (new production feature — shows real-time agent state)
        status_pills = ""
        for a in self.agents:
            name = a["name"]
            st = self.agent_states.get(
                name, {"status": "idle", "detail": "", "color": a.get("color", "#64748b")}
            )
            c = st.get("color", a.get("color", "#64748b"))
            status = st.get("status", "idle")
            detail = st.get("detail", "")
            status_color = {
                "thinking": "#a5b4fc",
                "researching": "#6366f1",
                "tool_use": "#34d399",
                "critiquing": "#fbbf24",
                "synthesizing": "#c084fc",
                "complete": "#4ade80",
                "error": "#f87171",
                "idle": c,
            }.get(status, c)
            detail_html = (
                f'<span class="text-[10px] text-zinc-400 ml-1.5 truncate max-w-[110px]">{detail}</span>'
                if detail
                else ""
            )
            status_pills += f"""
            <div class="px-3 py-1 rounded-2xl bg-zinc-950 border border-zinc-800 flex items-center gap-x-2 text-xs min-w-0">
                <div class="w-2 h-2 rounded-full flex-shrink-0" style="background:{c}"></div>
                <div class="font-semibold text-zinc-100">{name}</div>
                <div class="px-2 py-px rounded-full text-[10px] font-mono tracking-tight" style="background:{status_color}20; color:{status_color}; border:1px solid {status_color}40">{status}</div>
                {detail_html}
            </div>"""

        # Rich thought/event stream (supports tool cards)
        thoughts_html = ""
        for t in self.thoughts[-12:]:
            agent_name = t.get("agent", "Agent")
            col = next((a.get("color") for a in self.agents if a["name"] == agent_name), "#64748b")
            ts = t.get("ts", "")
            text = str(t.get("text", ""))
            etype = t.get("type", "thought")

            if etype == "tool":
                # Beautiful tool card (matches GrokChat aesthetic)
                tname = t.get("tool_name", "tool")
                args = t.get("args") or {}
                res = t.get("result")
                args_str = json.dumps(args, ensure_ascii=False)[:90]
                res_html = (
                    f'<div class="mt-1 text-emerald-300/90 text-[11px] font-mono break-words">→ {str(res)[:160]}</div>'
                    if res
                    else ""
                )
                thoughts_html += f"""
                <div class="my-1.5 rounded-2xl bg-zinc-950 border border-zinc-700 px-3 py-2 text-xs">
                    <div class="flex items-center gap-x-2 text-amber-400">
                        <span>🔧</span>
                        <span class="font-semibold" style="color:{col}">{agent_name}</span>
                        <span class="font-mono text-amber-300/80">· {tname}</span>
                    </div>
                    <div class="text-[10px] text-zinc-400 mt-0.5 font-mono">{args_str}</div>
                    {res_html}
                    <div class="text-right text-[9px] text-zinc-500 mt-1">{ts}</div>
                </div>"""
            else:
                prefix = "●" if etype == "status" else ""
                thoughts_html += f"""
                <div class="text-xs py-1 flex gap-x-2 items-start">
                    <span class="font-mono text-[9px] text-zinc-500 w-9 flex-shrink-0 pt-px">{ts}</span>
                    <span style="color:{col}" class="font-semibold flex-shrink-0">{agent_name}</span>
                    <span class="text-zinc-300 leading-snug">{prefix} {text}</span>
                </div>"""

        # === UPGRADED DYNAMIC MERMAID: impressive centerpiece for real-time agentic team work ===
        # Per user: "we do need to upgrade the live collaboration chart part...it is kind of boring.
        # the rest of the demo run is bad ass tho... make that part more visually on par...
        # make the visuals of the agentic team working in real time feel so good. ... all agents on hand.
        # team make this research swarm the experience i envision please. go team."
        # Now: varied node shapes (stadium/rounded for roles, diamond for critique/fact), dynamic subgraphs/clusters
        # for phases (research/critique/synthesis/specialists) even as spawns happen, descriptive labels with emoji
        # + role snippet + recent detail, color/gradient tied to per-agent color + status, classDefs + styles for
        # animate-able 'alive' real-time viz (thick pulsing strokes on active). Swarm-like topology: coordinator/hub
        # spokes with |handoff|/|tool flow| edge labels + parallel branches + chain. New add_agent nodes pop with
        # distinct shape/edge. Core agent_states now carries 'alive' for real-time viz support.
        # Backward compat: no changes to public agents list / API. Pure str build, zero perf hit, WS/_refresh safe.
        # Showcase isolation + enhancer updated for new shapes.

        # Make core graph data structure support 'alive' real-time viz (enrich states; builder populates visual graph)
        # recent_activity makes 'working swarm' precise (tool/thought/status/spawn count as live for edges/particles)
        for nm in list(self.agent_states.keys()):
            st = self.agent_states[nm]
            recent = st.get("recent_activity", st.get("status", "idle"))
            st["alive"] = (st.get("status", "idle") not in ("idle", "complete")) or recent in (
                "tool",
                "thought",
                "spawn",
                "status",
            )
            if "last_ts" not in st:
                st["last_ts"] = _now_ts()

        mermaid_lines = ["flowchart LR"]
        node_ids = {}
        for i, a in enumerate(self.agents):
            nid = f"A{i}"
            node_ids[a["name"]] = nid
            name = a["name"]
            role = a.get("role", name)
            st = self.agent_states.get(name, {})
            status = st.get("status", "idle")
            detail = (st.get("detail") or "")[:42]

            # Emoji + rich descriptive label (name/role snippet/recent detail) -- feels like live team roster
            rlow = (role + " " + name + " " + status + " " + detail).lower()
            emoji = "🤖"
            if any(k in rlow for k in ["research", "search", "web"]):
                emoji = "🔬"
            elif any(k in rlow for k in ["critic", "contradict", "fact", "verify"]):
                emoji = "🧐"
            elif any(k in rlow for k in ["synth", "publish", "pack", "narrat"]):
                emoji = "✍️"
            elif any(k in rlow for k in ["coord", "orchestr", "handoff"]):
                emoji = "🧭"
            elif any(k in rlow for k in ["visual", "chart", "table"]):
                emoji = "📊"
            elif any(k in rlow for k in ["tool", "fetch", "search"]):
                emoji = "🛠️"

            label = f"{emoji} {name}"
            if role and role != name:
                label += f"<br/><small>{role[:22]}</small>"
            if detail and status not in ("idle", "complete"):
                label += f"<br/><i>{detail}</i>"
            elif status not in ("idle", "complete"):
                label += f"<br/><small>{status}</small>"

            # HTML-escape rich labels (emoji/br/small/i) for safe <pre data-diagram="...">{mermaid}</pre> + mermaid parser
            # (prevents < being treated as tags, broken DOM/svg, missing visuals on render; critical per QA audit)
            label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            # Varied shapes by role/status for personality + visual dynamism (stadium for leads, diamond critique, rounded default)
            # These render distinct SVG (rect/rounded/circle-ish/polygon) so collaboration chart feels alive vs boring boxes
            if any(k in rlow for k in ["coord", "orchestr"]) or name == "Coordinator":
                # stadium/pill for hub/coordinator -- central in swarm
                node_decl = f'    {nid}([ "{label}" ])'
            elif any(k in rlow for k in ["critic", "fact", "verify", "contradict"]) or status in (
                "critiquing",
            ):
                # diamond/rhombus for critique/fact-check -- "sharp eye"
                node_decl = f'    {nid}{{"{label}"}}'
            elif status in ("thinking", "researching", "synthesizing", "tool_use"):
                # rounded/stadium-ish for active work
                node_decl = f'    {nid}( "{label}" )'
            elif status == "complete":
                # softer rounded pill for done
                node_decl = f'    {nid}( "{label}" )'
            else:
                # default rounded for idle/other
                node_decl = f'    {nid}( "{label}" )'
            mermaid_lines.append(node_decl)

        # Dynamic subgraphs/clusters for phases -- even with runtime spawns (FactChecker etc land in specialists)
        # Makes the chart feel like real phased team collaboration, not flat list. Dynamically built.
        phase_groups: dict[str, list[str]] = {
            "research": [],
            "critique": [],
            "synthesis": [],
            "specialists": [],
        }
        for a in self.agents:
            nm = a["name"]
            nid = node_ids[nm]
            rlow = (a.get("role", "") + " " + nm).lower()
            if any(k in rlow for k in ["research", "search", "web"]):
                phase_groups["research"].append(nid)
            elif any(k in rlow for k in ["critic", "fact", "verify", "contradict"]):
                phase_groups["critique"].append(nid)
            elif any(k in rlow for k in ["synth", "publish", "pack", "narrat"]):
                phase_groups["synthesis"].append(nid)
            else:
                phase_groups["specialists"].append(nid)

        for pname, nids in phase_groups.items():
            if len(nids) >= 1:
                plabel = {
                    "research": "🔬 Research",
                    "critique": "🧐 Critique & Verify",
                    "synthesis": "✍️ Synthesis",
                    "specialists": "⚡ Specialists",
                }.get(pname, pname.title())
                mermaid_lines.append(f'    subgraph {pname.upper()} ["{plabel}"]')
                for nid in nids:
                    mermaid_lines.append(f"        {nid}")
                mermaid_lines.append("    end")

        # Swarm-like dynamic edges for spawns + real-time feel: hub (coord or first) spokes + labeled handoffs/tool flows
        # + parallel branches + chain. New spawned agents (via add_agent) get instant visible connections.
        # Edge labels surface 'handoffs' / 'tool flow' from live status -- the agentic team working.
        n = len(self.agents)
        if n > 0:
            hub_name = self.agents[0]["name"]
            for aa in self.agents:
                if any(
                    k in (aa["name"] + aa.get("role", "")).lower() for k in ["coord", "orchestr"]
                ):
                    hub_name = aa["name"]
                    break
            hub_id = node_ids[hub_name]
            for aa in self.agents:
                nm = aa["name"]
                if nm == hub_name:
                    continue
                nid = node_ids[nm]
                st = self.agent_states.get(nm, {})
                elabel = "handoff"
                if "tool" in (st.get("status", "") + st.get("detail", "")).lower():
                    elabel = "tool flow"
                mermaid_lines.append(f"    {hub_id} -->|{elabel}| {nid}")
            # sequential chain (preserves order feel for spawns)
            for i in range(1, n):
                prev = self.agents[i - 1]["name"]
                curr = self.agents[i]["name"]
                mermaid_lines.append(f"    {node_ids[prev]} -->|chain| {node_ids[curr]}")
            # cross/parallel branches for swarm visual interest (grows impressive with add_agent)
            if n >= 3:
                mermaid_lines.append(
                    f"    {node_ids[self.agents[0]['name']]} -.->|cross-check| {node_ids[self.agents[-1]['name']]}"
                )
            if n >= 4:
                mid = self.agents[n // 2]["name"]
                mermaid_lines.append(
                    f"    {node_ids[self.agents[0]['name']]} -.->|parallel| {node_ids[mid]}"
                )

        # ClassDefs (for animate-able 'alive' CSS hooks in real-time viz + showcase enhancer) + styles (color + status tie + thick active strokes)
        # 'alive' nodes get prominent stroke-width so pulse anims (existing + new) fire gorgeously. Colors from agent color.
        mermaid_lines.append(
            "    classDef active fill:#0f172a,stroke:#67e8f9,stroke-width:4px,color:#e0f2fe,stroke-dasharray:4 2"
        )
        mermaid_lines.append(
            "    classDef complete fill:#052e16,stroke:#4ade80,stroke-width:2.5px,color:#86efac"
        )
        mermaid_lines.append(
            "    classDef idle fill:#1e2937,stroke:#64748b,stroke-width:1.5px,color:#cbd5e1"
        )

        for i, a in enumerate(self.agents):
            nid = f"A{i}"
            st = self.agent_states.get(a["name"], {})
            status = st.get("status", "idle")
            base = a.get("color", "#6366f1")
            is_alive = st.get("alive", status not in ("idle", "complete"))
            if is_alive or status in (
                "thinking",
                "researching",
                "tool_use",
                "critiquing",
                "synthesizing",
            ):
                mermaid_lines.append(f"    class {nid} active")
                mermaid_lines.append(f"    style {nid} stroke:{base},stroke-width:4px")
            elif status == "complete":
                mermaid_lines.append(f"    class {nid} complete")
            else:
                mermaid_lines.append(f"    class {nid} idle")
                mermaid_lines.append(f"    style {nid} stroke:{base},stroke-width:1.5px")

        mermaid = "\n".join(mermaid_lines)
        mermaid_escaped = mermaid.replace("\n", "\\n").replace("\r", "").replace('"', "&quot;")

        # Expose rich activity data for JS post-process (real-time 'alive' viz in enhancer).
        # recent_activity (thought/tool/status/spawn) + agent color/status drive particles, rings, data-flows, flashes, color-morphs.
        # JSON on container div (read by enhanceAgentBubbles after mermaid.run); keeps mermaid static but post-process super-powered.
        activity_map = {}
        for nm, st in list(self.agent_states.items()):
            if any(aa["name"] == nm for aa in self.agents):
                activity_map[nm] = {
                    "activity": st.get("recent_activity", st.get("status", "idle")),
                    "status": st.get("status", "idle"),
                    "color": st.get("color", "#64748b"),
                }
        activity_json = json.dumps(activity_map).replace('"', "&quot;")

        # Controls html
        play_html = (
            self._play_btn.to_html() if hasattr(self, "_play_btn") and self._play_btn else ""
        )
        inject_html = (
            self._inject_btn.to_html() if hasattr(self, "_inject_btn") and self._inject_btn else ""
        )
        reset_html = (
            self._reset_btn.to_html() if hasattr(self, "_reset_btn") and self._reset_btn else ""
        )

        return f'''
        <div id="{self.id}" class="w-full bg-zinc-900 border border-zinc-800 rounded-3xl flex flex-col overflow-hidden" style="height:{self.height}">
            <div class="px-5 py-3 border-b border-zinc-800 flex items-center justify-between bg-zinc-950/60">
                <div class="font-semibold flex items-center gap-x-2 text-white tracking-tight">
                    <i class="fa-solid fa-project-diagram text-indigo-400"></i> {self.title}
                </div>
                <div class="flex gap-x-1.5">
                    {play_html if self.show_controls else ""}
                    {inject_html if self.show_controls else ""}
                    {reset_html if self.show_controls else ""}
                </div>
            </div>

            <!-- Live Agent Status Row (production UX) -->
            <div class="px-4 pt-3 pb-2 bg-zinc-950/40 border-b border-zinc-800 flex flex-wrap gap-2">
                {status_pills or '<div class="text-xs text-zinc-500 px-1">Agents will appear here with live status as your orchestration runs.</div>'}
            </div>

            <div class="flex-1 flex overflow-hidden">
                <!-- Dynamic Live Graph -->
                <div class="w-3/5 p-4 border-r border-zinc-800 flex flex-col">
                    <div class="text-[10px] uppercase tracking-[1px] text-zinc-500 mb-1.5 px-1 flex items-center justify-between">
                        <span>Live Collaboration Chart</span>
                        <span class="normal-case text-emerald-400/70">real-time agentic team in motion • spawns, handoffs, thoughts &amp; tools live</span>
                    </div>
                    <div class="bg-zinc-950 rounded-2xl flex-1 p-3 overflow-auto custom-scroll" data-agent-activity="{activity_json}">
                        <pre class="mermaid" data-diagram="{mermaid_escaped}" style="background:transparent; font-size:13px">{mermaid}</pre>
                    </div>
                </div>

                <!-- Rich Thought + Event Stream -->
                <div class="w-2/5 flex flex-col">
                    <div class="px-4 pt-3 text-[10px] uppercase tracking-[1px] text-zinc-500">Thought &amp; Event Stream</div>
                    <div class="flex-1 overflow-auto p-3 text-sm bg-zinc-950 custom-scroll agent-thoughts" style="font-size:12.5px; line-height:1.35">
                        {thoughts_html or '<div class="text-zinc-500 px-1 py-2 text-xs">No activity yet. Use update_agent_status / add_thought / add_event from your Python orchestration.</div>'}
                    </div>
                    <div class="p-2.5 border-t border-zinc-800 text-[9px] text-zinc-500 bg-zinc-950/70 flex items-center gap-2">
                        <span>Real-time via WS • call the public methods from any agent loop</span>
                    </div>
                </div>
            </div>
        </div>

        <script>
        (function() {{
            const initMermaidForCanvas = () => {{
                if (!window.mermaid) {{
                    const s = document.createElement('script');
                    s.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
                    s.onload = () => {{
                        // Enhanced mermaid config for Grok/AI-native collab viz: rich labels, organic curves for 'flow/handoff' feel,
                        // loose security (for our dynamic labels), dark theme harmony with zinc/indigo shell. Direction LR keeps
                        // sequential+swarm handoff visual (collaborative team motion left-to-right); TD would be more hierarchy.
                        mermaid.initialize({{
                            startOnLoad: false,
                            theme: 'dark',
                            securityLevel: 'loose',
                            flowchart: {{
                                useMaxWidth: true,
                                htmlLabels: true,
                                curve: 'basis',  // smooth organic connections for data-flow handoffs vs straight
                                padding: 12,
                            }},
                        }});
                        renderMermaidInRoot();
                    }};
                    document.head.appendChild(s);
                }} else {{
                    renderMermaidInRoot();
                }}
            }};
            const renderMermaidInRoot = () => {{
                const root = document.getElementById('{self.id}');
                if (!root) return;
                const pres = root.querySelectorAll('.mermaid');
                pres.forEach(p => {{
                    if (!p.hasAttribute('data-processed')) {{
                        try {{ mermaid.run({{nodes: [p]}}).catch(()=>{{}}); }} catch(e){{}}
                    }}
                }});
            }};
            // Run on initial mount
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initMermaidForCanvas);
            }} else {{
                initMermaidForCanvas();
            }}
        }})();
        </script>
        '''

    def _html_tag(self):
        return "div"


__all__ = ["GrokChat", "AgentCanvas"]
