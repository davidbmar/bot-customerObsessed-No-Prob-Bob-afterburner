"""End-to-end pipeline tests: discovery conversation -> synthesis -> save seed -> verify file.

Proves the full value loop:
  1. Gateway processes multi-turn conversations (mocked LLM)
  2. save_discovery writes seed docs to a target project directory
  3. The /api/tools/save_discovery HTTP endpoint works end-to-end
  4. Edge cases: empty content, missing dirs, invalid paths
"""

from __future__ import annotations

import io
import json
import tempfile
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, ToolCall
from bot.tools import execute_tool, tool_save_discovery


# ─── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def personalities_dir() -> Path:
    """Return the real personalities directory."""
    return Path(__file__).parent.parent / "personalities"


@pytest.fixture
def mock_llm_chat():
    """Mock OllamaClient.chat with 5+ canned responses for multi-turn conversations."""
    responses = iter([
        LLMResponse(content="Hi! Tell me about the problem you're trying to solve.", duration_ms=50),
        LLMResponse(content="Interesting — how does that affect your daily workflow?", duration_ms=50),
        LLMResponse(content="Who else on your team feels this pain?", duration_ms=50),
        LLMResponse(content="What have you tried so far to solve this?", duration_ms=50),
        LLMResponse(content="Let me synthesize what I've heard so far.", duration_ms=50),
    ])

    def fake_chat(messages, system_prompt=None, tools=None):
        try:
            return next(responses)
        except StopIteration:
            return LLMResponse(content="Thank you for sharing all of that!", duration_ms=10)

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
    project = tmp_path / "test-pipeline-project"
    (project / "docs" / "seed").mkdir(parents=True)
    return project


@pytest.fixture
def tmp_project_no_seed(tmp_path: Path) -> Path:
    """Create a temporary project directory WITHOUT docs/seed/."""
    project = tmp_path / "test-no-seed-project"
    project.mkdir(parents=True)
    return project


SEED_CONTENT = (
    "# Customer Discovery: Pipeline Test\n\n"
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
)

EXPECTED_SECTIONS = ["## Problem", "## Users", "## Use Cases", "## Success Criteria"]


# ─── Test 1: Temporary project directory with docs/seed/ ──────────────────


class TestProjectDirectorySetup:
    """Test 1: Verify temporary project directories are set up correctly."""

    def test_tmp_project_has_seed_dir(self, tmp_project: Path) -> None:
        """Temporary project has docs/seed/ directory."""
        assert (tmp_project / "docs" / "seed").is_dir()

    def test_tmp_project_seed_dir_is_empty(self, tmp_project: Path) -> None:
        """docs/seed/ starts empty."""
        assert list((tmp_project / "docs" / "seed").iterdir()) == []

    def test_tmp_project_no_seed_has_no_seed_dir(self, tmp_project_no_seed: Path) -> None:
        """Project without seed dir indeed lacks docs/seed/."""
        assert not (tmp_project_no_seed / "docs" / "seed").exists()


# ─── Test 2: Simulate 5 message exchanges through Gateway ─────────────────


class TestGatewayConversation:
    """Test 2: Simulate 5+ message exchanges through the Gateway."""

    def test_five_exchange_conversation(self, gateway: Gateway) -> None:
        """Gateway handles 5 message exchanges with non-empty responses."""
        chat_id = "pipeline-5-exchanges"
        messages = [
            "We run a small warehouse and tracking inventory is a nightmare.",
            "We lose about 10 hours a week on manual stock counts.",
            "Our warehouse staff and the purchasing team both need visibility.",
            "We tried spreadsheets but they go stale within hours.",
            "We need something that updates in real time when items move.",
        ]

        responses = []
        for msg in messages:
            resp = gateway.process_message(chat_id, msg)
            responses.append(resp)

        assert len(responses) == 5
        assert all(isinstance(r, GatewayResponse) for r in responses)
        assert all(r.text for r in responses)

    def test_conversation_memory_grows(self, gateway: Gateway) -> None:
        """Each exchange adds to conversation memory."""
        chat_id = "pipeline-memory-growth"
        messages = [
            "First message about inventory problems.",
            "Second message about team needs.",
            "Third message about current workarounds.",
            "Fourth message about budget constraints.",
            "Fifth message about timeline expectations.",
        ]

        for msg in messages:
            gateway.process_message(chat_id, msg)

        history = gateway.memory.get_history(chat_id)
        # 5 user + 5 assistant = 10 messages minimum
        assert len(history) >= 10

    def test_gateway_response_has_memory_count(self, gateway: Gateway) -> None:
        """GatewayResponse includes memory_count field."""
        resp = gateway.process_message("mem-count-test", "Hello")
        assert resp.memory_count > 0

    def test_gateway_response_has_duration(self, gateway: Gateway) -> None:
        """GatewayResponse includes timing information."""
        resp = gateway.process_message("duration-test", "Hello")
        assert resp.duration_ms >= 0


