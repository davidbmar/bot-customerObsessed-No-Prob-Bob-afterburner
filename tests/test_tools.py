"""Tests for bot/tools.py — save_discovery, get_project_summary, add_to_backlog, get_sprint_status, generate_vision, feedback_on_sprint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.tools import (
    add_to_backlog,
    execute_tool,
    generate_vision,
    feedback_on_sprint,
    get_project_summary,
    get_sprint_status,
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


# -- get_sprint_status tests --


@pytest.fixture
def sprint_project(tmp_path: Path) -> Path:
    """Create a project with sprint marker files."""
    (tmp_path / "SPRINT_BRIEF.md").write_text("# Sprint 7\n\nSome tasks here.\n")
    (tmp_path / ".agent-done-agentA").write_text("")
    (tmp_path / ".agent-done-agentB").write_text("")
    sprint_dir = tmp_path / ".sprint"
    sprint_dir.mkdir()
    (sprint_dir / "config.sh").write_text(
        'AGENTS=("agentA" "agentB" "agentC")\n'
    )
    return tmp_path


def test_get_sprint_status_reads_agents(sprint_project: Path) -> None:
    """get_sprint_status reports correct done/running agents."""
    result = get_sprint_status(sprint_project)
    assert result["sprint_number"] == 7
    assert result["agent_count"] == 3
    assert sorted(result["agents_done"]) == ["agentA", "agentB"]
    assert result["agents_running"] == ["agentC"]


def test_get_sprint_status_no_brief(tmp_path: Path) -> None:
    """get_sprint_status returns sprint_number 0 when no brief exists."""
    result = get_sprint_status(tmp_path)
    assert result["sprint_number"] == 0
    assert result["agents_done"] == []
    assert result["agents_running"] == []


def test_get_sprint_status_no_config(tmp_path: Path) -> None:
    """get_sprint_status infers agents from done files when no config exists."""
    (tmp_path / "SPRINT_BRIEF.md").write_text("Sprint 3 brief\n")
    (tmp_path / ".agent-done-worker1").write_text("")
    result = get_sprint_status(tmp_path)
    assert result["sprint_number"] == 3
    assert result["agents_done"] == ["worker1"]
    assert result["agent_count"] == 1


def test_execute_tool_dispatches_get_sprint_status(sprint_project: Path) -> None:
    """execute_tool routes 'get_sprint_status' correctly."""
    with patch("bot.tools._find_project_root", return_value=sprint_project):
        result = execute_tool("get_sprint_status", {"slug": "test"})
    data = json.loads(result)
    assert data["sprint_number"] == 7
    assert "agentA" in data["agents_done"]


def test_tool_registration_includes_get_sprint_status() -> None:
    """TOOL_DEFINITIONS in llm.py includes get_sprint_status."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "get_sprint_status" in tool_names


# -- generate_vision tests --


def test_generate_vision_writes_vision_md(tmp_path: Path) -> None:
    """generate_vision writes a Vision.md with correct sections."""
    result = generate_vision(
        tmp_path,
        problem="Users can't track inventory",
        users="Small business owners",
        use_cases="Manual stock counts\nAutomatic reorder alerts",
        differentiators="AI-powered predictions",
        success_criteria="50% time reduction\n95% accuracy",
        product_name="InventoryBot",
    )
    assert "generated" in result.lower() or "Vision" in result

    vision_path = tmp_path / "docs" / "lifecycle" / "VISION.md"
    assert vision_path.exists()

    content = vision_path.read_text()
    assert "# InventoryBot" in content
    assert "## Problem" in content
    assert "Users can't track inventory" in content
    assert "## Target Audience" in content
    assert "Small business owners" in content
    assert "## Key Differentiators" in content
    assert "AI-powered predictions" in content
    assert "## Solution Overview" in content
    assert "- Manual stock counts" in content
    assert "- Automatic reorder alerts" in content
    assert "## Success Criteria" in content
    assert "- 50% time reduction" in content
    assert "## FAQ" in content


def test_generate_vision_defaults_product_name(tmp_path: Path) -> None:
    """generate_vision uses project dir name when no product_name given."""
    project = tmp_path / "my-cool-app"
    project.mkdir()
    generate_vision(project, problem="Something", users="Someone")
    content = (project / "docs" / "lifecycle" / "VISION.md").read_text()
    assert "# My Cool App" in content


