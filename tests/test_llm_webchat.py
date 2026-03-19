"""Tests for the LLM webchat components (agentB scope)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bot.llm import DEFAULT_MODEL, OllamaClient, LLMResponse, ToolCall, TOOL_DEFINITIONS
from bot.gateway import Gateway, GatewayResponse
from bot.server import BotHTTPHandler, CHAT_UI_PATH


# -- OllamaClient tests --

class TestOllamaClient:
    def test_default_model(self):
        client = OllamaClient()
        assert client.model == "qwen3.5:latest"
        assert client.base_url == "http://localhost:11434"
        client.close()

    def test_custom_model(self):
        client = OllamaClient(model="llama3:8b", base_url="http://other:11434")
        assert client.model == "llama3:8b"
        assert client.base_url == "http://other:11434"
        client.close()

    def test_chat_error_returns_response(self):
        """When Ollama is unreachable, chat() returns an error LLMResponse."""
        client = OllamaClient(base_url="http://localhost:99999", timeout=1.0)
        resp = client.chat([{"role": "user", "content": "hi"}])
        assert isinstance(resp, LLMResponse)
        assert "trouble connecting" in resp.content
        assert resp.duration_ms > 0
        client.close()

    def test_build_messages_with_system_prompt(self):
        client = OllamaClient()
        msgs = client._build_messages(
            [{"role": "user", "content": "hi"}],
            system_prompt="You are helpful.",
        )
        assert msgs[0]["role"] == "system"
        assert msgs[0]["content"] == "You are helpful."
        assert msgs[1]["role"] == "user"
        client.close()

    def test_build_messages_without_system_prompt(self):
        client = OllamaClient()
        msgs = client._build_messages(
            [{"role": "user", "content": "hi"}],
            system_prompt=None,
        )
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"
        client.close()


# -- LLMResponse / ToolCall dataclasses --

class TestDataclasses:
    def test_llm_response_defaults(self):
        resp = LLMResponse(content="hello")
        assert resp.content == "hello"
        assert resp.tool_calls == []
        assert resp.input_tokens == 0

    def test_tool_call(self):
        tc = ToolCall(name="save_discovery", arguments={"slug": "test"})
        assert tc.name == "save_discovery"
        assert tc.arguments["slug"] == "test"


# -- Tool definitions --

class TestToolDefinitions:
    def test_tool_definitions_structure(self):
        assert len(TOOL_DEFINITIONS) >= 2
        for td in TOOL_DEFINITIONS:
            assert td["type"] == "function"
            assert "function" in td
            assert "name" in td["function"]
            assert "parameters" in td["function"]


# -- Chat UI --

class TestChatUI:
    def test_chat_ui_exists(self):
        assert CHAT_UI_PATH.exists(), "chat_ui.html must exist"

    def test_chat_ui_contains_dark_theme(self):
        content = CHAT_UI_PATH.read_text()
        assert "--bg: #0d1117" in content

    def test_chat_ui_has_debug_panel(self):
        content = CHAT_UI_PATH.read_text()
        assert "debug-panel" in content
        assert "collapsed" in content  # collapsible support

    def test_chat_ui_has_new_conversation_button(self):
        content = CHAT_UI_PATH.read_text()
        assert "newConversation" in content
        assert "New Chat" in content

    def test_chat_ui_uses_conversation_id(self):
        content = CHAT_UI_PATH.read_text()
        assert "conversation_id" in content

    def test_chat_ui_has_latency_display(self):
        content = CHAT_UI_PATH.read_text()
        assert "debugLatency" in content
        assert "duration_ms" in content


# -- Gateway --

class TestGateway:
    def test_gateway_init(self):
        gw = Gateway()
        assert gw.personality.name == "customer-discovery"
        assert gw.llm.model == "qwen3.5:latest"
        assert len(gw.principles) > 0

    def test_personality_info(self):
        gw = Gateway()
        info = gw.get_personality_info()
        assert info["name"] == "customer-discovery"
        assert "Customer Obsession" in info["principles"]
        assert info["model"] == "qwen3.5:latest"

    def test_get_memory_creates_new(self):
        gw = Gateway()
        mem = gw._get_memory("test-conv-1")
        assert mem.chat_id == "test-conv-1"
        # Same ID returns same instance
        mem2 = gw._get_memory("test-conv-1")
        assert mem is mem2

    def test_gateway_response_fields(self):
        resp = GatewayResponse(
            text="hello",
            tools_called=[],
            principles=["p1"],
            memory_count=2,
            input_tokens=10,
            output_tokens=5,
            duration_ms=100,
        )
        assert resp.text == "hello"
        assert resp.duration_ms == 100


# -- Server API field naming --

class TestServerAPI:
    def test_api_chat_uses_conversation_id(self):
        """The /api/chat endpoint accepts conversation_id parameter."""
        import inspect
        source = inspect.getsource(BotHTTPHandler._handle_chat)
        assert "conversation_id" in source

    def test_api_response_includes_principles_active(self):
        """The /api/chat response uses principles_active key."""
        import inspect
        source = inspect.getsource(BotHTTPHandler._handle_chat)
        assert "principles_active" in source
