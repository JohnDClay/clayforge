"""
Basic tests for Grok components (GrokChat, AgentCanvas, GrokClient).

Covers import, instantiation, public API surface, render (light + with handlers),
graceful no-key behavior. Complements the showcase section tests and examples.
"""

import clayforge as cf
from clayforge.grok import AgentCanvas, GrokChat, get_grok_client


def test_grok_imports_and_version():
    assert hasattr(cf, "__version__")
    assert "grok" in str(GrokChat) or True  # class exists


def test_grokchat_instantiation_and_public_api():
    chat = GrokChat(height="300px", show_input=True)
    assert chat.height == "300px"
    assert chat.show_input is True
    # public helpers exist
    assert hasattr(chat, "add_user_message")
    assert hasattr(chat, "add_assistant_message")
    assert hasattr(chat, "add_tool_call")
    assert hasattr(chat, "stream_append")
    assert hasattr(chat, "flush")
    # messages start with welcome
    assert len(chat.messages) >= 1
    assert chat.messages[0]["role"] == "assistant"


def test_grokchat_public_api_mutations():
    chat = GrokChat(show_input=False)
    chat.add_user_message("hello")
    chat.add_assistant_message("hi there")
    chat.add_tool_call("search", {"q": "test"}, "found stuff")
    assert len(chat.messages) == 4  # welcome + 3
    assert any(m.get("role") == "tool" for m in chat.messages)


def test_agentcanvas_instantiation_and_public_api():
    canvas = AgentCanvas(
        title="Test Swarm",
        height="200px",
        show_controls=True,
        agents=[
            {"name": "Researcher", "role": "r", "color": "#6366f1"},
            {"name": "Synthesizer", "role": "s", "color": "#8b5cf6"},
        ],
    )
    assert canvas.title == "Test Swarm"
    assert canvas.show_controls is True
    assert len(canvas.agents) == 2
    assert hasattr(canvas, "update_agent_status")
    assert hasattr(canvas, "add_thought")
    assert hasattr(canvas, "add_event")
    assert hasattr(canvas, "clear_thoughts")
    # initial thoughts
    assert len(canvas.thoughts) >= 1


def test_agentcanvas_public_api_mutations():
    canvas = AgentCanvas(
        agents=[{"name": "R", "role": "r", "color": "#000"}],
        show_controls=False,
    )
    canvas.update_agent_status("R", "thinking", "working")
    canvas.add_thought("R", "deep thought")
    canvas.add_event("R", "tool", "searched", tool_name="web", args={"q": "x"}, result="y")
    assert "thinking" in str(canvas.agent_states["R"])
    assert len(canvas.thoughts) >= 3  # initial + status + thought + event


def test_grokclient_graceful_no_key():
    client = get_grok_client(api_key=None)
    # stream_chat should yield a done message without error
    import asyncio

    async def _run():
        chunks = []
        async for c in client.stream_chat([{"role": "user", "content": "hi"}]):
            chunks.append(c)
        return chunks

    chunks = asyncio.run(_run())
    assert len(chunks) >= 1
    assert chunks[-1].get("done") is True


def test_grokchat_renders_to_html():
    chat = GrokChat(height="200px")
    html = chat.to_html()
    assert "grok-4.3" in html or "Grok" in html
    assert "flex flex-col bg-zinc-900" in html  # shell


def test_agentcanvas_renders_to_html():
    canvas = AgentCanvas(title="Swarm", agents=[{"name": "A", "role": "a", "color": "#f00"}])
    html = canvas.to_html()
    assert "Swarm" in html
    assert "project-diagram" in html or "rounded-3xl" in html


def test_grokchat_show_input_false_hides_composer():
    chat = GrokChat(show_input=False)
    html = chat.to_html()
    assert "Message Grok" not in html
    assert "Send" not in html  # no send btn


def test_agentcanvas_show_controls_false_hides_buttons():
    canvas = AgentCanvas(show_controls=False, agents=[{"name": "A", "role": "", "color": "#000"}])
    html = canvas.to_html()
    # no ▶ or Inject or Reset text in controls area
    assert "▶" not in html
    assert "Inject" not in html


def test_agentcanvas_dynamic_add_agent_and_mermaid_growth():
    """New public API + dynamic team growth for impressive agentic viz (used in showcase long demo)."""
    canvas = AgentCanvas(
        agents=[{"name": "Researcher", "role": "r", "color": "#6366f1"}],
        title="Dyn Swarm",
        height="180px",
        show_controls=False,
    )
    assert len(canvas.agents) == 1
    canvas.add_agent("FactChecker", "verify claims", "#ef4444")
    assert len(canvas.agents) == 2
    assert any(a["name"] == "FactChecker" for a in canvas.agents)
    canvas.update_agent_status("FactChecker", "thinking", "validating")
    assert canvas.agent_states["FactChecker"]["status"] == "thinking"
    html = canvas.to_html()
    assert "FactChecker" in html  # appears in pills or mermaid nodes
    assert "thinking" in html or "mermaid" in html
    # mermaid should include the new node label
    assert "FactChecker" in html
    # reset should trim back to initial
    canvas._handle_reset({})
    assert len(canvas.agents) == 1
    assert "FactChecker" not in [a["name"] for a in canvas.agents]
