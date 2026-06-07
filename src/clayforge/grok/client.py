"""
Thin, resilient Grok / xAI client wrapper.

Goal: Make the most powerful AI capabilities (real token streaming + server-side tools)
feel like a single beautiful component, while still allowing power users full control.

Real streaming implemented:
- Uses AsyncOpenAI (OpenAI-compatible) pointing at https://api.x.ai/v1 when api_key present
- Yields incremental content + tool_call chunks for GrokChat / on_message handlers
- 100% graceful: no key or no `openai` dep → helpful message (GrokChat auto-simulates)
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

# Soft import for real streaming (OpenAI-compatible endpoint at api.x.ai)
# No hard dependency — falls back gracefully to simulation when unavailable.
try:
    from openai import APIError, AsyncOpenAI  # type: ignore

    _HAS_OPENAI = True
except Exception:  # pragma: no cover - optional dep
    AsyncOpenAI = None  # type: ignore
    APIError = Exception  # type: ignore
    _HAS_OPENAI = False


class GrokClient:
    """
    Thin resilient wrapper around xAI / Grok capabilities.

    Real streaming (token-by-token) is wired:
    - Provide api_key (or `pip install "clayforge[grok]"` for the openai SDK)
    - Use directly or pass to GrokChat(api_key=...) / GrokChat(client=...)
    - GrokChat auto-uses real streaming when key present (falls back to high-fidelity sim)

    Full tool calling deltas are yielded via stream_chat.
    """

    def __init__(self, api_key: str | None = None, model: str = "grok-4.3") -> None:
        self.api_key = api_key
        self.model = model
        self._sdk: Any = None  # lazy

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        tools: list[Any] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Real (or graceful) streaming.

        Yields dicts of shape: {'content': str, 'tool_calls': [...], 'done': bool, 'error': bool, ...}

        - When api_key + openai present: true token-by-token streaming from xAI (api.x.ai/v1)
        - Otherwise: friendly guidance message + done (GrokChat falls back to sim automatically)
        """
        if not self.api_key:
            yield {
                "content": "Provide an xAI API key to enable real Grok streaming (GrokChat will auto-detect and use it).",
                "done": True,
            }
            return

        if not _HAS_OPENAI:
            yield {
                "content": (
                    "Real Grok streaming requires the optional dependency.\n"
                    'pip install openai   (or pip install "clayforge[grok]" when the extra is defined)\n'
                    "GrokChat continues to deliver beautiful simulation when no key is present."
                ),
                "done": True,
            }
            return

        try:
            oai = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )

            create_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "stream": True,
            }
            if tools:
                create_kwargs["tools"] = tools
                if "tool_choice" in kwargs:
                    create_kwargs["tool_choice"] = kwargs["tool_choice"]

            stream = await oai.chat.completions.create(**create_kwargs)

            async for chunk in stream:
                choice = chunk.choices[0] if getattr(chunk, "choices", None) else None
                if not choice:
                    continue
                delta = getattr(choice, "delta", None)
                if not delta:
                    continue

                payload: dict[str, Any] = {"done": False}

                content = getattr(delta, "content", None)
                if content:
                    payload["content"] = content

                tool_calls = getattr(delta, "tool_calls", None)
                if tool_calls:
                    # Yield incremental tool call chunks (consumer / GrokChat can accumulate if desired)
                    payload["tool_calls"] = [
                        {
                            "id": getattr(tc, "id", None),
                            "type": getattr(tc, "type", None),
                            "function": {
                                "name": getattr(getattr(tc, "function", None), "name", None),
                                "arguments": getattr(
                                    getattr(tc, "function", None), "arguments", ""
                                ),
                            },
                        }
                        for tc in tool_calls
                        if tc is not None
                    ]

                if payload.get("content") or payload.get("tool_calls"):
                    yield payload

            # Always terminate with done
            yield {"done": True}

        except APIError as e:
            yield {
                "content": f"[xAI API Error] {getattr(e, 'message', str(e))}",
                "done": True,
                "error": True,
            }
        except Exception as e:
            yield {
                "content": f"[GrokClient streaming error] {type(e).__name__}: {str(e)[:160]}",
                "done": True,
                "error": True,
            }


def get_grok_client(api_key: str | None = None, model: str = "grok-4.3") -> GrokClient:
    """Convenience factory. Now accepts model for parity with GrokClient()."""
    return GrokClient(api_key=api_key, model=model)
