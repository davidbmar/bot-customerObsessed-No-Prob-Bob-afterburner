"""Tests for SSE streaming endpoint and gateway streaming support."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, OllamaClient
from bot.server import BotHTTPHandler, _classify_llm_error


# -- Gateway process_message_stream --


class TestGatewayStreamMethod:
    """Tests for Gateway.process_message_stream()."""

    @pytest.fixture
    def personalities_dir(self) -> Path:
        return Path(__file__).parent.parent / "personalities"

    @pytest.fixture
    def mock_llm_chat(self):
        def fake_chat(messages, system_prompt=None, tools=None):
            return LLMResponse(content="Mock response", duration_ms=10)

        with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
            yield

    @pytest.fixture
    def gateway(self, personalities_dir, mock_llm_chat) -> Gateway:
        return Gateway(
            personality_name="customer-discovery",
            model="test-model",
            ollama_url="http://localhost:11434",
            personalities_dir=str(personalities_dir),
        )

    def test_gateway_has_stream_method(self) -> None:
        assert hasattr(Gateway, "process_message_stream")

    def test_stream_yields_token_chunks(self, gateway) -> None:
        """Streaming with chat_stream yields token dicts."""
        def fake_stream(messages, system_prompt=None, tools=None):
            yield "Hello "
            yield "world"
            return LLMResponse(content="Hello world", duration_ms=50)

        with patch.object(gateway.llm, "chat_stream", side_effect=fake_stream):
            gen = gateway.process_message_stream("test-conv", "Hi")
            chunks = []
            result = None
            try:
                while True:
                    chunks.append(next(gen))
            except StopIteration as e:
                result = e.value

            assert len(chunks) == 2
            assert chunks[0] == {"type": "token", "content": "Hello "}
            assert chunks[1] == {"type": "token", "content": "world"}
            assert isinstance(result, GatewayResponse)
            assert result.text == "Hello world"
            assert result.duration_ms == 50

    def test_stream_fallback_no_chat_stream(self, gateway) -> None:
        """If LLM client has no chat_stream, falls back to non-streaming."""
        # Use a mock LLM without chat_stream (don't modify OllamaClient class)
        mock_llm = MagicMock(spec=[])  # empty spec = no attributes
        mock_llm.chat = MagicMock(return_value=LLMResponse(content="Fallback response", duration_ms=5))
        mock_llm.model = "test"
        gateway.llm = mock_llm

        gen = gateway.process_message_stream("test-conv", "Hi")
        chunks = []
        result = None
        try:
            while True:
                chunks.append(next(gen))
        except StopIteration as e:
            result = e.value

        assert len(chunks) == 1
        assert chunks[0]["content"] == "Fallback response"
        assert isinstance(result, GatewayResponse)

    def test_stream_saves_to_memory(self, gateway) -> None:
        """Streaming saves messages to conversation memory."""
        def fake_stream(messages, system_prompt=None, tools=None):
            yield "Hi back"
            return LLMResponse(content="Hi back", duration_ms=10)

        with patch.object(gateway.llm, "chat_stream", side_effect=fake_stream):
            gen = gateway.process_message_stream("test-mem", "Hello")
            try:
                while True:
                    next(gen)
            except StopIteration:
                pass

        history = gateway.memory.get_history("test-mem")
        roles = [m["role"] for m in history]
        assert "user" in roles
        assert "assistant" in roles

    def test_stream_returns_principles(self, gateway) -> None:
        """GatewayResponse includes personality principles."""
        def fake_stream(messages, system_prompt=None, tools=None):
            yield "test"
            return LLMResponse(content="test", duration_ms=5)

        with patch.object(gateway.llm, "chat_stream", side_effect=fake_stream):
            gen = gateway.process_message_stream("test-pr", "Hi")
            result = None
            try:
                while True:
                    next(gen)
            except StopIteration as e:
                result = e.value

            assert len(result.principles) > 0

    def test_stream_returns_memory_count(self, gateway) -> None:
        """GatewayResponse includes memory count."""
        def fake_stream(messages, system_prompt=None, tools=None):
            yield "ok"
            return LLMResponse(content="ok", duration_ms=5)

        with patch.object(gateway.llm, "chat_stream", side_effect=fake_stream):
            gen = gateway.process_message_stream("test-mc", "Hi")
            result = None
            try:
                while True:
                    next(gen)
            except StopIteration as e:
                result = e.value

            assert result.memory_count >= 2  # user + assistant

    def test_stream_returns_token_counts(self, gateway) -> None:
        """GatewayResponse includes token counts from the LLM response."""
        def fake_stream(messages, system_prompt=None, tools=None):
            yield "ok"
            return LLMResponse(content="ok", duration_ms=5, input_tokens=100, output_tokens=50)

        with patch.object(gateway.llm, "chat_stream", side_effect=fake_stream):
            gen = gateway.process_message_stream("test-tok", "Hi")
            result = None
            try:
                while True:
                    next(gen)
            except StopIteration as e:
                result = e.value

            assert result.input_tokens == 100
            assert result.output_tokens == 50


# -- SSE endpoint in server --


class TestSSEEndpoint:
    """Tests for POST /api/chat/stream endpoint."""

    def test_handler_has_stream_method(self) -> None:
        assert hasattr(BotHTTPHandler, "_handle_chat_stream")

    def test_server_routes_stream_endpoint(self) -> None:
        """POST /api/chat/stream is routed in do_POST."""
        import inspect
        source = inspect.getsource(BotHTTPHandler.do_POST)
        assert "/api/chat/stream" in source


# -- Error classification --


class TestErrorClassification:
    """Tests for _classify_llm_error helper."""

    def test_connection_error_returns_503(self) -> None:
        status, data = _classify_llm_error(ConnectionError("refused"))
        assert status == 503
        assert data["error"] == "LLM unreachable"

    def test_httpx_connect_error_returns_503(self) -> None:
        import httpx
        exc = httpx.ConnectError("Connection refused")
        status, data = _classify_llm_error(exc)
        assert status == 503
        assert data["error"] == "LLM unreachable"

    def test_httpx_timeout_returns_503(self) -> None:
        import httpx
        exc = httpx.TimeoutException("timed out")
        status, data = _classify_llm_error(exc)
        assert status == 503
        assert data["error"] == "LLM unreachable"

    def test_anthropic_auth_error_returns_401(self) -> None:
        try:
            import anthropic
            exc = anthropic.AuthenticationError(
                message="Invalid API Key",
                response=MagicMock(status_code=401, headers={}),
                body={"error": {"message": "Invalid API Key"}},
            )
            status, data = _classify_llm_error(exc)
            assert status == 401
            assert data["error"] == "Invalid API key"
        except ImportError:
            pytest.skip("anthropic not installed")

    def test_generic_error_returns_500(self) -> None:
        status, data = _classify_llm_error(RuntimeError("something broke"))
        assert status == 500
        assert "something broke" in data["error"]

    def test_error_includes_detail(self) -> None:
        status, data = _classify_llm_error(ConnectionError("host unreachable"))
        assert "detail" in data
        assert "host unreachable" in data["detail"]


# -- Chat UI tests --


class TestChatUIStreaming:
    """Tests for streaming-related elements in chat_ui.html."""

    @pytest.fixture
    def chat_ui_content(self) -> str:
        from bot.server import CHAT_UI_PATH
        return CHAT_UI_PATH.read_text()

    def test_chat_ui_has_stream_endpoint(self, chat_ui_content) -> None:
        assert "/api/chat/stream" in chat_ui_content

    def test_chat_ui_has_streaming_label(self, chat_ui_content) -> None:
        assert "Streaming..." in chat_ui_content

    def test_chat_ui_has_error_class(self, chat_ui_content) -> None:
        assert "message error" in chat_ui_content or "message.error" in chat_ui_content

    def test_chat_ui_has_retry_button(self, chat_ui_content) -> None:
        assert "btn-retry" in chat_ui_content
        assert "Retry" in chat_ui_content

    def test_chat_ui_has_save_conversation(self, chat_ui_content) -> None:
        assert "saveConversation" in chat_ui_content

    def test_chat_ui_has_restore_conversation(self, chat_ui_content) -> None:
        assert "restoreConversation" in chat_ui_content

    def test_chat_ui_has_localstorage_usage(self, chat_ui_content) -> None:
        assert "localStorage" in chat_ui_content

    def test_chat_ui_has_clear_storage(self, chat_ui_content) -> None:
        assert "clearConversationStorage" in chat_ui_content

    def test_chat_ui_new_chat_clears_storage(self, chat_ui_content) -> None:
        assert "clearConversationStorage" in chat_ui_content

    def test_chat_ui_has_stream_reader(self, chat_ui_content) -> None:
        assert "getReader" in chat_ui_content

    def test_chat_ui_has_text_decoder(self, chat_ui_content) -> None:
        assert "TextDecoder" in chat_ui_content
