"""Tests for multi-provider LLM support."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.llm import (
    LLM_PROVIDERS,
    LLMResponse,
    ToolCall,
    OllamaClient,
    OpenAICompatibleClient,
    AnthropicClient,
    get_client,
    _openai_tools_to_anthropic,
    TOOL_DEFINITIONS,
)


# -- LLM_PROVIDERS dict --

class TestLLMProviders:
    def test_has_six_providers(self):
        assert len(LLM_PROVIDERS) == 6

    def test_provider_keys(self):
        expected = {"qwen-3.5", "ollama-other", "claude-haiku", "claude-sonnet", "claude-opus", "chatgpt"}
        assert set(LLM_PROVIDERS.keys()) == expected

    def test_each_provider_has_required_fields(self):
        required = {"label", "default_base_url", "default_model", "api_format", "needs_key", "model_choices"}
        for pid, pinfo in LLM_PROVIDERS.items():
            assert required.issubset(set(pinfo.keys())), f"{pid} missing fields"

    def test_api_format_values(self):
        for pid, pinfo in LLM_PROVIDERS.items():
            assert pinfo["api_format"] in ("openai", "anthropic"), f"{pid} has invalid api_format"

    def test_ollama_providers_no_key(self):
        assert LLM_PROVIDERS["qwen-3.5"]["needs_key"] is False
        assert LLM_PROVIDERS["ollama-other"]["needs_key"] is False

    def test_cloud_providers_need_key(self):
        for pid in ("claude-haiku", "claude-sonnet", "claude-opus", "chatgpt"):
            assert LLM_PROVIDERS[pid]["needs_key"] is True

    def test_anthropic_format_for_claude(self):
        for pid in ("claude-haiku", "claude-sonnet", "claude-opus"):
            assert LLM_PROVIDERS[pid]["api_format"] == "anthropic"

    def test_openai_format_for_chatgpt(self):
        assert LLM_PROVIDERS["chatgpt"]["api_format"] == "openai"

    def test_model_choices_not_empty(self):
        for pid, pinfo in LLM_PROVIDERS.items():
            assert len(pinfo["model_choices"]) >= 1


# -- get_client factory --

class TestGetClient:
    def test_qwen_returns_openai_compatible(self):
        client = get_client("qwen-3.5")
        assert isinstance(client, OpenAICompatibleClient)
        client.close()

    def test_chatgpt_returns_openai_compatible(self):
        client = get_client("chatgpt", api_key="fake-key")
        assert isinstance(client, OpenAICompatibleClient)
        client.close()

    def test_claude_sonnet_returns_anthropic(self):
        client = get_client("claude-sonnet", api_key="fake-key")
        assert isinstance(client, AnthropicClient)
        client.close()

    def test_claude_haiku_returns_anthropic(self):
        client = get_client("claude-haiku", api_key="fake-key")
        assert isinstance(client, AnthropicClient)
        client.close()

    def test_claude_opus_returns_anthropic(self):
        client = get_client("claude-opus", api_key="fake-key")
        assert isinstance(client, AnthropicClient)
        client.close()

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_client("nonexistent-provider")

    def test_custom_model_override(self):
        client = get_client("qwen-3.5", model="custom:latest")
        assert client.model == "custom:latest"
        client.close()

    def test_custom_base_url_override(self):
        client = get_client("qwen-3.5", base_url="http://custom:9999/v1")
        assert client.base_url == "http://custom:9999/v1"
        client.close()


# -- OpenAICompatibleClient --

class TestOpenAICompatibleClient:
    def test_init_defaults(self):
        client = OpenAICompatibleClient()
        assert client.model == "qwen3.5:latest"
        assert client.base_url == "http://localhost:11434/v1"
        client.close()

    def test_init_custom(self):
        client = OpenAICompatibleClient(
            model="gpt-5.4",
            base_url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert client.model == "gpt-5.4"
        assert client.base_url == "https://api.openai.com/v1"
        client.close()


# -- AnthropicClient --

class TestAnthropicClient:
    def test_init(self):
        client = AnthropicClient(model="claude-sonnet-4-6", api_key="sk-test")
        assert client.model == "claude-sonnet-4-6"
        client.close()


# -- Tool format conversion --

class TestToolFormatConversion:
    def test_openai_to_anthropic_conversion(self):
        result = _openai_tools_to_anthropic(TOOL_DEFINITIONS)
        assert len(result) == len(TOOL_DEFINITIONS)
        for tool in result:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_conversion_preserves_names(self):
        result = _openai_tools_to_anthropic(TOOL_DEFINITIONS)
        names = {t["name"] for t in result}
        expected_names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
        assert names == expected_names


# -- LLM config persistence --

class TestLLMConfig:
    def test_load_provider_config_defaults(self, tmp_path):
        from bot.llm_config import load_provider_config
        cfg = load_provider_config("qwen-3.5", path=tmp_path / "llm.json")
        assert cfg["base_url"] == "http://localhost:11434/v1"
        assert cfg["model"] == "qwen3.5:latest"

    def test_save_and_load_provider_config(self, tmp_path):
        from bot.llm_config import save_provider_config, load_provider_config
        config_path = tmp_path / "llm.json"
        save_provider_config("chatgpt", {
            "base_url": "https://custom.openai.com/v1",
            "model": "gpt-4o",
            "api_key": "sk-test123",
        }, path=config_path)
        loaded = load_provider_config("chatgpt", path=config_path)
        assert loaded["base_url"] == "https://custom.openai.com/v1"
        assert loaded["model"] == "gpt-4o"
        assert loaded["api_key"] == "sk-test123"

    def test_get_set_active_provider(self, tmp_path):
        from bot.llm_config import get_active_provider, set_active_provider
        config_path = tmp_path / "llm.json"
        assert get_active_provider(config_path) == "qwen-3.5"
        set_active_provider("claude-sonnet", config_path)
        assert get_active_provider(config_path) == "claude-sonnet"

    def test_api_key_from_env_fallback(self, tmp_path):
        from bot.llm_config import load_provider_config
        config_path = tmp_path / "llm.json"
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key-123"}):
            cfg = load_provider_config("claude-sonnet", path=config_path)
            assert cfg["api_key"] == "env-key-123"

    def test_saved_key_overrides_env(self, tmp_path):
        from bot.llm_config import save_provider_config, load_provider_config
        config_path = tmp_path / "llm.json"
        save_provider_config("claude-sonnet", {"api_key": "saved-key"}, path=config_path)
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            cfg = load_provider_config("claude-sonnet", path=config_path)
            assert cfg["api_key"] == "saved-key"


# -- Gateway provider switching --

class TestGatewayProviderSwitch:
    def test_gateway_has_switch_provider(self):
        from bot.gateway import Gateway
        assert hasattr(Gateway, "switch_provider")

    def test_gateway_health_includes_provider(self):
        from bot.gateway import Gateway
        gw = Gateway()
        health = gw.health_check()
        assert "provider" in health


# -- Server LLM endpoints --

class TestServerLLMEndpoints:
    def test_handler_has_llm_providers_method(self):
        from bot.server import BotHTTPHandler
        assert hasattr(BotHTTPHandler, "_handle_get_llm_providers")

    def test_handler_has_llm_switch_method(self):
        from bot.server import BotHTTPHandler
        assert hasattr(BotHTTPHandler, "_handle_llm_switch")

    def test_handler_has_llm_config_get_method(self):
        from bot.server import BotHTTPHandler
        assert hasattr(BotHTTPHandler, "_handle_get_llm_config")

    def test_handler_has_llm_config_post_method(self):
        from bot.server import BotHTTPHandler
        assert hasattr(BotHTTPHandler, "_handle_post_llm_config")


# -- Chat UI --

class TestChatUIProviders:
    def test_chat_ui_has_provider_cards(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "providerCards" in content
        assert "provider-card" in content

    def test_chat_ui_has_api_key_field(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "settingsApiKey" in content

    def test_chat_ui_has_test_connection(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "testConnection" in content

    def test_chat_ui_has_base_url_field(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "settingsBaseUrl" in content

    def test_chat_ui_fetches_llm_providers(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "/api/llm/providers" in content

    def test_chat_ui_has_model_selector(self):
        from bot.server import CHAT_UI_PATH
        content = CHAT_UI_PATH.read_text()
        assert "settingsModel" in content
        assert "model_choices" in content
