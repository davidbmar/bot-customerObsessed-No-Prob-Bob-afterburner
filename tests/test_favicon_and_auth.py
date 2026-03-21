"""Tests for favicon serving and localhost auth bypass (F-056, F-057)."""

from __future__ import annotations

import http.client
import os
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.server import BotHTTPHandler, create_app, STATIC_DIR
from bot.gateway import Gateway
from bot.llm import LLMResponse


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


@pytest.fixture
def live_server(gateway):
    """Start a real HTTP server on a random port for integration tests."""
    app = create_app(gateway, port=0)
    _, port = app.server_address
    thread = threading.Thread(target=app.serve_forever, daemon=True)
    thread.start()
    yield port
    app.shutdown()
    app.server_close()


class TestFaviconServing:
    """Tests for favicon routes (F-056)."""

    def test_favicon_ico_returns_200(self, live_server) -> None:
        """GET /favicon.ico returns 200 with content."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/favicon.ico")
        resp = conn.getresponse()
        body = resp.read()
        assert resp.status == 200
        assert resp.getheader("Content-Type") == "image/x-icon"
        assert len(body) > 0
        conn.close()

    def test_favicon_svg_returns_200(self, live_server) -> None:
        """GET /favicon.svg returns 200 with SVG content."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/favicon.svg")
        resp = conn.getresponse()
        body = resp.read()
        assert resp.status == 200
        assert resp.getheader("Content-Type") == "image/svg+xml"
        assert b"<svg" in body
        conn.close()

    def test_chat_html_includes_favicon_link(self, live_server) -> None:
        """The chat page HTML includes <link rel="icon">."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/chat")
        resp = conn.getresponse()
        body = resp.read().decode()
        assert resp.status == 200
        assert '<link rel="icon"' in body
        conn.close()

    def test_static_dir_has_favicon_files(self) -> None:
        """The static directory contains both favicon files."""
        assert (STATIC_DIR / "favicon.ico").exists()
        assert (STATIC_DIR / "favicon.svg").exists()


class TestLocalhostAuthBypass:
    """Tests for localhost auth bypass (F-057)."""

    def test_no_client_id_injects_empty_string(self, live_server) -> None:
        """When GOOGLE_CLIENT_ID is unset, the HTML injects an empty string."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GOOGLE_CLIENT_ID", None)
            conn = http.client.HTTPConnection("127.0.0.1", live_server)
            conn.request("GET", "/chat")
            resp = conn.getresponse()
            body = resp.read().decode()
            assert 'window.__GOOGLE_CLIENT_ID__ = ""' in body
            conn.close()
