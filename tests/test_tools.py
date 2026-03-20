"""Tests for bot/tools.py — save_discovery and tool registration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.tools import execute_tool, tool_save_discovery


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal project directory."""
    return tmp_path / "test-project"


def test_save_discovery_writes_markdown(tmp_project: Path) -> None:
    """save_discovery writes correct markdown to docs/seed/ with timestamped name."""
    tmp_project.mkdir(parents=True)

    content = (
        "# Discovery\n\n"
        "## Problem\nUsers can't track inventory.\n\n"
        "## Users\nSmall business owners.\n\n"
        "## Use Cases\n- Manual stock counts\n\n"
        "## Success Criteria\n- 50% time reduction\n"
    )

    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = tool_save_discovery(slug="test-project", content=content)

    # Should report success
    assert "saved" in result.lower() or "Discovery" in result

    # Should have created docs/seed/ directory
    seed_dir = tmp_project / "docs" / "seed"
    assert seed_dir.exists()

    # Should have one file matching discovery-*.md pattern
    seed_files = list(seed_dir.glob("discovery-*.md"))
    assert len(seed_files) == 1

    # File content should match
    written = seed_files[0].read_text()
    assert "## Problem" in written
    assert "Users can't track inventory." in written
    assert "## Success Criteria" in written


def test_save_discovery_creates_seed_dir(tmp_project: Path) -> None:
    """save_discovery creates docs/seed/ if it doesn't exist."""
    tmp_project.mkdir(parents=True)

    with patch("bot.tools._find_project_root", return_value=tmp_project):
        tool_save_discovery(slug="test-project", content="# Test seed doc")

    assert (tmp_project / "docs" / "seed").is_dir()


def test_save_discovery_unknown_project() -> None:
    """save_discovery returns error when project not found."""
    with patch("bot.tools._find_project_root", return_value=None):
        result = tool_save_discovery(slug="nonexistent", content="test")

    assert "not found" in result.lower()


def test_execute_tool_dispatches_save_discovery(tmp_project: Path) -> None:
    """execute_tool routes 'save_discovery' to tool_save_discovery."""
    tmp_project.mkdir(parents=True)

    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = execute_tool("save_discovery", {"slug": "test", "content": "# Test"})

    assert "saved" in result.lower() or "Discovery" in result


def test_execute_tool_unknown_tool() -> None:
    """execute_tool returns error for unknown tool names."""
    result = execute_tool("nonexistent_tool", {})
    assert "unknown tool" in result.lower()


def test_tool_registration_includes_save_discovery() -> None:
    """TOOL_DEFINITIONS in llm.py includes save_discovery."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "save_discovery" in tool_names


def test_tool_registration_save_discovery_params() -> None:
    """save_discovery tool definition has required slug and content parameters."""
    from bot.llm import TOOL_DEFINITIONS

    save_disc = next(
        t for t in TOOL_DEFINITIONS if t["function"]["name"] == "save_discovery"
    )
    params = save_disc["function"]["parameters"]
    assert "slug" in params["properties"]
    assert "content" in params["properties"]
    assert set(params["required"]) == {"slug", "content"}
