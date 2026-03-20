"""End-to-end test: conversation -> save_discovery -> seed doc on disk.

Exercises the full pipeline: Gateway processes messages (with mocked LLM),
then save_discovery writes a seed document to a temp project directory.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, ToolCall
from bot.tools import execute_tool, tool_save_discovery


@pytest.fixture
def personalities_dir() -> Path:
    """Return the real personalities directory."""
    return Path(__file__).parent.parent / "personalities"


@pytest.fixture
def mock_llm_chat():
    """Mock OllamaClient.chat to return canned responses without a real LLM."""
    responses = iter([
        LLMResponse(content="Hi! I'd love to learn about the problem you're solving.", duration_ms=50),
        LLMResponse(content="Interesting — so inventory tracking is painful for small businesses?", duration_ms=50),
        LLMResponse(content="Got it. Let me summarize what I've learned about your needs.", duration_ms=50),
    ])

    def fake_chat(messages, system_prompt=None, tools=None):
        try:
            return next(responses)
        except StopIteration:
            return LLMResponse(content="Thank you for sharing!", duration_ms=10)

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
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with docs/seed/."""
    project = tmp_path / "test-e2e-project"
    (project / "docs" / "seed").mkdir(parents=True)
    return project


class TestConversationToSeedDoc:
    """End-to-end: simulate discovery conversation, then save a seed doc."""

    def test_gateway_returns_responses(self, gateway: Gateway) -> None:
        """Gateway returns non-empty responses for each message."""
        chat_id = "e2e-test-conv"

        messages = [
            "We run a small warehouse and tracking inventory is a nightmare.",
            "We lose about 10 hours a week on manual stock counts.",
            "Our warehouse staff and the purchasing team both need visibility.",
        ]

        for msg in messages:
            resp = gateway.process_message(chat_id, msg)
            assert isinstance(resp, GatewayResponse)
            assert resp.text  # non-empty response
            assert resp.memory_count > 0  # messages are being stored

    def test_conversation_builds_history(self, gateway: Gateway) -> None:
        """Messages accumulate in conversation memory."""
        chat_id = "e2e-history-test"

        gateway.process_message(chat_id, "First message")
        gateway.process_message(chat_id, "Second message")

        history = gateway.memory.get_history(chat_id)
        # Each process_message adds user + assistant = 2 entries
        assert len(history) >= 4

    def test_save_discovery_writes_seed_doc(self, tmp_project: Path) -> None:
        """save_discovery writes a markdown seed doc to docs/seed/."""
        content = (
            "# Customer Discovery: Inventory Tracker\n\n"
            "## Problem\n"
            "Small warehouse operators waste 10+ hours/week on manual inventory counts.\n\n"
            "## Users\n"
            "- Warehouse staff (daily stock counts)\n"
            "- Purchasing team (reorder decisions)\n\n"
            "## Use Cases\n"
            "- Scan barcodes to update stock levels in real time\n"
            "- Auto-generate reorder alerts when stock drops below threshold\n"
            "- Weekly inventory variance reports\n\n"
            "## Success Criteria\n"
            "- 50% reduction in time spent on manual counts\n"
            "- Stock accuracy above 98%\n"
            "- Reorder alerts within 1 hour of threshold breach\n"
        )

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test-e2e-project", content=content)

        assert "saved" in result.lower() or "discovery" in result.lower()

        seed_dir = tmp_project / "docs" / "seed"
        seed_files = list(seed_dir.glob("discovery-*.md"))
        assert len(seed_files) == 1

        written = seed_files[0].read_text()
        assert "## Problem" in written
        assert "## Users" in written
        assert "## Use Cases" in written
        assert "## Success Criteria" in written
        assert "manual inventory counts" in written

    def test_execute_tool_routes_save_discovery(self, tmp_project: Path) -> None:
        """execute_tool dispatches save_discovery correctly."""
        content = "# Discovery\n\n## Problem\nTest problem\n\n## Users\nTest users\n\n## Use Cases\n- Test\n\n## Success Criteria\n- Pass"

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = execute_tool("save_discovery", {
                "slug": "test-e2e-project",
                "content": content,
            })

        assert "saved" in result.lower() or "discovery" in result.lower()

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1

    def test_full_pipeline_conversation_then_save(
        self, gateway: Gateway, tmp_project: Path
    ) -> None:
        """Full pipeline: conversation messages -> save_discovery -> seed doc on disk."""
        chat_id = "e2e-full-pipeline"

        # Simulate a discovery conversation
        discovery_messages = [
            "We run a small warehouse and tracking inventory is a nightmare.",
            "We lose about 10 hours a week on manual stock counts.",
            "Our warehouse staff and the purchasing team both need visibility.",
        ]

        responses = []
        for msg in discovery_messages:
            resp = gateway.process_message(chat_id, msg)
            responses.append(resp)

        # All messages got responses
        assert all(r.text for r in responses)

        # Conversation history was built
        history = gateway.memory.get_history(chat_id)
        assert len(history) >= 6  # 3 user + 3 assistant messages

        # Now the bot would call save_discovery — simulate that
        seed_content = (
            "# Customer Discovery: Inventory Tracker\n\n"
            "## Problem\n"
            "Small warehouse operators waste 10+ hours/week on manual counts.\n\n"
            "## Users\n"
            "- Warehouse staff\n"
            "- Purchasing team\n\n"
            "## Use Cases\n"
            "- Real-time barcode scanning\n"
            "- Automated reorder alerts\n\n"
            "## Success Criteria\n"
            "- 50% time reduction in manual counts\n"
            "- 98% stock accuracy\n"
        )

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = execute_tool("save_discovery", {
                "slug": "test-e2e-project",
                "content": seed_content,
            })

        # Seed doc was written
        assert "saved" in result.lower() or "discovery" in result.lower()

        seed_dir = tmp_project / "docs" / "seed"
        seed_files = list(seed_dir.glob("discovery-*.md"))
        assert len(seed_files) == 1

        doc = seed_files[0].read_text()
        for section in ["## Problem", "## Users", "## Use Cases", "## Success Criteria"]:
            assert section in doc, f"Missing section: {section}"
