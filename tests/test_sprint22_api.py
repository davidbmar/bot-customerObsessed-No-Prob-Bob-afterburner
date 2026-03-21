"""Tests for Sprint 22 API endpoints: /api/projects, /api/health, /api/conversations/new."""

from __future__ import annotations

import http.client
import json
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.config import BotConfig
from bot.server import create_app
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
def config_with_projects(tmp_path) -> BotConfig:
    """BotConfig with a known project registered."""
    cfg = BotConfig(
        projects={"noprobbob": str(tmp_path)},
        active_project="noprobbob",
    )
    return cfg


@pytest.fixture
def gateway(personalities_dir, mock_llm_chat, config_with_projects) -> Gateway:
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(personalities_dir),
        config=config_with_projects,
    )


@pytest.fixture
def gateway_no_config(personalities_dir, mock_llm_chat) -> Gateway:
    """Gateway without a config (simulates missing config)."""
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(personalities_dir),
    )


@pytest.fixture
def live_server(gateway):
    app = create_app(gateway, port=0)
    _, port = app.server_address
    thread = threading.Thread(target=app.serve_forever, daemon=True)
    thread.start()
    yield port
    app.shutdown()
    app.server_close()


@pytest.fixture
def live_server_no_config(gateway_no_config):
    app = create_app(gateway_no_config, port=0)
    _, port = app.server_address
    thread = threading.Thread(target=app.serve_forever, daemon=True)
    thread.start()
    yield port
    app.shutdown()
    app.server_close()


class TestGetProjects:
    """Tests for GET /api/projects."""

    def test_returns_projects_list(self, live_server) -> None:
        """GET /api/projects returns JSON with at least one project object."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/projects")
        resp = conn.getresponse()
        assert resp.status == 200
        data = json.loads(resp.read())
        assert "projects" in data
        assert len(data["projects"]) >= 1
        proj = data["projects"][0]
        assert "slug" in proj
        assert "name" in proj
        assert proj["slug"] == "noprobbob"

    def test_returns_active_project(self, live_server) -> None:
        """GET /api/projects includes the active_project field."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/projects")
        resp = conn.getresponse()
        data = json.loads(resp.read())
        assert data["active_project"] == "noprobbob"

    def test_no_config_returns_empty(self, live_server_no_config) -> None:
        """Without config, /api/projects returns empty list."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server_no_config)
        conn.request("GET", "/api/projects")
        resp = conn.getresponse()
        assert resp.status == 200
        data = json.loads(resp.read())
        assert data["projects"] == []


class TestGetHealth:
    """Tests for GET /api/health."""

    def test_health_returns_200(self, live_server) -> None:
        """GET /api/health returns 200 with expected fields."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/health")
        resp = conn.getresponse()
        assert resp.status == 200
        data = json.loads(resp.read())
        assert "status" in data

    def test_health_includes_model(self, live_server) -> None:
        """Health response includes model info."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/health")
        resp = conn.getresponse()
        data = json.loads(resp.read())
        assert "model" in data


class TestNewConversation:
    """Tests for POST /api/conversations/new."""

    def test_returns_conversation_id(self, live_server) -> None:
        """POST /api/conversations/new returns a valid conversation_id."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        body = json.dumps({})
        conn.request("POST", "/api/conversations/new", body=body,
                      headers={"Content-Type": "application/json",
                                "Content-Length": str(len(body))})
        resp = conn.getresponse()
        assert resp.status == 200
        data = json.loads(resp.read())
        assert "conversation_id" in data
        assert data["conversation_id"].startswith("web-")
        assert len(data["conversation_id"]) > 4

    def test_each_call_returns_unique_id(self, live_server) -> None:
        """Each call to /api/conversations/new returns a different ID."""
        ids = []
        for _ in range(3):
            conn = http.client.HTTPConnection("127.0.0.1", live_server)
            body = json.dumps({})
            conn.request("POST", "/api/conversations/new", body=body,
                          headers={"Content-Type": "application/json",
                                    "Content-Length": str(len(body))})
            resp = conn.getresponse()
            data = json.loads(resp.read())
            ids.append(data["conversation_id"])
        assert len(set(ids)) == 3
