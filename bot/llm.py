"""LLM interface — multi-provider support (Ollama, Claude, ChatGPT)."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Generator

import httpx

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:latest"

LLM_PROVIDERS = {
    "qwen-3.5": {
        "label": "Qwen 3.5",
        "default_base_url": "http://localhost:11434/v1",
        "default_model": "qwen3.5:latest",
        "api_format": "openai",
        "needs_key": False,
        "model_choices": ["qwen3.5:latest", "qwen3.5:4b", "qwen3.5:9b", "qwen3.5:27b"],
    },
    "ollama-other": {
        "label": "Ollama (other)",
        "default_base_url": "http://localhost:11434/v1",
        "default_model": "mistral-nemo:latest",
        "api_format": "openai",
        "needs_key": False,
        "model_choices": ["mistral-nemo:latest", "deepseek-r1:14b", "llama3.1:8b", "gemma2:9b"],
    },
    "claude-haiku": {
        "label": "Claude Haiku",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-haiku-4-5-20251001",
        "api_format": "anthropic",
        "needs_key": True,
        "model_choices": ["claude-haiku-4-5-20251001"],
    },
    "claude-sonnet": {
        "label": "Claude Sonnet",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-sonnet-4-6",
        "api_format": "anthropic",
        "needs_key": True,
        "model_choices": ["claude-sonnet-4-6"],
    },
    "claude-opus": {
        "label": "Claude Opus",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-opus-4-6",
        "api_format": "anthropic",
        "needs_key": True,
        "model_choices": ["claude-opus-4-6"],
    },
    "chatgpt": {
        "label": "ChatGPT",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-5.4",
        "api_format": "openai",
        "needs_key": True,
        "model_choices": ["gpt-5.4", "gpt-5.4-pro", "gpt-5-mini", "gpt-4o"],
    },
}


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str = ""


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0


# -- Tool definitions for OpenAI format --

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
    {
        "type": "function",
        "function": {
            "name": "add_to_backlog",
            "description": "Add a bug or feature to the project backlog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug",
                    },
                    "kind": {
                        "type": "string",
                        "description": "Type of item: 'bug' or 'feature'",
                        "enum": ["bug", "feature"],
                    },
                    "title": {
                        "type": "string",
                        "description": "Short description of the bug or feature",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "enum": ["Low", "Medium", "High", "Critical"],
                    },
                },
                "required": ["slug", "kind", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sprint_status",
            "description": "Check the current sprint status for an Afterburner project — how many agents are done, which are still running.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug (optional — defaults to active project)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_vision",
            "description": "Generate an Afterburner Vision document from structured discovery data. Call this after gathering problem, users, use cases, differentiators, and success criteria from the customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Product name for the Vision doc heading",
                    },
                    "problem": {
                        "type": "string",
                        "description": "Problem statement",
                    },
                    "users": {
                        "type": "string",
                        "description": "Target audience / user personas",
                    },
                    "use_cases": {
                        "type": "string",
                        "description": "Key use cases, one per line",
                    },
                    "differentiators": {
                        "type": "string",
                        "description": "What makes this product unique",
                    },
                    "success_criteria": {
                        "type": "string",
                        "description": "Measurable success criteria, one per line",
                    },
                    "slug": {
                        "type": "string",
                        "description": "Project slug (optional — defaults to active project)",
                    },
                },
                "required": ["problem", "users"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "feedback_on_sprint",
            "description": "Read the latest PROJECT_STATUS document and summarize what was shipped in the most recent sprint. Use this to give the customer a summary and ask if it matches their expectations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug (optional — defaults to active project)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all registered Afterburner projects. Call this when the user asks what projects exist, wants to see all projects, or needs to pick a project.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_project_doc",
            "description": "Read a file from a project's directory. Use this to understand what a project does by reading its README.md, or to check specific files like package.json, pyproject.toml, CLAUDE.md, etc. Call this when get_project_summary returns empty data and you need to learn about the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Project slug (e.g. 'tool-s3-cloudfront-push')",
                    },
                    "path": {
                        "type": "string",
                        "description": "Relative file path within the project (default: README.md)",
                    },
                },
                "required": ["slug"],
            },
        },
    },
]


# Tools that modify project files — blocked for unauthenticated users
WRITE_TOOL_NAMES = {"save_discovery", "add_to_backlog", "generate_vision"}

# Read-only subset of TOOL_DEFINITIONS (safe for any user)
READ_ONLY_TOOLS: list[dict] = [
    t for t in TOOL_DEFINITIONS
    if t.get("function", {}).get("name") not in WRITE_TOOL_NAMES
]


def _openai_tools_to_anthropic(tools: list[dict]) -> list[dict]:
    """Convert OpenAI-format tool definitions to Anthropic's tool format."""
    result = []
    for tool in tools:
        fn = tool.get("function", {})
        result.append({
            "name": fn.get("name", ""),
            "description": fn.get("description", ""),
            "input_schema": fn.get("parameters", {}),
        })
    return result


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
        """Stream a chat completion, yielding content chunks."""
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

                    chunk = msg.get("content", "")
                    if chunk:
                        full_content += chunk
                        yield chunk

                    for tc in msg.get("tool_calls", []):
                        fn = tc.get("function", {})
                        tool_calls.append(
                            ToolCall(
                                name=fn.get("name", ""),
                                arguments=fn.get("arguments", {}),
                            )
                        )

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


