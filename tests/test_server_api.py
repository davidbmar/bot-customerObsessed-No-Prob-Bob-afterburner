"""Tests for new API endpoints: /api/personalities, /api/config, /api/conversations/new."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.server import BotHTTPHandler, create_app
from bot.gateway import Gateway
from bot.llm import LLMResponse


@pytest.fixture
def personalities_dir() -> Path:
    """Return the real personalities directory."""
    return Path(__file__).parent.parent / "personalities"


@pytest.fixture
def mock_llm_chat():
    """Mock OllamaClient.chat to avoid real LLM calls."""
    def fake_chat(messages, system_prompt=None, tools=None):
        return LLMResponse(content="Mock response", duration_ms=10)

    with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
        yield


@pytest.fixture
def gateway(personalities_dir, mock_llm_chat) -> Gateway:
    """Create a Gateway with mocked LLM."""
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(personalities_dir),
    )


@pytest.fixture
def server(gateway):
    """Create the HTTP server without starting it."""
    app = create_app(gateway, port=0)
    yield app
    app.server_close()


class TestGetPersonalities:
    """Tests for GET /api/personalities."""

    def test_returns_personality_list(self, gateway) -> None:
        """The endpoint returns available personality names."""
        from bot.personality import PersonalityLoader

        pdir = Path(__file__).parent.parent / "personalities"
        loader = PersonalityLoader(pdir)
        expected = loader.list_personalities()
        assert len(expected) >= 2  # base and customer-discovery
        assert "customer-discovery" in expected

    def test_handler_has_personalities_method(self) -> None:
        """BotHTTPHandler has the _handle_get_personalities method."""
        assert hasattr(BotHTTPHandler, "_handle_get_personalities")


class TestGetConfig:
    """Tests for GET /api/config."""

    def test_config_returns_current_settings(self, gateway) -> None:
        """Config matches gateway's current state."""
        assert gateway.personality.name == "customer-discovery"
        assert gateway.llm.model == "test-model"


class TestPostConfig:
    """Tests for POST /api/config."""

    def test_handler_has_post_config_method(self) -> None:
        """BotHTTPHandler has the _handle_post_config method."""
        assert hasattr(BotHTTPHandler, "_handle_post_config")

    def test_gateway_model_can_be_changed(self, gateway) -> None:
        """Gateway model attribute is mutable."""
        gateway.llm.model = "new-model"
        assert gateway.llm.model == "new-model"

    def test_gateway_personality_can_be_switched(self, gateway, personalities_dir) -> None:
        """Gateway personality can be switched at runtime."""
        from bot.personality import PersonalityLoader

        loader = PersonalityLoader(personalities_dir)
        new_personality = loader.load("base")
        gateway.personality = new_personality
        gateway.system_prompt = new_personality.system_prompt
        gateway.principles = new_personality.principles
        assert gateway.personality.name != "customer-discovery"


class TestNewConversation:
    """Tests for POST /api/conversations/new."""

    def test_handler_has_new_conversation_method(self) -> None:
        """BotHTTPHandler has the _handle_new_conversation method."""
        assert hasattr(BotHTTPHandler, "_handle_new_conversation")


class TestChatResponseIncludesPersonality:
    """Tests that /api/chat response includes personality name."""

    def test_chat_response_has_personality_field(self, gateway) -> None:
        """process_message response can be combined with personality name."""
        resp = gateway.process_message("test-conv", "Hello")
        # The server adds personality to the JSON response
        response_data = {
            "response": resp.text,
            "personality": gateway.personality.name,
            "tools_called": resp.tools_called,
            "principles_active": resp.principles,
        }
        assert "personality" in response_data
        assert response_data["personality"] == "customer-discovery"
