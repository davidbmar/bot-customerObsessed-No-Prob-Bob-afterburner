"""Tests for Sprint 23 — tool result formatting (B-033 guard), conversation endpoint, /api/stats."""

from __future__ import annotations

import http.client
import json
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, ToolCall, TOOL_DEFINITIONS
from bot.server import create_app


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


@pytest.fixture
def live_server(gateway):
    app = create_app(gateway, port=0)
    _, port = app.server_address
    thread = threading.Thread(target=app.serve_forever, daemon=True)
    thread.start()
    yield port
    app.shutdown()
    app.server_close()


# =============================================================================
# Task 1 — Tool result formatting regression guard (B-033)
# =============================================================================


class TestToolResultFormatting:
    """Verify _handle_tool_calls formats messages correctly for Anthropic vs OpenAI."""

    def test_tool_call_id_stored(self):
        """ToolCall.id is stored when set."""
        tc = ToolCall(name="save_discovery", arguments={"slug": "test"}, id="test-123")
        assert tc.id == "test-123"
        assert tc.name == "save_discovery"

    def test_tool_call_id_default_empty(self):
        """ToolCall.id defaults to empty string."""
        tc = ToolCall(name="save_discovery", arguments={})
        assert tc.id == ""

    def test_anthropic_format_with_id(self, gateway):
        """When ToolCall has id, messages use Anthropic format (tool_use + tool_result blocks)."""
        llm_resp = LLMResponse(
            content="Let me save that.",
            tool_calls=[
                ToolCall(name="save_discovery", arguments={"slug": "test", "content": "# Test"}, id="toolu_123"),
            ],
            duration_ms=50,
        )
        messages = [
            {"role": "user", "content": "Save my notes"},
        ]

        with patch("bot.tools._find_project_root", return_value=None):
            with patch("bot.llm.OllamaClient.chat", return_value=LLMResponse(content="Done!", duration_ms=10)):
                gateway._handle_tool_calls(llm_resp, messages)

        # After tool handling, messages should have Anthropic-format entries
        assistant_msg = messages[1]
        assert assistant_msg["role"] == "assistant"
        assert isinstance(assistant_msg["content"], list)

        # Check tool_use block
        tool_use_block = [b for b in assistant_msg["content"] if b.get("type") == "tool_use"]
        assert len(tool_use_block) == 1
        assert tool_use_block[0]["id"] == "toolu_123"
        assert tool_use_block[0]["name"] == "save_discovery"

        # Check text block is present
        text_blocks = [b for b in assistant_msg["content"] if b.get("type") == "text"]
        assert len(text_blocks) == 1
        assert text_blocks[0]["text"] == "Let me save that."

        # Check tool_result message
        result_msg = messages[2]
        assert result_msg["role"] == "user"
        assert isinstance(result_msg["content"], list)
        assert result_msg["content"][0]["type"] == "tool_result"
        assert result_msg["content"][0]["tool_use_id"] == "toolu_123"

    def test_openai_format_without_id(self, gateway):
        """When ToolCall has id='', messages use OpenAI format (role: tool)."""
        llm_resp = LLMResponse(
            content="Checking status.",
            tool_calls=[
                ToolCall(name="get_sprint_status", arguments={}, id=""),
            ],
            duration_ms=50,
        )
        messages = [
            {"role": "user", "content": "What's the sprint status?"},
        ]

        with patch("bot.tools._find_project_root", return_value=None):
            with patch("bot.llm.OllamaClient.chat", return_value=LLMResponse(content="Here's the status.", duration_ms=10)):
                gateway._handle_tool_calls(llm_resp, messages)

        # After tool handling, messages should have OpenAI-format entries
        assistant_msg = messages[1]
        assert assistant_msg["role"] == "assistant"
        assert isinstance(assistant_msg["content"], str)
        assert assistant_msg["content"] == "Checking status."

        tool_msg = messages[2]
        assert tool_msg["role"] == "tool"
        assert isinstance(tool_msg["content"], str)

    def test_anthropic_format_no_text_content(self, gateway):
        """When LLM returns tool_use with empty content, no text block is included."""
        llm_resp = LLMResponse(
            content="",
            tool_calls=[
                ToolCall(name="save_discovery", arguments={"slug": "t", "content": "x"}, id="toolu_456"),
            ],
            duration_ms=50,
        )
        messages = [{"role": "user", "content": "Save"}]

        with patch("bot.tools._find_project_root", return_value=None):
            with patch("bot.llm.OllamaClient.chat", return_value=LLMResponse(content="Saved!", duration_ms=10)):
                gateway._handle_tool_calls(llm_resp, messages)

        assistant_msg = messages[1]
        content_blocks = assistant_msg["content"]
        text_blocks = [b for b in content_blocks if b.get("type") == "text"]
        assert len(text_blocks) == 0  # No text block when content is empty
        tool_blocks = [b for b in content_blocks if b.get("type") == "tool_use"]
        assert len(tool_blocks) == 1