class OpenAICompatibleClient:
    """Chat completion via OpenAI-compatible API (works for Ollama /v1 and ChatGPT)."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = "http://localhost:11434/v1",
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.needs_key = api_key is not None and api_key != "ollama"
        self._client = OpenAI(
            base_url=self.base_url,
            api_key=api_key or "ollama",
            timeout=timeout,
        )

    def chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request."""
        all_messages: list[dict] = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
        }
        if tools:
            kwargs["tools"] = tools

        start = time.monotonic()
        try:
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            log.error("OpenAI-compatible request failed: %s", exc)
            return LLMResponse(
                content=f"Sorry, I'm having trouble connecting to the LLM. ({exc})",
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        duration_ms = int((time.monotonic() - start) * 1000)
        choice = resp.choices[0] if resp.choices else None
        content = choice.message.content or "" if choice else ""

        tool_calls: list[ToolCall] = []
        if choice and choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append(ToolCall(name=tc.function.name, arguments=args))

        usage = resp.usage
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            duration_ms=duration_ms,
        )

    def health_check(self) -> bool:
        """Check if the API endpoint is reachable."""
        try:
            if self.needs_key:
                # For cloud APIs, just check key exists
                return bool(self._client.api_key and len(self._client.api_key) > 5)
            # For local (Ollama), actually check the endpoint
            self._client.models.list()
            return True
        except Exception:
            return False

    def close(self) -> None:
        self._client.close()


class AnthropicClient:
    """Chat completion via the Anthropic SDK."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        base_url: str = "https://api.anthropic.com",
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        import anthropic

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.Anthropic(
            api_key=resolved_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    def chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request to the Anthropic API."""
        # Filter out system messages — Claude uses a separate system parameter
        filtered = [m for m in messages if m.get("role") != "system"]

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": filtered,
            "max_tokens": 4096,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = _openai_tools_to_anthropic(tools)

        start = time.monotonic()
        try:
            resp = self._client.messages.create(**kwargs)
        except Exception as exc:
            log.error("Anthropic request failed: %s", exc)
            return LLMResponse(
                content=f"Sorry, I'm having trouble connecting to the LLM. ({exc})",
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        duration_ms = int((time.monotonic() - start) * 1000)

        content_parts = []
        tool_calls: list[ToolCall] = []
        for block in resp.content:
            if block.type == "text":
                content_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(name=block.name, arguments=block.input or {}, id=block.id)
                )

        usage = resp.usage
        return LLMResponse(
            content="\n".join(content_parts),
            tool_calls=tool_calls,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
            duration_ms=duration_ms,
        )

    def health_check(self) -> bool:
        """Check if the Anthropic API key is configured."""
        # Don't send a real API call — just verify key exists and looks valid
        try:
            return bool(self._client.api_key and len(self._client.api_key) > 10)
        except Exception:
            return False

    def close(self) -> None:
        self._client.close()


def get_client(
    provider_id: str,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> OllamaClient | OpenAICompatibleClient | AnthropicClient:
    """Factory: return the right LLM client for a given provider ID."""
    if provider_id not in LLM_PROVIDERS:
        raise ValueError(f"Unknown LLM provider: '{provider_id}'. Available: {list(LLM_PROVIDERS.keys())}")

    provider = LLM_PROVIDERS[provider_id]
    resolved_url = base_url or provider["default_base_url"]
    resolved_model = model or provider["default_model"]

    if provider["api_format"] == "anthropic":
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        return AnthropicClient(
            model=resolved_model,
            base_url=resolved_url,
            api_key=resolved_key,
        )
    elif not provider["needs_key"]:
        # Local Ollama — use native /api/chat for accurate token counts
        # (the /v1 OpenAI-compat endpoint inflates counts with thinking tokens)
        ollama_url = resolved_url.rstrip("/")
        if ollama_url.endswith("/v1"):
            ollama_url = ollama_url[:-3]
        return OllamaClient(
            model=resolved_model,
            base_url=ollama_url,
        )
    else:
        # Cloud OpenAI-compatible (ChatGPT)
        resolved_key = api_key
        if not resolved_key:
            resolved_key = os.environ.get("OPENAI_API_KEY", "")
        return OpenAICompatibleClient(
            model=resolved_model,
            base_url=resolved_url,
            api_key=resolved_key,
        )
