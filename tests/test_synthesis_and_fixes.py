"""Tests for Sprint 13: server direct-run, save_discovery API, auto-synthesis."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse, SYNTHESIS_THRESHOLD, SYNTHESIS_PROMPT_SUFFIX
from bot.server import BotHTTPHandler, create_app
from bot.llm import LLMResponse


# ─── Fixtures ────────────────────────────────────────────────────────────────


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


# ─── Task 1: Server Direct-Run Import Fix (B-017) ───────────────────────────


class TestServerDirectRun:
    """Tests that python3 bot/server.py bootstrap works."""

    def test_server_module_imports_gateway(self) -> None:
        """server.py successfully imports Gateway via relative import."""
        from bot.server import Gateway as ServerGateway
        from bot.gateway import Gateway as DirectGateway
        assert ServerGateway is DirectGateway

    def test_server_has_main_function(self) -> None:
        """server.py exposes a main() entry point."""
        from bot.server import main
        assert callable(main)

    def test_server_bootstrap_sets_package(self) -> None:
        """The bootstrap guard in server.py sets __package__ correctly."""
        import bot.server
        assert bot.server.__package__ == "bot"

    def test_server_imports_personality_loader(self) -> None:
        """server.py imports PersonalityLoader without errors."""
        from bot.server import PersonalityLoader
        assert PersonalityLoader is not None

    def test_create_app_works(self, gateway) -> None:
        """create_app() returns a working server instance."""
        app = create_app(gateway, port=0)
        try:
            assert app is not None
            assert BotHTTPHandler.gateway is gateway
        finally:
            app.server_close()

    def test_server_module_level_imports(self) -> None:
        """All top-level imports in server.py resolve correctly."""
        import importlib
        mod = importlib.import_module("bot.server")
        assert hasattr(mod, "Gateway")
        assert hasattr(mod, "PersonalityLoader")
        assert hasattr(mod, "BotHTTPHandler")
        assert hasattr(mod, "create_app")
        assert hasattr(mod, "start_server")


# ─── Task 2: Save Discovery API Endpoint (F-033) ────────────────────────────


class TestSaveDiscoveryEndpoint:
    """Tests for POST /api/tools/save_discovery."""

    def test_handler_has_save_discovery_method(self) -> None:
        """BotHTTPHandler has the _handle_save_discovery method."""
        assert hasattr(BotHTTPHandler, "_handle_save_discovery")

    def test_save_discovery_with_conversation(self, gateway, tmp_path) -> None:
        """save_discovery writes a seed doc from conversation history."""
        # Add some conversation history
        gateway.memory.add("test-save", "user", "I have a problem with X")
        gateway.memory.add("test-save", "assistant", "Tell me more about X")
        gateway.memory.add("test-save", "user", "It affects our customers")

        # Create a project directory structure
        project_dir = tmp_path / "test-project"
        seed_dir = project_dir / "docs" / "seed"
        seed_dir.mkdir(parents=True)

        with patch("bot.tools._resolve_project_root", return_value=project_dir):
            from bot.tools import tool_save_discovery
            result = tool_save_discovery(slug="test-project", content="test content")

        assert "saved to" in result.lower() or "Discovery" in result
        seed_files = list(seed_dir.glob("discovery-*.md"))
        assert len(seed_files) == 1

    def test_save_discovery_formats_conversation(self, gateway) -> None:
        """Conversation history is formatted into a discovery doc."""
        gateway.memory.add("conv-fmt", "user", "Problem statement")
        gateway.memory.add("conv-fmt", "assistant", "Response text")

        history = gateway.memory.get_history("conv-fmt")
        lines = ["# Discovery Notes\n"]
        for msg in history:
            role = msg["role"].title()
            lines.append(f"**{role}:** {msg['content']}\n")
        content = "\n".join(lines)

        assert "**User:** Problem statement" in content
        assert "**Assistant:** Response text" in content
        assert "# Discovery Notes" in content

    def test_save_discovery_no_conversation(self, gateway) -> None:
        """Returns empty history for nonexistent conversation."""
        history = gateway.memory.get_history("nonexistent-conv")
        assert history == []

    def test_save_discovery_project_not_found(self) -> None:
        """tool_save_discovery returns error for unknown project."""
        from bot.tools import tool_save_discovery
        with patch("bot.tools._resolve_project_root", return_value=None):
            result = tool_save_discovery(slug="nonexistent", content="test")
        assert "not found" in result.lower()

    def test_save_discovery_creates_seed_dir(self, tmp_path) -> None:
        """tool_save_discovery creates docs/seed/ if it doesn't exist."""
        project_dir = tmp_path / "new-project"
        project_dir.mkdir()
        # seed dir does NOT exist yet

        with patch("bot.tools._resolve_project_root", return_value=project_dir):
            from bot.tools import tool_save_discovery
            result = tool_save_discovery(slug="new-project", content="discovery content")

        seed_dir = project_dir / "docs" / "seed"
        assert seed_dir.exists()
        seed_files = list(seed_dir.glob("discovery-*.md"))
        assert len(seed_files) == 1
        assert seed_files[0].read_text() == "discovery content"

    def test_do_post_routes_save_discovery(self) -> None:
        """POST routing includes /api/tools/save_discovery."""
        import inspect
        source = inspect.getsource(BotHTTPHandler.do_POST)
        assert "/api/tools/save_discovery" in source