def test_generate_vision_creates_lifecycle_dir(tmp_path: Path) -> None:
    """generate_vision creates docs/lifecycle/ if it doesn't exist."""
    generate_vision(tmp_path, problem="P", users="U")
    assert (tmp_path / "docs" / "lifecycle").is_dir()


def test_generate_vision_tbd_for_empty_fields(tmp_path: Path) -> None:
    """generate_vision writes TBD for missing optional fields."""
    generate_vision(tmp_path, problem="Something", users="Someone")
    content = (tmp_path / "docs" / "lifecycle" / "VISION.md").read_text()
    assert "TBD" in content


def test_execute_tool_dispatches_generate_vision(tmp_path: Path) -> None:
    """execute_tool routes 'generate_vision' correctly."""
    from bot.tools import set_config
    from unittest.mock import MagicMock

    mock_config = MagicMock()
    mock_config.active_project_root = tmp_path
    mock_config.projects = {}
    set_config(mock_config)

    result = execute_tool("generate_vision", {
        "problem": "Test problem",
        "users": "Test users",
    })
    assert "Vision" in result or "generated" in result.lower()
    assert (tmp_path / "docs" / "lifecycle" / "VISION.md").exists()

    set_config(None)


def test_tool_registration_includes_generate_vision() -> None:
    """TOOL_DEFINITIONS in llm.py includes generate_vision."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "generate_vision" in tool_names


def test_tool_registration_generate_vision_params() -> None:
    """generate_vision tool definition has required problem and users parameters."""
    from bot.llm import TOOL_DEFINITIONS

    gen_vis = next(
        t for t in TOOL_DEFINITIONS if t["function"]["name"] == "generate_vision"
    )
    params = gen_vis["function"]["parameters"]
    assert "problem" in params["properties"]
    assert "users" in params["properties"]
    assert "problem" in params["required"]
    assert "users" in params["required"]


# -- feedback_on_sprint tests --


@pytest.fixture
def project_with_status(tmp_path: Path) -> Path:
    """Create a project with a PROJECT_STATUS doc."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "PROJECT_STATUS_sprint7.md").write_text(
        "# Sprint 7 Status\n\n"
        "## Completed\n"
        "- Web chat debug panel with real data\n"
        "- Settings panel for personality and model\n"
        "- Typing indicator with bouncing dots\n"
        "\n## Notes\nAll tests pass.\n"
    )
    return tmp_path


def test_feedback_on_sprint_reads_status(project_with_status: Path) -> None:
    """feedback_on_sprint extracts deliverables from PROJECT_STATUS."""
    result = feedback_on_sprint(project_with_status)
    assert "Sprint 7" in result
    assert "debug panel" in result.lower() or "Web chat" in result
    assert "match what you expected" in result.lower()


def test_feedback_on_sprint_no_status_docs(tmp_path: Path) -> None:
    """feedback_on_sprint returns error when no status docs exist."""
    result = feedback_on_sprint(tmp_path)
    assert "no project_status" in result.lower() or "not found" in result.lower()


def test_feedback_on_sprint_root_level_status(tmp_path: Path) -> None:
    """feedback_on_sprint finds PROJECT_STATUS at project root too."""
    (tmp_path / "PROJECT_STATUS_sprint5.md").write_text(
        "# Sprint 5\n\n## Summary\n- Added authentication\n- Fixed login bug\n"
    )
    result = feedback_on_sprint(tmp_path)
    assert "Sprint 5" in result


def test_execute_tool_dispatches_feedback_on_sprint(project_with_status: Path) -> None:
    """execute_tool routes 'feedback_on_sprint' correctly."""
    from bot.tools import set_config
    from unittest.mock import MagicMock

    mock_config = MagicMock()
    mock_config.active_project_root = project_with_status
    mock_config.projects = {}
    set_config(mock_config)

    result = execute_tool("feedback_on_sprint", {})
    assert "Sprint 7" in result

    set_config(None)


def test_tool_registration_includes_feedback_on_sprint() -> None:
    """TOOL_DEFINITIONS in llm.py includes feedback_on_sprint."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "feedback_on_sprint" in tool_names