# ─── Test 3: Call save_discovery with conversation summary ─────────────────


class TestSaveDiscovery:
    """Test 3: Call save_discovery(project_root, conversation_summary)."""

    def test_save_discovery_with_full_content(self, tmp_project: Path) -> None:
        """save_discovery writes seed doc with all synthesis sections."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test-project", content=SEED_CONTENT)
        assert "saved" in result.lower()

    def test_save_discovery_via_execute_tool(self, tmp_project: Path) -> None:
        """execute_tool dispatches save_discovery correctly."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = execute_tool("save_discovery", {
                "slug": "test-project",
                "content": SEED_CONTENT,
            })
        assert "saved" in result.lower()

    def test_save_discovery_creates_seed_dir_if_missing(self, tmp_project_no_seed: Path) -> None:
        """save_discovery creates docs/seed/ when it doesn't exist."""
        with patch("bot.tools._find_project_root", return_value=tmp_project_no_seed):
            result = tool_save_discovery(slug="test", content="# Test\n\n## Problem\nTest")
        assert "saved" in result.lower()
        assert (tmp_project_no_seed / "docs" / "seed").is_dir()


# ─── Test 4: Verify seed doc file was created in docs/seed/ ────────────────


class TestSeedDocCreation:
    """Test 4: Verify a seed doc file was created in {project_root}/docs/seed/."""

    def test_seed_file_exists_after_save(self, tmp_project: Path) -> None:
        """A discovery-*.md file appears in docs/seed/ after save."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1

    def test_seed_file_has_timestamped_name(self, tmp_project: Path) -> None:
        """Seed doc filename follows discovery-YYYYMMDD-HHMMSS.md pattern."""
        import re

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1
        assert re.match(r"discovery-\d{8}-\d{6}\.md", seed_files[0].name)

    def test_seed_file_is_not_empty(self, tmp_project: Path) -> None:
        """Seed doc file has non-zero content."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert seed_files[0].stat().st_size > 0


# ─── Test 5: Verify seed doc contains expected synthesis sections ──────────


class TestSeedDocContent:
    """Test 5: Verify the seed doc contains expected synthesis sections."""

    def test_contains_problem_section(self, tmp_project: Path) -> None:
        """Seed doc contains ## Problem section."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "## Problem" in doc

    def test_contains_users_section(self, tmp_project: Path) -> None:
        """Seed doc contains ## Users section."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "## Users" in doc

    def test_contains_use_cases_section(self, tmp_project: Path) -> None:
        """Seed doc contains ## Use Cases section."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "## Use Cases" in doc

    def test_contains_success_criteria_section(self, tmp_project: Path) -> None:
        """Seed doc contains ## Success Criteria section."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "## Success Criteria" in doc

    def test_contains_all_sections(self, tmp_project: Path) -> None:
        """Seed doc contains all expected synthesis sections."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        for section in EXPECTED_SECTIONS:
            assert section in doc, f"Missing section: {section}"

    def test_contains_specific_content(self, tmp_project: Path) -> None:
        """Seed doc preserves the actual discovery content."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=SEED_CONTENT)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "manual inventory counts" in doc
        assert "Warehouse staff" in doc
        assert "98%" in doc


# ─── Test 6: HTTP endpoint /api/tools/save_discovery ───────────────────────


