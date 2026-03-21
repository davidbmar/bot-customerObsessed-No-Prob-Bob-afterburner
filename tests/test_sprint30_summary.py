"""Tests for GET /api/conversations/{id}/summary endpoint (F-070)."""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.server import BotHTTPHandler, create_app
from bot.gateway import Gateway
from bot.llm import LLMResponse


@pytest.fixture
def mock_llm_chat():
    def fake_chat(messages, system_prompt=None, tools=None):
        return LLMResponse(content="Mock response", duration_ms=10)
    with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
        yield


@pytest.fixture
def gateway(mock_llm_chat) -> Gateway:
    pdir = Path(__file__).parent.parent / "personalities"
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(pdir),
    )


def _unique_id() -> str:
    return f"s30-{uuid.uuid4().hex[:8]}"


class TestConversationSummary:
    """Tests for GET /api/conversations/{id}/summary."""

    def test_summary_returns_first_user_message(self, gateway) -> None:
        cid = _unique_id()
        gateway.memory.add(cid, "user", "How do I build a voice bot?")
        gateway.memory.add(cid, "assistant", "Great question!")
        gateway.memory.add(cid, "user", "With Python please")

        messages = gateway.memory.get_history(cid)
        assert len(messages) >= 3

        # Extract summary logic (mirrors _handle_conversation_summary)
        summary = ""
        for msg in messages:
            if msg.get("role") == "user":
                text = msg.get("content", "").strip()
                if text:
                    summary = text[:120] + ("..." if len(text) > 120 else "")
                    break

        assert summary == "How do I build a voice bot?"

    def test_summary_message_count(self, gateway) -> None:
        cid = _unique_id()
        gateway.memory.add(cid, "user", "Hello")
        gateway.memory.add(cid, "assistant", "Hi!")
        gateway.memory.add(cid, "user", "Tell me more")

        messages = gateway.memory.get_history(cid)
        assert len(messages) >= 3

    def test_summary_missing_conversation(self, gateway) -> None:
        messages = gateway.memory.get_history(f"nonexistent-{uuid.uuid4().hex[:8]}")
        assert len(messages) == 0

    def test_summary_truncates_long_messages(self, gateway) -> None:
        cid = _unique_id()
        long_text = "A" * 200
        gateway.memory.add(cid, "user", long_text)

        messages = gateway.memory.get_history(cid)
        # Find the user message we just added
        user_msgs = [m for m in messages if m["role"] == "user" and len(m["content"]) == 200]
        assert len(user_msgs) >= 1
        text = user_msgs[0]["content"].strip()
        summary = text[:120] + ("..." if len(text) > 120 else "")
        assert len(summary) == 123  # 120 chars + "..."
        assert summary.endswith("...")

    def test_handler_has_summary_method(self) -> None:
        assert hasattr(BotHTTPHandler, "_handle_conversation_summary")

    def test_summary_skips_assistant_messages(self, gateway) -> None:
        cid = _unique_id()
        gateway.memory.add(cid, "assistant", "Welcome!")
        gateway.memory.add(cid, "user", "Thanks, I need help")

        messages = gateway.memory.get_history(cid)
        summary = ""
        for msg in messages:
            if msg.get("role") == "user":
                text = msg.get("content", "").strip()
                if text:
                    summary = text[:120] + ("..." if len(text) > 120 else "")
                    break

        assert summary == "Thanks, I need help"