# ─── Task 3: Auto-Synthesis After 5+ Exchanges (F-034) ──────────────────────


class TestAutoSynthesis:
    """Tests for auto-synthesis after 5+ exchanges."""

    def test_gateway_has_exchange_counts(self, gateway) -> None:
        """Gateway tracks exchange counts per conversation."""
        assert hasattr(gateway, "_exchange_counts")
        assert isinstance(gateway._exchange_counts, dict)

    def test_gateway_has_synthesis_triggered(self, gateway) -> None:
        """Gateway tracks synthesis triggered flag per conversation."""
        assert hasattr(gateway, "_synthesis_triggered")
        assert isinstance(gateway._synthesis_triggered, dict)

    def test_exchange_count_increments(self, gateway) -> None:
        """Each user message increments the exchange count."""
        gateway.process_message("count-test", "msg 1")
        assert gateway._exchange_counts["count-test"] == 1
        gateway.process_message("count-test", "msg 2")
        assert gateway._exchange_counts["count-test"] == 2

    def test_exchange_counts_per_conversation(self, gateway) -> None:
        """Exchange counts are tracked separately per conversation."""
        gateway.process_message("conv-a", "hello")
        gateway.process_message("conv-b", "hello")
        gateway.process_message("conv-a", "again")
        assert gateway._exchange_counts["conv-a"] == 2
        assert gateway._exchange_counts["conv-b"] == 1

    def test_synthesis_not_triggered_before_threshold(self, gateway) -> None:
        """Synthesis is not triggered before SYNTHESIS_THRESHOLD messages."""
        for i in range(SYNTHESIS_THRESHOLD - 1):
            gateway.process_message("early-test", f"msg {i+1}")
        assert not gateway._synthesis_triggered.get("early-test", False)

    def test_synthesis_triggered_at_threshold(self, gateway) -> None:
        """Synthesis triggers on the SYNTHESIS_THRESHOLD-th message."""
        for i in range(SYNTHESIS_THRESHOLD):
            gateway.process_message("threshold-test", f"msg {i+1}")
        assert gateway._synthesis_triggered.get("threshold-test", False)

    def test_synthesis_prompt_appended(self, gateway) -> None:
        """System prompt includes synthesis suffix at threshold."""
        # Send messages up to threshold - 1
        for i in range(SYNTHESIS_THRESHOLD - 1):
            gateway.process_message("prompt-test", f"msg {i+1}")

        # Capture the system prompt used on the threshold call
        captured_prompts = []
        original_chat = gateway.llm.chat

        def capturing_chat(messages, system_prompt=None, tools=None):
            captured_prompts.append(system_prompt)
            return LLMResponse(content="synthesis response", duration_ms=10)

        with patch.object(gateway.llm, "chat", side_effect=capturing_chat):
            gateway.process_message("prompt-test", f"msg {SYNTHESIS_THRESHOLD}")

        assert len(captured_prompts) == 1
        assert SYNTHESIS_PROMPT_SUFFIX in captured_prompts[0]

    def test_synthesis_not_re_triggered(self, gateway) -> None:
        """Synthesis prompt is only appended once per conversation."""
        captured_prompts = []

        def capturing_chat(messages, system_prompt=None, tools=None):
            captured_prompts.append(system_prompt)
            return LLMResponse(content="response", duration_ms=10)

        with patch.object(gateway.llm, "chat", side_effect=capturing_chat):
            for i in range(SYNTHESIS_THRESHOLD + 2):
                gateway.process_message("once-test", f"msg {i+1}")

        # Only the threshold message should have the synthesis suffix
        synthesis_count = sum(1 for p in captured_prompts if SYNTHESIS_PROMPT_SUFFIX in p)
        assert synthesis_count == 1

    def test_normal_prompt_before_threshold(self, gateway) -> None:
        """System prompt is unmodified before threshold."""
        captured_prompts = []

        def capturing_chat(messages, system_prompt=None, tools=None):
            captured_prompts.append(system_prompt)
            return LLMResponse(content="response", duration_ms=10)

        with patch.object(gateway.llm, "chat", side_effect=capturing_chat):
            gateway.process_message("normal-test", "msg 1")

        assert SYNTHESIS_PROMPT_SUFFIX not in captured_prompts[0]
        assert captured_prompts[0] == gateway.system_prompt

    def test_synthesis_threshold_constant(self) -> None:
        """SYNTHESIS_THRESHOLD is 5."""
        assert SYNTHESIS_THRESHOLD == 5

    def test_get_system_prompt_helper(self, gateway) -> None:
        """_get_system_prompt returns modified prompt at threshold."""
        gateway._exchange_counts["helper-test"] = SYNTHESIS_THRESHOLD
        prompt = gateway._get_system_prompt("helper-test")
        assert SYNTHESIS_PROMPT_SUFFIX in prompt

        # After triggering, should return normal prompt
        prompt2 = gateway._get_system_prompt("helper-test")
        assert SYNTHESIS_PROMPT_SUFFIX not in prompt2

    def test_get_system_prompt_below_threshold(self, gateway) -> None:
        """_get_system_prompt returns normal prompt below threshold."""
        gateway._exchange_counts["below-test"] = 3
        prompt = gateway._get_system_prompt("below-test")
        assert prompt == gateway.system_prompt