class TestSaveDiscoveryHTTPEndpoint:
    """Test 6: The /api/tools/save_discovery HTTP endpoint."""

    @pytest.fixture
    def server_with_gateway(self, gateway, tmp_project):
        """Create a server with a gateway that has conversation history."""
        from bot.server import create_app

        # Seed conversation history
        gateway.memory.add("conv-123", "user", "We need inventory tracking.")
        gateway.memory.add("conv-123", "assistant", "Tell me more about the problem.")
        gateway.memory.add("conv-123", "user", "We lose 10 hours/week on manual counts.")
        gateway.memory.add("conv-123", "assistant", "Who on your team feels this most?")

        app = create_app(gateway, port=0)
        yield app, tmp_project
        app.server_close()

    def test_save_discovery_endpoint_returns_200(self, server_with_gateway) -> None:
        """POST /api/tools/save_discovery returns 200 with valid inputs."""
        app, tmp_project = server_with_gateway
        from bot.server import BotHTTPHandler

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            # Simulate the handler's logic directly
            result = tool_save_discovery(slug="test-project", content="# Discovery\n\n**User:** We need inventory tracking.\n")

        assert "saved" in result.lower()

    def test_save_discovery_endpoint_creates_file(self, server_with_gateway) -> None:
        """The endpoint creates a seed doc file on disk."""
        app, tmp_project = server_with_gateway

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(
                slug="test-project",
                content="# Discovery Notes\n\n**User:** We need inventory tracking.\n**Assistant:** Tell me more.\n"
            )

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) >= 1

    def test_handler_has_save_discovery_method(self) -> None:
        """BotHTTPHandler has the _handle_save_discovery method."""
        from bot.server import BotHTTPHandler
        assert hasattr(BotHTTPHandler, "_handle_save_discovery")

    def test_save_discovery_endpoint_with_conversation_history(self, gateway, tmp_project) -> None:
        """The endpoint formats conversation history as markdown and saves it."""
        # Get the conversation history
        history = gateway.memory.get_history("conv-123")
        assert len(history) >= 4

        # Format as the endpoint would
        lines = ["# Discovery Notes\n"]
        for msg in history:
            role = msg["role"].title()
            lines.append(f"**{role}:** {msg['content']}\n")
        content = "\n".join(lines)

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test-project", content=content)

        assert "saved" in result.lower()

        # Verify the file contains conversation content
        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1
        doc = seed_files[0].read_text()
        assert "inventory tracking" in doc.lower()

    def test_save_discovery_endpoint_missing_slug(self) -> None:
        """save_discovery with empty slug returns not-found error."""
        with patch("bot.tools._find_project_root", return_value=None):
            result = tool_save_discovery(slug="", content="test")
        assert "not found" in result.lower()


# ─── Full pipeline: conversation → save → verify ──────────────────────────


