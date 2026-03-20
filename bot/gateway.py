"""Gateway — the central brain that connects transports to the LLM.

Transport-agnostic: receives text + chat_id, returns response text.
Handles personality loading, memory management, and tool execution.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Generator

from .llm import TOOL_DEFINITIONS, LLMResponse, OllamaClient, get_client, LLM_PROVIDERS
from .memory import ConversationMemory
from .personality import PersonalityLoader
from .tools import execute_tool, set_config

log = logging.getLogger(__name__)

SYNTHESIS_THRESHOLD = 5
SYNTHESIS_PROMPT_SUFFIX = (
    "\n\nYou have had enough exchanges. In your next response, synthesize the "
    "conversation into a structured summary with sections: Problem, Users, "
    "Use Cases, Success Criteria. Present this as a formatted summary."
)


@dataclass
class GatewayResponse:
    """What we return to transports after processing a message."""

    text: str
    tools_called: list[dict[str, Any]] = field(default_factory=list)
    principles: list[str] = field(default_factory=list)
    memory_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0


class Gateway:
    """Central message handler — connects any transport to the LLM."""

    def __init__(
        self,
        personality_name: str = "customer-discovery",
        model: str = "qwen3:4b",
        ollama_url: str = "http://localhost:11434",
        personalities_dir: str | Path | None = None,
        config: Any = None,
        provider_id: str | None = None,
    ) -> None:
        from pathlib import Path as _Path
        pdir = _Path(personalities_dir) if personalities_dir else _Path(__file__).parent.parent / "personalities"
        self._personality_loader = PersonalityLoader(pdir)
        self.personality = self._personality_loader.load(personality_name)
        self.system_prompt = self.personality.system_prompt
        self.principles = self.personality.principles

        # If a provider_id is given, use the multi-provider factory
        if provider_id and provider_id in LLM_PROVIDERS:
            self._provider_id = provider_id
            self.llm = get_client(provider_id, model=model)
        else:
            self._provider_id = None
            self.llm = OllamaClient(model=model, base_url=ollama_url)

        self.memory = ConversationMemory()
        self._exchange_counts: dict[str, int] = {}
        self._synthesis_triggered: dict[str, bool] = {}
        self.config = config
        if config:
            set_config(config)

    def switch_provider(self, provider_id: str, model: str | None = None) -> None:
        """Swap the LLM client at runtime to a different provider."""
        from .llm_config import load_provider_config, set_active_provider

        if provider_id not in LLM_PROVIDERS:
            raise ValueError(f"Unknown provider: '{provider_id}'")

        cfg = load_provider_config(provider_id)
        resolved_model = model or cfg.get("model") or LLM_PROVIDERS[provider_id]["default_model"]
        api_key = cfg.get("api_key", "")
        base_url = cfg.get("base_url") or LLM_PROVIDERS[provider_id]["default_base_url"]

        old = self.llm
        self.llm = get_client(
            provider_id,
            base_url=base_url,
            model=resolved_model,
            api_key=api_key,
        )
        self._provider_id = provider_id
        set_active_provider(provider_id)

        if hasattr(old, "close"):
            try:
                old.close()
            except Exception:
                pass

        log.info("Switched LLM provider to %s (model=%s)", provider_id, resolved_model)

    def _get_system_prompt(self, chat_id: str) -> str:
        """Return the system prompt, appending synthesis instruction if threshold reached."""
        count = self._exchange_counts.get(chat_id, 0)
        if count >= SYNTHESIS_THRESHOLD and not self._synthesis_triggered.get(chat_id, False):
            self._synthesis_triggered[chat_id] = True
            return self.system_prompt + SYNTHESIS_PROMPT_SUFFIX
        return self.system_prompt

    def process_message(self, chat_id: str, text: str) -> GatewayResponse:
        """Process a user message and return the bot's response.

        This is the main entry point — all transports call this.
        """
        self.memory.add(chat_id, "user", text)
        self._exchange_counts[chat_id] = self._exchange_counts.get(chat_id, 0) + 1

        # Build context from conversation history
        history = self.memory.get_history(chat_id, limit=20)
        messages = [{"role": m["role"], "content": m["content"]} for m in history]

        system_prompt = self._get_system_prompt(chat_id)

        # Call LLM
        llm_resp = self.llm.chat(
            messages=messages,
            system_prompt=system_prompt,
            tools=TOOL_DEFINITIONS,
        )

        # Handle tool calls if any
        tools_called: list[dict[str, Any]] = []
        if llm_resp.tool_calls:
            tools_called = self._handle_tool_calls(llm_resp, messages)

        # Get final response text
        response_text = llm_resp.content or "I'm thinking about that..."

        # Save assistant response
        self.memory.add(chat_id, "assistant", response_text)

        return GatewayResponse(
            text=response_text,
            tools_called=tools_called,
            principles=self.principles,
            memory_count=self.memory.message_count(chat_id),
            input_tokens=llm_resp.input_tokens,
            output_tokens=llm_resp.output_tokens,
            duration_ms=llm_resp.duration_ms,
        )

    def process_message_stream(
        self, chat_id: str, text: str
    ) -> Generator[dict, None, GatewayResponse]:
        """Process a user message, streaming token chunks back.

        Yields dicts like {"type": "token", "content": "word"}.
        Returns the final GatewayResponse (accessible via StopIteration.value).
        Falls back to non-streaming for clients without chat_stream().
        """
        self.memory.add(chat_id, "user", text)
        self._exchange_counts[chat_id] = self._exchange_counts.get(chat_id, 0) + 1

        history = self.memory.get_history(chat_id, limit=20)
        messages = [{"role": m["role"], "content": m["content"]} for m in history]

        system_prompt = self._get_system_prompt(chat_id)
        start = time.monotonic()

        # Check if the LLM client supports streaming
        if not hasattr(self.llm, "chat_stream"):
            # Fallback: non-streaming, yield full response as one chunk
            llm_resp = self.llm.chat(
                messages=messages,
                system_prompt=system_prompt,
                tools=TOOL_DEFINITIONS,
            )
            tools_called: list[dict[str, Any]] = []
            if llm_resp.tool_calls:
                tools_called = self._handle_tool_calls(llm_resp, messages)

            response_text = llm_resp.content or "I'm thinking about that..."
            yield {"type": "token", "content": response_text}
        else:
            # Streaming path
            gen = self.llm.chat_stream(
                messages=messages,
                system_prompt=system_prompt,
                tools=TOOL_DEFINITIONS,
            )
            full_content = ""
            llm_resp = None
            try:
                while True:
                    chunk = next(gen)
                    full_content += chunk
                    yield {"type": "token", "content": chunk}
            except StopIteration as e:
                llm_resp = e.value

            if llm_resp is None:
                from .llm import LLMResponse as _LR
                llm_resp = _LR(content=full_content, duration_ms=int((time.monotonic() - start) * 1000))

            tools_called = []
            if llm_resp.tool_calls:
                tools_called = self._handle_tool_calls(llm_resp, messages)

            response_text = llm_resp.content or full_content or "I'm thinking about that..."

        duration_ms = llm_resp.duration_ms if llm_resp else int((time.monotonic() - start) * 1000)

        self.memory.add(chat_id, "assistant", response_text)

        return GatewayResponse(
            text=response_text,
            tools_called=tools_called,
            principles=self.principles,
            memory_count=self.memory.message_count(chat_id),
            input_tokens=llm_resp.input_tokens if llm_resp else 0,
            output_tokens=llm_resp.output_tokens if llm_resp else 0,
            duration_ms=duration_ms,
        )

    def _handle_tool_calls(
        self,
        llm_resp: LLMResponse,
        messages: list[dict],
    ) -> list[dict[str, Any]]:
        """Execute tool calls and re-query the LLM with results."""
        tools_called: list[dict[str, Any]] = []

        for tc in llm_resp.tool_calls:
            log.info("Tool call: %s(%s)", tc.name, tc.arguments)
            result = execute_tool(tc.name, tc.arguments)
            tools_called.append({
                "name": tc.name,
                "arguments": tc.arguments,
                "result": result,
            })

            # Add tool result to conversation for the follow-up LLM call
            messages.append({
                "role": "assistant",
                "content": llm_resp.content or "",
            })
            messages.append({
                "role": "tool",
                "content": result,
            })

        # Re-query LLM with tool results so it can respond naturally
        follow_up = self.llm.chat(
            messages=messages,
            system_prompt=self.system_prompt,
        )
        if follow_up.content:
            llm_resp.content = follow_up.content
            llm_resp.duration_ms += follow_up.duration_ms
            llm_resp.output_tokens += follow_up.output_tokens

        return tools_called

    def reload_personality(self) -> None:
        """Re-read the current personality from disk (hot-reload)."""
        self.personality = self._personality_loader.load(self.personality.name)
        self.system_prompt = self.personality.system_prompt
        self.principles = self.personality.principles
        log.info("Reloaded personality: %s", self.personality.name)

    def get_personality_info(self) -> dict:
        """Return personality metadata for debug panels."""
        return {
            "name": self.personality.name,
            "principles": self.principles,
            "model": self.llm.model,
        }

    def health_check(self) -> dict:
        """Check system health."""
        llm_ok = self.llm.health_check()
        provider = self._provider_id or "ollama"
        provider_label = LLM_PROVIDERS.get(provider, {}).get("label", provider) if provider else "ollama"
        status = "ok" if llm_ok else "unavailable"
        return {
            "status": status,
            "ollama": status,  # backward compat
            "personality": self.personality.name,
            "model": self.llm.model,
            "provider": provider,
            "provider_label": provider_label,
        }
