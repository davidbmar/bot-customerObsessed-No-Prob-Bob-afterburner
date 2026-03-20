"""Tests for Sprint 14 — conversation sidebar, token fix, cost display, provider label."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.llm import (
    LLM_PROVIDERS,
    LLMResponse,
    OllamaClient,
    OpenAICompatibleClient,
    AnthropicClient,
    get_client,
)
from bot.gateway import Gateway, GatewayResponse


# -- Token count accuracy --

class TestTokenCountFix:
    """B-018: Verify Ollama providers use OllamaClient for accurate token counts."""

    def test_qwen_uses_ollama_client(self):
        client = get_client("qwen-3.5")
        assert isinstance(client, OllamaClient)
        client.close()

    def test_ollama_other_uses_ollama_client(self):
        client = get_client("ollama-other")
        assert isinstance(client, OllamaClient)
        client.close()

    def test_chatgpt_still_uses_openai_client(self):
        client = get_client("chatgpt", api_key="fake-key")
        assert isinstance(client, OpenAICompatibleClient)
        client.close()

    def test_claude_still_uses_anthropic_client(self):
        client = get_client("claude-sonnet", api_key="fake-key")
        assert isinstance(client, AnthropicClient)
        client.close()

    def test_ollama_strips_v1_from_url(self):
        client = get_client("qwen-3.5", base_url="http://localhost:11434/v1")
        assert isinstance(client, OllamaClient)
        assert client.base_url == "http://localhost:11434"
        client.close()

    def test_ollama_preserves_non_v1_url(self):
        client = get_client("qwen-3.5", base_url="http://localhost:11434")
        assert client.base_url == "http://localhost:11434"
        client.close()

    def test_ollama_response_uses_eval_count(self):
        """OllamaClient parses eval_count for accurate output tokens."""
        client = OllamaClient()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "message": {"content": "Hello world"},
            "prompt_eval_count": 50,
            "eval_count": 12,
        }
        mock_resp.raise_for_status = MagicMock()
        with patch.object(client._client, "post", return_value=mock_resp):
            result = client.chat([{"role": "user", "content": "hi"}])
        assert result.output_tokens == 12
        assert result.input_tokens == 50
        client.close()

    def test_llm_response_dataclass_fields(self):
        resp = LLMResponse(content="test", input_tokens=100, output_tokens=25, duration_ms=500)
        assert resp.input_tokens == 100
        assert resp.output_tokens == 25
        assert resp.duration_ms == 500


# -- Provider label display --

class TestProviderLabelFix:
    """B-019: Verify health check returns provider_label for display."""

    def test_health_check_includes_provider_label(self):
        gw = Gateway()
        health = gw.health_check()
        assert "provider_label" in health

    def test_health_check_label_for_default_provider(self):
        gw = Gateway()
        health = gw.health_check()
        # Default provider defaults to "qwen-3.5" (B-019 fix)
        assert health["provider_label"] == "Qwen 3.5"

    def test_health_check_label_for_qwen(self):
        gw = Gateway(provider_id="qwen-3.5")
        health = gw.health_check()
        assert health["provider_label"] == "Qwen 3.5"

    def test_all_providers_have_labels(self):
        for pid, pinfo in LLM_PROVIDERS.items():
            assert "label" in pinfo, f"Provider {pid} missing label"
            assert pinfo["label"], f"Provider {pid} has empty label"


# -- Cost calculation --

class TestCostCalculation:
    """F-030: Token cost display for paid providers."""

    # These mirror the JS TOKEN_PRICES constants
    PRICES = {
        "claude-haiku":  {"input": 0.25,  "output": 1.25},
        "claude-sonnet": {"input": 3.00,  "output": 15.00},
        "claude-opus":   {"input": 15.00, "output": 75.00},
        "chatgpt":       {"input": 2.50,  "output": 10.00},
    }

    def _calc(self, provider_id, input_tokens, output_tokens):
        prices = self.PRICES.get(provider_id)
        if not prices:
            return None
        return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

    def test_claude_haiku_cost(self):
        cost = self._calc("claude-haiku", 1000, 500)
        expected = (1000 * 0.25 + 500 * 1.25) / 1_000_000
        assert abs(cost - expected) < 1e-10

    def test_claude_sonnet_cost(self):
        cost = self._calc("claude-sonnet", 1000, 500)
        expected = (1000 * 3.00 + 500 * 15.00) / 1_000_000
        assert abs(cost - expected) < 1e-10

    def test_claude_opus_cost(self):
        cost = self._calc("claude-opus", 1000, 500)
        expected = (1000 * 15.00 + 500 * 75.00) / 1_000_000
        assert abs(cost - expected) < 1e-10

    def test_chatgpt_cost(self):
        cost = self._calc("chatgpt", 1000, 500)
        expected = (1000 * 2.50 + 500 * 10.00) / 1_000_000
        assert abs(cost - expected) < 1e-10

    def test_ollama_is_free(self):
        assert self._calc("qwen-3.5", 1000, 500) is None
        assert self._calc("ollama-other", 1000, 500) is None

    def test_zero_tokens_zero_cost(self):
        assert self._calc("claude-haiku", 0, 0) == 0.0


# -- Conversation sidebar in HTML --

class TestConversationSidebar:
    """F-032: Conversation list sidebar in chat_ui.html."""

    @pytest.fixture
    def chat_html(self):
        return (Path(__file__).parent.parent / "bot" / "chat_ui.html").read_text()

    def test_sidebar_html_exists(self, chat_html):
        assert "conv-sidebar" in chat_html

    def test_sidebar_has_conv_list(self, chat_html):
        assert "convList" in chat_html

    def test_sidebar_has_new_chat_button(self, chat_html):
        assert "btn-new-chat" in chat_html

    def test_sidebar_toggle_function(self, chat_html):
        assert "toggleSidebar" in chat_html

    def test_sidebar_toggle_button(self, chat_html):
        assert "sidebarToggle" in chat_html

    def test_refresh_conversation_list_function(self, chat_html):
        assert "refreshConversationList" in chat_html

    def test_switch_conversation_function(self, chat_html):
        assert "switchToConversation" in chat_html

    def test_sidebar_reads_localstorage(self, chat_html):
        assert "conv_" in chat_html

    def test_mobile_sidebar_backdrop(self, chat_html):
        assert "sidebarBackdrop" in chat_html

    def test_sidebar_collapsed_by_default(self, chat_html):
        # Sidebar hidden by CSS default (no 'open' class in markup)
        assert 'class="conv-sidebar"' in chat_html


# -- Cost display in HTML --

class TestCostDisplayHTML:
    """F-030: Token cost display elements in chat_ui.html."""

    @pytest.fixture
    def chat_html(self):
        return (Path(__file__).parent.parent / "bot" / "chat_ui.html").read_text()

    def test_cost_debug_element(self, chat_html):
        assert "debugCost" in chat_html

    def test_session_cost_element(self, chat_html):
        assert "debugSessionCost" in chat_html

    def test_token_prices_defined(self, chat_html):
        assert "TOKEN_PRICES" in chat_html

    def test_calculate_cost_function(self, chat_html):
        assert "calculateCost" in chat_html

    def test_format_cost_function(self, chat_html):
        assert "formatCost" in chat_html

    def test_free_label_for_ollama(self, chat_html):
        assert "'free'" in chat_html

    def test_provider_label_in_header(self, chat_html):
        assert "provider_label" in chat_html


# -- Gateway response structure --

class TestGatewayResponse:
    def test_gateway_response_has_token_fields(self):
        resp = GatewayResponse(text="hello", input_tokens=100, output_tokens=50, duration_ms=200)
        assert resp.input_tokens == 100
        assert resp.output_tokens == 50

    def test_gateway_response_defaults(self):
        resp = GatewayResponse(text="hello")
        assert resp.input_tokens == 0
        assert resp.output_tokens == 0
        assert resp.duration_ms == 0
        assert resp.tools_called == []
        assert resp.principles == []
