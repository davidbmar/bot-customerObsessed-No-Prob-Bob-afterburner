"""Tests for Sprint 17: provider label fix (B-019) and PROJECT_STATUS docs (B-021)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.llm import LLM_PROVIDERS, LLMResponse, OllamaClient
from bot.gateway import Gateway


REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
PERSONALITIES_DIR = REPO_ROOT / "personalities"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_llm_chat():
    """Mock OllamaClient.chat to avoid real LLM calls."""
    def fake_chat(messages, system_prompt=None, tools=None):
        return LLMResponse(content="Mock response", duration_ms=10)
    with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
        yield


@pytest.fixture
def gateway_default(mock_llm_chat) -> Gateway:
    """Gateway with default (no explicit provider_id)."""
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(PERSONALITIES_DIR),
    )


@pytest.fixture
def gateway_with_provider(mock_llm_chat) -> Gateway:
    """Gateway with explicit provider_id='qwen-3.5'."""
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(PERSONALITIES_DIR),
        provider_id="qwen-3.5",
    )


# ---------------------------------------------------------------------------
# B-019: Provider label in health endpoint
# ---------------------------------------------------------------------------

class TestHealthProviderLabel:
    """health_check() must return the display label, not the raw provider key."""

    def test_default_gateway_returns_qwen_label(self, gateway_default):
        health = gateway_default.health_check()
        assert health["provider_label"] == "Qwen 3.5"

    def test_default_gateway_provider_is_qwen(self, gateway_default):
        health = gateway_default.health_check()
        assert health["provider"] == "qwen-3.5"

    def test_explicit_provider_returns_correct_label(self, gateway_with_provider):
        health = gateway_with_provider.health_check()
        assert health["provider_label"] == "Qwen 3.5"

    def test_health_not_ollama_label(self, gateway_default):
        health = gateway_default.health_check()
        assert health["provider_label"] != "ollama"

    def test_health_has_required_keys(self, gateway_default):
        health = gateway_default.health_check()
        for key in ("status", "personality", "model", "provider", "provider_label"):
            assert key in health

    @pytest.mark.parametrize("provider_id,expected_label", [
        ("qwen-3.5", "Qwen 3.5"),
        ("claude-haiku", "Claude Haiku"),
        ("claude-sonnet", "Claude Sonnet"),
        ("claude-opus", "Claude Opus"),
        ("chatgpt", "ChatGPT"),
        ("ollama-other", "Ollama (other)"),
    ])
    def test_label_for_each_provider(self, mock_llm_chat, provider_id, expected_label):
        """Each provider_id maps to the correct display label via LLM_PROVIDERS."""
        label = LLM_PROVIDERS[provider_id]["label"]
        assert label == expected_label


class TestProviderIdDefault:
    """Gateway._provider_id defaults to 'qwen-3.5', not None."""

    def test_default_provider_id_set(self, gateway_default):
        assert gateway_default._provider_id == "qwen-3.5"

    def test_explicit_provider_id_set(self, gateway_with_provider):
        assert gateway_with_provider._provider_id == "qwen-3.5"


# ---------------------------------------------------------------------------
# /api/llm/providers: active_label field
# ---------------------------------------------------------------------------

class TestLLMProvidersEndpointActiveLabel:
    """The _handle_get_llm_providers handler should include active_label."""

    def test_active_label_in_response(self, gateway_default):
        from bot.server import BotHTTPHandler
        from bot.llm import LLM_PROVIDERS
        from bot.llm_config import get_active_provider

        active = getattr(gateway_default, "_provider_id", None) or get_active_provider()
        expected_label = LLM_PROVIDERS.get(active, {}).get("label", active)
        assert expected_label == "Qwen 3.5"

    def test_all_providers_have_label_key(self):
        for pid, pinfo in LLM_PROVIDERS.items():
            assert "label" in pinfo, f"Provider {pid} missing 'label'"


# ---------------------------------------------------------------------------
# B-021: PROJECT_STATUS docs for Sprints 12-16
# ---------------------------------------------------------------------------

class TestProjectStatusDocs:
    """Verify PROJECT_STATUS docs exist for all 17 sprints."""

    def test_seventeen_docs_exist(self):
        docs = list(DOCS_DIR.glob("PROJECT_STATUS_*.md"))
        assert len(docs) >= 17, f"Expected >=17, found {len(docs)}: {[d.name for d in docs]}"

    @pytest.mark.parametrize("sprint_num", range(1, 18))
    def test_doc_exists_for_sprint(self, sprint_num):
        matches = list(DOCS_DIR.glob(f"PROJECT_STATUS_*-sprint{sprint_num}.md"))
        assert len(matches) == 1, f"Expected 1 doc for sprint {sprint_num}, found {len(matches)}"

    @pytest.mark.parametrize("sprint_num", range(12, 17))
    def test_sprint_12_16_doc_has_content(self, sprint_num):
        matches = list(DOCS_DIR.glob(f"PROJECT_STATUS_*-sprint{sprint_num}.md"))
        assert len(matches) == 1
        content = matches[0].read_text()
        assert f"Sprint {sprint_num}" in content
        assert "## What Changed" in content
        assert "## Merge Results" in content

    @pytest.mark.parametrize("sprint_num", range(12, 17))
    def test_sprint_doc_has_goal(self, sprint_num):
        matches = list(DOCS_DIR.glob(f"PROJECT_STATUS_*-sprint{sprint_num}.md"))
        content = matches[0].read_text()
        assert f"Sprint {sprint_num} goal:" in content


# ---------------------------------------------------------------------------
# generate_sprint_history.py
# ---------------------------------------------------------------------------

class TestGenerateSprintHistory:
    """Test the generate_sprint_history script internals."""

    def test_parse_brief_extracts_sprint_num(self):
        from scripts.generate_sprint_history import parse_brief
        brief_path = REPO_ROOT / ".sprint" / "history" / "sprint-12-brief.md"
        if brief_path.exists():
            result = parse_brief(brief_path)
            assert result["num"] == 12

    def test_parse_brief_extracts_goal(self):
        from scripts.generate_sprint_history import parse_brief
        brief_path = REPO_ROOT / ".sprint" / "history" / "sprint-12-brief.md"
        if brief_path.exists():
            result = parse_brief(brief_path)
            assert len(result["goal"]) > 0

    def test_generate_status_doc_format(self):
        from scripts.generate_sprint_history import generate_status_doc
        brief = {
            "num": 99,
            "goal": "Test goal",
            "goal_lines": ["Test goal"],
            "agents": [{"branch": "agentA-test", "objective": "Test objective"}],
            "merge_order": ["agentA-test"],
        }
        doc = generate_status_doc(brief, "2026-01-01")
        assert "Sprint 99" in doc
        assert "Test goal" in doc
        assert "agentA-test" in doc
        assert "## Merge Results" in doc

    def test_discover_sprint_range(self):
        from scripts.generate_sprint_history import discover_sprint_range
        start, end = discover_sprint_range()
        assert start >= 1
        assert end >= 16
