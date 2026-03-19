"""Gateway — the central brain that connects transports to the LLM.

Transport-agnostic: receives text + chat_id, returns response text.
Handles personality loading, memory management, and tool execution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .llm import TOOL_DEFINITIONS, LLMResponse, OllamaLLM
from .memory import ChatMemory
from .personality import Personality
from .tools import execute_tool

log = logging.getLogger(__name__)


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
    ) -> None:
        self.personality = Personality(personality_name)
        self.system_prompt = self.personality.to_system_prompt()
        self.principles = self.personality.get_principles()
        self.llm = OllamaLLM(model=model, base_url=ollama_url)
        self._memories: dict[str, ChatMemory] = {}

    def process_message(self, chat_id: str, text: str) -> GatewayResponse:
        """Process a user message and return the bot's response.

        This is the main entry point — all transports call this.
        """
        memory = self._get_memory(chat_id)
        memory.add_message("user", text)

        # Build context from conversation history
        messages = memory.get_context_messages()

        # Call LLM
        llm_resp = self.llm.chat(
            messages=messages,
            system_prompt=self.system_prompt,
            tools=TOOL_DEFINITIONS,
        )

        # Handle tool calls if any
        tools_called: list[dict[str, Any]] = []
        if llm_resp.tool_calls:
            tools_called = self._handle_tool_calls(llm_resp, messages, memory)

        # Get final response text
        response_text = llm_resp.content or "I'm thinking about that..."

        # Save assistant response
        memory.add_message("assistant", response_text)

        return GatewayResponse(
            text=response_text,
            tools_called=tools_called,
            principles=self.principles,
            memory_count=memory.message_count(),
            input_tokens=llm_resp.input_tokens,
            output_tokens=llm_resp.output_tokens,
            duration_ms=llm_resp.duration_ms,
        )

    def _handle_tool_calls(
        self,
        llm_resp: LLMResponse,
        messages: list[dict],
        memory: ChatMemory,
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

    def _get_memory(self, chat_id: str) -> ChatMemory:
        """Get or create memory for a chat session."""
        if chat_id not in self._memories:
            self._memories[chat_id] = ChatMemory(chat_id)
        return self._memories[chat_id]

    def get_personality_info(self) -> dict:
        """Return personality metadata for debug panels."""
        return {
            "name": self.personality.name,
            "principles": self.principles,
            "model": self.llm.model,
        }

    def health_check(self) -> dict:
        """Check system health."""
        ollama_ok = self.llm.health_check()
        return {
            "ollama": "ok" if ollama_ok else "unavailable",
            "personality": self.personality.name,
            "model": self.llm.model,
        }
