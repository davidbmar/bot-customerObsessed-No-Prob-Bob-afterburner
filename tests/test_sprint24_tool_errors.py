"""Tests for Sprint 24 — tool error handling in gateway (F-063)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, ToolCall


# -- Fixtures --

@pytest.fixture
def personalities_dir() -> Path:
    return Path(__file__).parent.parent / "personalities"


@pytest.fixture
def mock_llm_chat():
    def fake_chat(messages, system_prompt=None, tools=None):
        return LLMResponse(content="Mock response", duration_ms=10)

    with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
        yield


@pytest.fixture
def gateway(personalities_dir, mock_llm_chat) -> Gateway:
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(personalities_dir),
    )


# =============================================================================
# Task — Tool error handling (F-063)
# =============================================================================


class TestToolErrorHandling:
    """Verify gateway catches tool errors and returns a response instead of crashing."""

    def test_execute_tool_exception_returns_response(self, gateway):
        """When execute_tool raises, gateway catches it and returns a valid response."""
        llm_resp = LLMResponse(
            content="Let me check that.",
            tool_calls=[
                ToolCall(name="get_sprint_status", arguments={}, id=""),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "What's the status?"}]

        with patch("bot.gateway.execute_tool", side_effect=RuntimeError("connection refused")):
            with patch("bot.llm.OllamaClient.chat", return_value=LLMResponse(content="Sorry, I had trouble.", duration_ms=10)):
                tools = gateway._handle_tool_calls(llm_resp, messages)

        # Should return tools_called list, not crash
        assert len(tools) == 1
        assert tools[0]["name"] == "get_sprint_status"
        assert "get_sprint_status" in tools[0]["result"]
        assert "connection refused" in tools[0]["result"]

    def test_error_message_includes_tool_name(self, gateway):
        """Error result from a failing tool includes the tool name."""
        llm_resp = LLMResponse(
            content="Saving.",
            tool_calls=[
                ToolCall(name="save_discovery", arguments={"slug": "t", "content": "x"}, id=""),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "Save my notes"}]

        with patch("bot.gateway.execute_tool", side_effect=ValueError("missing field")):
            with patch("bot.llm.OllamaClient.chat", return_value=LLMResponse(content="Oops.", duration_ms=10)):
                tools = gateway._handle_tool_calls(llm_resp, messages)

        assert "save_discovery" in tools[0]["result"]

    def test_tool_error_injects_system_note(self, gateway):
        """When a tool fails, the follow-up LLM call receives a system note about the error."""
        llm_resp = LLMResponse(
            content="Checking.",
            tool_calls=[
                ToolCall(name="get_sprint_status", arguments={}, id=""),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "Status?"}]

        captured_system_prompts = []

        def capture_chat(messages, system_prompt=None, tools=None):
            captured_system_prompts.append(system_prompt)
            return LLMResponse(content="I had trouble checking.", duration_ms=10)

        with patch("bot.gateway.execute_tool", side_effect=RuntimeError("timeout")):
            with patch("bot.llm.OllamaClient.chat", side_effect=capture_chat):
                gateway._handle_tool_calls(llm_resp, messages)

        # The follow-up call should have the error note in the system prompt
        assert len(captured_system_prompts) == 1
        assert "tool calls encountered errors" in captured_system_prompts[0]
        assert "get_sprint_status" in captured_system_prompts[0]

    def test_successful_tool_no_error_note(self, gateway):
        """When tools succeed, no error note is injected into the follow-up system prompt."""
        llm_resp = LLMResponse(
            content="Checking.",
            tool_calls=[
                ToolCall(name="get_sprint_status", arguments={}, id=""),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "Status?"}]

        captured_system_prompts = []

        def capture_chat(messages, system_prompt=None, tools=None):
            captured_system_prompts.append(system_prompt)
            return LLMResponse(content="Here's the status.", duration_ms=10)

        with patch("bot.gateway.execute_tool", return_value="Sprint 24 is in progress"):
            with patch("bot.llm.OllamaClient.chat", side_effect=capture_chat):
                gateway._handle_tool_calls(llm_resp, messages)

        assert len(captured_system_prompts) == 1
        assert "tool calls encountered errors" not in captured_system_prompts[0]

    def test_unknown_tool_detected_as_error(self, gateway):
        """execute_tool returning 'Unknown tool:' is detected as an error."""
        llm_resp = LLMResponse(
            content="Let me try.",
            tool_calls=[
                ToolCall(name="nonexistent_tool", arguments={}, id=""),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "Do something"}]

        captured_system_prompts = []

        def capture_chat(messages, system_prompt=None, tools=None):
            captured_system_prompts.append(system_prompt)
            return LLMResponse(content="I don't have that tool.", duration_ms=10)

        with patch("bot.llm.OllamaClient.chat", side_effect=capture_chat):
            gateway._handle_tool_calls(llm_resp, messages)

        assert len(captured_system_prompts) == 1
        assert "tool calls encountered errors" in captured_system_prompts[0]