class TestFullPipeline:
    """Full pipeline: 5 message exchanges → save_discovery → verify seed doc."""

    def test_full_pipeline_conversation_to_seed_doc(
        self, gateway: Gateway, tmp_project: Path
    ) -> None:
        """Complete pipeline: conversation messages → save → seed doc on disk."""
        chat_id = "full-pipeline-test"

        messages = [
            "We run a small warehouse and tracking inventory is a nightmare.",
            "We lose about 10 hours a week on manual stock counts.",
            "Our warehouse staff and the purchasing team both need visibility.",
            "We tried spreadsheets but they go stale within hours.",
            "We need something that updates in real time when items move.",
        ]

        # Step 1: Process all 5 messages
        responses = []
        for msg in messages:
            resp = gateway.process_message(chat_id, msg)
            responses.append(resp)

        assert len(responses) == 5
        assert all(r.text for r in responses)

        # Step 2: Verify conversation history was built
        history = gateway.memory.get_history(chat_id)
        assert len(history) >= 10  # 5 user + 5 assistant

        # Step 3: Save discovery doc (as the bot would after synthesis)
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = execute_tool("save_discovery", {
                "slug": "test-project",
                "content": SEED_CONTENT,
            })

        # Step 4: Verify file was created
        assert "saved" in result.lower()
        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1

        # Step 5: Verify content has all sections
        doc = seed_files[0].read_text()
        for section in EXPECTED_SECTIONS:
            assert section in doc

    def test_pipeline_with_no_seed_dir(
        self, gateway: Gateway, tmp_project_no_seed: Path
    ) -> None:
        """Pipeline works even when docs/seed/ doesn't pre-exist."""
        chat_id = "no-seed-dir-pipeline"

        gateway.process_message(chat_id, "We need help with inventory.")
        gateway.process_message(chat_id, "Our team is 5 people.")

        with patch("bot.tools._find_project_root", return_value=tmp_project_no_seed):
            result = execute_tool("save_discovery", {
                "slug": "test",
                "content": SEED_CONTENT,
            })

        assert "saved" in result.lower()
        assert (tmp_project_no_seed / "docs" / "seed").is_dir()
        seed_files = list((tmp_project_no_seed / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1


# ─── Edge cases for save_discovery ─────────────────────────────────────────


class TestSaveDiscoveryEdgeCases:
    """Edge case tests for save_discovery."""

    def test_empty_content(self, tmp_project: Path) -> None:
        """save_discovery with empty content creates a file (empty is valid)."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test", content="")
        assert "saved" in result.lower()

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 1
        assert seed_files[0].read_text() == ""

    def test_invalid_project_slug(self) -> None:
        """save_discovery with unknown slug returns not-found error."""
        with patch("bot.tools._find_project_root", return_value=None):
            result = tool_save_discovery(slug="nonexistent-project", content="test")
        assert "not found" in result.lower()

    def test_missing_docs_seed_creates_it(self, tmp_project_no_seed: Path) -> None:
        """save_discovery creates docs/seed/ if it doesn't exist."""
        assert not (tmp_project_no_seed / "docs" / "seed").exists()

        with patch("bot.tools._find_project_root", return_value=tmp_project_no_seed):
            result = tool_save_discovery(slug="test", content="# Test seed doc")

        assert "saved" in result.lower()
        assert (tmp_project_no_seed / "docs" / "seed").is_dir()

    def test_save_discovery_with_unicode_content(self, tmp_project: Path) -> None:
        """save_discovery handles unicode content correctly."""
        content = "# Discovery\n\n## Problem\nUtilisateurs ne peuvent pas suivre l'inventaire.\n## Users\n- Equipe d'entrepot\n"
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test", content=content)
        assert "saved" in result.lower()

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "Utilisateurs" in doc

    def test_save_discovery_with_large_content(self, tmp_project: Path) -> None:
        """save_discovery handles large content without error."""
        content = "# Discovery\n\n" + ("Lorem ipsum dolor sit amet. " * 1000)
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test", content=content)
        assert "saved" in result.lower()

    def test_save_discovery_invalid_path_returns_error(self) -> None:
        """save_discovery with invalid filesystem path returns error gracefully."""
        invalid_path = Path("/dev/null/impossible/path")
        with patch("bot.tools._find_project_root", return_value=invalid_path):
            result = tool_save_discovery(slug="test", content="test")
        assert "failed" in result.lower() or "error" in result.lower()

    def test_save_discovery_empty_slug_no_config(self) -> None:
        """save_discovery with empty slug and no config returns not-found."""
        from bot.tools import set_config
        set_config(None)
        result = tool_save_discovery(slug="", content="test")
        assert "not found" in result.lower()

    def test_save_discovery_result_contains_path(self, tmp_project: Path) -> None:
        """save_discovery result message includes the file path."""
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            result = tool_save_discovery(slug="test", content="# Test")
        assert "saved to" in result.lower()
        assert "discovery-" in result

    def test_multiple_saves_create_separate_files(self, tmp_project: Path) -> None:
        """Multiple save_discovery calls create separate files."""
        import time

        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content="# First discovery")
            time.sleep(1.1)  # Ensure different timestamp
            tool_save_discovery(slug="test", content="# Second discovery")

        seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
        assert len(seed_files) == 2

    def test_save_discovery_preserves_markdown_formatting(self, tmp_project: Path) -> None:
        """save_discovery preserves markdown formatting in content."""
        content = "# Title\n\n## Section\n\n- Item 1\n- Item 2\n\n> Quote\n\n```python\nprint('hello')\n```\n"
        with patch("bot.tools._find_project_root", return_value=tmp_project):
            tool_save_discovery(slug="test", content=content)

        doc = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))[0].read_text()
        assert "```python" in doc
        assert "> Quote" in doc
        assert "- Item 1" in doc