# =============================================================================
# Task 2 — Conversation new endpoint robustness
# =============================================================================


class TestConversationNewEndpointRobust:
    """POST /api/conversations/new returns unique IDs with expected format."""

    def test_multiple_calls_return_unique_ids(self, live_server) -> None:
        """Five calls to /api/conversations/new all return different IDs."""
        ids = set()
        for _ in range(5):
            conn = http.client.HTTPConnection("127.0.0.1", live_server)
            body = json.dumps({})
            conn.request(
                "POST", "/api/conversations/new", body=body,
                headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
            )
            resp = conn.getresponse()
            assert resp.status == 200
            data = json.loads(resp.read())
            ids.add(data["conversation_id"])
        assert len(ids) == 5

    def test_conversation_id_format(self, live_server) -> None:
        """Conversation IDs follow 'web-<12 hex chars>' format."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        body = json.dumps({})
        conn.request(
            "POST", "/api/conversations/new", body=body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        resp = conn.getresponse()
        data = json.loads(resp.read())
        cid = data["conversation_id"]
        assert cid.startswith("web-")
        hex_part = cid[4:]
        assert len(hex_part) == 12
        # Verify it's valid hex
        int(hex_part, 16)


# =============================================================================
# Task 3 — /api/stats endpoint
# =============================================================================


class TestStatsEndpoint:
    """Tests for GET /api/stats."""

    def test_stats_returns_200(self, live_server) -> None:
        """GET /api/stats returns 200 with expected keys."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/stats")
        resp = conn.getresponse()
        assert resp.status == 200
        data = json.loads(resp.read())
        assert "sprints" in data
        assert "tests" in data
        assert "features" in data

    def test_stats_values_are_ints(self, live_server) -> None:
        """Stats values are integers."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server)
        conn.request("GET", "/api/stats")
        resp = conn.getresponse()
        data = json.loads(resp.read())
        assert isinstance(data["sprints"], int)
        assert isinstance(data["tests"], int)
        assert isinstance(data["features"], int)

    def test_stats_sprint_count_matches_files(self) -> None:
        """Sprint count matches the number of PROJECT_STATUS_*.md files in docs/."""
        docs_dir = Path(__file__).parent.parent / "docs"
        expected = len(list(docs_dir.glob("PROJECT_STATUS_*.md")))
        from bot.server import _count_sprints
        assert _count_sprints() == expected

    def test_stats_feature_count_matches_backlog(self) -> None:
        """Feature count matches lines with '| F-' in backlog README."""
        from bot.server import _count_features
        count = _count_features()
        backlog_path = Path(__file__).parent.parent / "docs" / "project-memory" / "backlog" / "README.md"
        if backlog_path.exists():
            expected = sum(1 for line in backlog_path.read_text().splitlines() if "| F-" in line)
            assert count == expected
        else:
            assert count == 0
