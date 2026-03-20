"""Tests for bot/tools.py — save_discovery, get_project_summary, add_to_backlog."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.tools import (
    add_to_backlog,
    execute_tool,
    get_project_summary,
    tool_save_discovery,
)


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


# -- get_project_summary tests --


@pytest.fixture
def project_with_lifecycle(tmp_path: Path) -> Path:
    """Create a project with lifecycle docs."""
    lifecycle = tmp_path / "docs" / "lifecycle"
    lifecycle.mkdir(parents=True)

    (lifecycle / "Vision.md").write_text(
        "# Inventory Tracker\n\n## Problem\nUsers can't track stock levels.\n\n## Solution\nBuild a tracker.\n"
    )
    (lifecycle / "Plan.md").write_text(
        "# Plan\n\n## Appetite\n2 weeks, small batch.\n\n## Scope\nMVP only.\n"
    )
    (lifecycle / "Roadmap.md").write_text(
        "# Roadmap\n\n- Sprint 1: Core inventory CRUD\n- Sprint 2: Reporting dashboard\n- Sprint 3: Mobile support\n"
    )
    return tmp_path


def test_get_project_summary_reads_lifecycle(project_with_lifecycle: Path) -> None:
    """get_project_summary reads Vision, Plan, Roadmap docs."""
    result = get_project_summary(project_with_lifecycle)
    assert result["title"] == "Inventory Tracker"
    assert "stock levels" in result["problem"].lower()
    assert "2 weeks" in result["appetite"]
    assert len(result["sprint_candidates"]) == 3


def test_get_project_summary_missing_lifecycle(tmp_path: Path) -> None:
    """get_project_summary returns empty dict when no lifecycle dir."""
    result = get_project_summary(tmp_path)
    assert result["title"] == ""
    assert result["problem"] == ""
    assert result["sprint_candidates"] == []


def test_get_project_summary_partial_docs(tmp_path: Path) -> None:
    """get_project_summary handles missing individual docs gracefully."""
    lifecycle = tmp_path / "docs" / "lifecycle"
    lifecycle.mkdir(parents=True)
    (lifecycle / "Vision.md").write_text("# My Project\n\n## Problem\nSomething is broken.\n")
    result = get_project_summary(tmp_path)
    assert result["title"] == "My Project"
    assert result["appetite"] == ""
    assert result["sprint_candidates"] == []


# -- add_to_backlog tests --


@pytest.fixture
def project_with_backlog(tmp_path: Path) -> Path:
    """Create a project with a backlog README."""
    backlog_dir = tmp_path / "docs" / "project-memory" / "backlog"
    backlog_dir.mkdir(parents=True)
    (backlog_dir / "README.md").write_text(
        "# Backlog\n\n## Bugs\n\n"
        "| ID | Title | Priority | Status |\n"
        "|----|-------|----------|--------|\n"
        "| B-001 | Login crash | High | Open |\n"
        "\n## Features\n\n"
        "| ID | Title | Priority | Status |\n"
        "|----|-------|----------|--------|\n"
        "| F-001 | Dark mode | Medium | Planned |\n"
        "| F-002 | Export CSV | Low | Planned |\n"
    )
    return tmp_path


def test_add_to_backlog_adds_bug(project_with_backlog: Path) -> None:
    """add_to_backlog adds a new bug with incremented ID."""
    result = add_to_backlog(project_with_backlog, kind="bug", title="Crash on save", priority="Critical")
    assert "B-002" in result
    content = (project_with_backlog / "docs" / "project-memory" / "backlog" / "README.md").read_text()
    assert "B-002" in content
    assert "Crash on save" in content
    assert "Critical" in content


def test_add_to_backlog_adds_feature(project_with_backlog: Path) -> None:
    """add_to_backlog adds a new feature with incremented ID."""
    result = add_to_backlog(project_with_backlog, kind="feature", title="Dark theme toggle")
    assert "F-003" in result
    content = (project_with_backlog / "docs" / "project-memory" / "backlog" / "README.md").read_text()
    assert "F-003" in content
    assert "Dark theme toggle" in content


def test_add_to_backlog_unknown_kind(project_with_backlog: Path) -> None:
    """add_to_backlog rejects unknown kind."""
    result = add_to_backlog(project_with_backlog, kind="epic", title="Big thing")
    assert "unknown" in result.lower()


def test_add_to_backlog_missing_file(tmp_path: Path) -> None:
    """add_to_backlog returns error when backlog doesn't exist."""
    result = add_to_backlog(tmp_path, kind="bug", title="Something")
    assert "not found" in result.lower()


def test_execute_tool_dispatches_add_to_backlog(project_with_backlog: Path) -> None:
    """execute_tool routes 'add_to_backlog' to tool_add_to_backlog."""
    with patch("bot.tools._find_project_root", return_value=project_with_backlog):
        result = execute_tool("add_to_backlog", {"slug": "test", "kind": "bug", "title": "Test bug"})
    assert "B-002" in result


def test_tool_registration_includes_add_to_backlog() -> None:
    """TOOL_DEFINITIONS in llm.py includes add_to_backlog."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "add_to_backlog" in tool_names


def test_tool_registration_includes_get_project_summary() -> None:
    """TOOL_DEFINITIONS in llm.py includes get_project_summary."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "get_project_summary" in tool_names
