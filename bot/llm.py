"""LLM interface — Qwen 3.5 via Ollama with tool calling and streaming support."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Generator

import httpx

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:latest"


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0


# -- Tool definitions for Ollama format --

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "save_discovery",
            "description": "Save customer discovery notes as a seed document for an Afterburner project. Call this when you have a confirmed synthesis of the customer's problem, users, use cases, and success criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug (e.g. 'inventory-tracker')",
                    },
                    "content": {
                        "type": "string",
                        "description": "Markdown content: Problem, Users, Use Cases, Success Criteria",
                    },
                },
                "required": ["slug", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_summary",
            "description": "Get a summary of an Afterburner project — what's been built, planned, and shipped.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug",
                    },
                },
                "required": ["slug"],
            },
        },
    },
]


class OllamaClient:
    """Chat completion via Ollama's /api/chat endpoint with streaming support."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request to Ollama (non-streaming)."""
        all_messages = self._build_messages(messages, system_prompt)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        start = time.monotonic()
        try:
            resp = self._client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            log.error("Ollama request failed: %s", exc)
            return LLMResponse(
                content=f"Sorry, I'm having trouble connecting to the LLM. ({exc})",
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        data = resp.json()
        duration_ms = int((time.monotonic() - start) * 1000)

        msg = data.get("message", {})
        content = msg.get("content", "")

        # Parse tool calls if present
        tool_calls: list[ToolCall] = []
        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            tool_calls.append(
                ToolCall(
                    name=fn.get("name", ""),
                    arguments=fn.get("arguments", {}),
                )
            )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            duration_ms=duration_ms,
        )

    def chat_stream(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> Generator[str, None, LLMResponse]:
        """Stream a chat completion, yielding content chunks.

        Yields partial content strings as they arrive.
        Returns the final LLMResponse when the generator is exhausted.
        Use: gen = client.chat_stream(...); for chunk in gen: ...
        The return value can be captured via StopIteration.value.
        """
        all_messages = self._build_messages(messages, system_prompt)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        start = time.monotonic()
        full_content = ""
        input_tokens = 0
        output_tokens = 0
        tool_calls: list[ToolCall] = []

        try:
            with self._client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    msg = data.get("message", {})

                    # Accumulate content chunks
                    chunk = msg.get("content", "")
                    if chunk:
                        full_content += chunk
                        yield chunk

                    # Capture tool calls from the final message
                    for tc in msg.get("tool_calls", []):
                        fn = tc.get("function", {})
                        tool_calls.append(
                            ToolCall(
                                name=fn.get("name", ""),
                                arguments=fn.get("arguments", {}),
                            )
                        )

                    # Final message contains token counts
                    if data.get("done"):
                        input_tokens = data.get("prompt_eval_count", 0)
                        output_tokens = data.get("eval_count", 0)

        except httpx.HTTPError as exc:
            log.error("Ollama streaming request failed: %s", exc)
            full_content = f"Sorry, I'm having trouble connecting to the LLM. ({exc})"
            yield full_content

        duration_ms = int((time.monotonic() - start) * 1000)
        return LLMResponse(
            content=full_content,
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
        )

    def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            resp = self._client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.model.split(":")[0] in m for m in models)
        except httpx.HTTPError:
            return False

    def close(self) -> None:
        self._client.close()

    def _build_messages(
        self, messages: list[dict], system_prompt: str | None
    ) -> list[dict]:
        """Prepend system prompt to message list if provided."""
        all_messages: list[dict] = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        return all_messages
