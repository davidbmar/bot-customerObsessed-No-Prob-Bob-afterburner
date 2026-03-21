"""Tests for bot/tools.py — save_discovery, get_project_summary, add_to_backlog, get_sprint_status, generate_vision, feedback_on_sprint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bot.tools import (
    _extract_section,
    _format_structured_discovery,
    add_to_backlog,
    execute_tool,
    generate_vision,
    feedback_on_sprint,
    get_project_summary,
    get_sprint_status,
    list_project_slugs,
    resolve_slug,
    tool_feedback_on_sprint,
    tool_get_sprint_status,
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
    """execute_tool routes 'get_sprint_status' correctly (filesystem fallback)."""
    import httpx as _httpx
    with patch("bot.tools.httpx.get", side_effect=_httpx.ConnectError("refused")):
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
    """execute_tool routes 'feedback_on_sprint' correctly (filesystem fallback)."""
    from bot.tools import set_config

    mock_config = MagicMock()
    mock_config.active_project_root = project_with_status
    mock_config.active_project = "test-project"
    mock_config.projects = {}
    set_config(mock_config)

    import httpx as _httpx
    with patch("bot.tools.httpx.get", side_effect=_httpx.ConnectError("refused")):
        result = execute_tool("feedback_on_sprint", {})
    assert "Sprint 7" in result

    set_config(None)


def test_tool_registration_includes_feedback_on_sprint() -> None:
    """TOOL_DEFINITIONS in llm.py includes feedback_on_sprint."""
    from bot.llm import TOOL_DEFINITIONS

    tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "feedback_on_sprint" in tool_names


# -- structured seed doc export tests (F-047) --


SAMPLE_MESSAGES_WITH_SYNTHESIS = [
    {"role": "user", "content": "I need a tool to track restaurant inventory"},
    {"role": "assistant", "content": "Tell me more about the problem."},
    {"role": "user", "content": "We waste a lot of food because we can't track expiry dates."},
    {"role": "assistant", "content": "Who are the main users?"},
    {"role": "user", "content": "Restaurant managers and kitchen staff."},
    {
        "role": "assistant",
        "content": (
            "## Problem\nRestaurants waste food due to poor expiry tracking.\n\n"
            "## Users\nRestaurant managers and kitchen staff.\n\n"
            "## Use Cases\n- Track expiry dates of inventory items\n"
            "- Get alerts before items expire\n\n"
            "## Success Criteria\n- 30% reduction in food waste\n"
            "- Staff can check inventory in under 1 minute\n"
        ),
    },
]

SAMPLE_MESSAGES_NO_SYNTHESIS = [
    {"role": "user", "content": "I need help with project planning"},
    {"role": "assistant", "content": "What kind of project are you working on?"},
    {"role": "user", "content": "A mobile app for dog walkers."},
]


def test_extract_section_finds_problem() -> None:
    """_extract_section extracts ## Problem content from markdown."""
    text = "## Problem\nSomething is broken.\n\n## Users\nEveryone."
    assert _extract_section(text, "Problem") == "Something is broken."


def test_extract_section_finds_multiline() -> None:
    """_extract_section handles multi-line section content."""
    text = "## Use Cases\n- Case 1\n- Case 2\n- Case 3\n\n## Success Criteria\nDone."
    result = _extract_section(text, "Use Cases")
    assert "Case 1" in result
    assert "Case 3" in result


def test_extract_section_case_insensitive() -> None:
    """_extract_section is case-insensitive for heading match."""
    text = "## success criteria\n- 50% improvement\n"
    assert "50% improvement" in _extract_section(text, "Success Criteria")


def test_extract_section_returns_empty_for_missing() -> None:
    """_extract_section returns empty string when heading not found."""
    assert _extract_section("## Other\nStuff.", "Problem") == ""


def test_extract_section_returns_empty_for_empty_content() -> None:
    """_extract_section returns empty string when section has no content."""
    assert _extract_section("## Problem\n\n## Users\nSomeone.", "Problem") == ""


def test_format_structured_discovery_with_synthesis() -> None:
    """_format_structured_discovery produces sections when bot synthesized them."""
    doc = _format_structured_discovery(SAMPLE_MESSAGES_WITH_SYNTHESIS, provider="claude")

    assert doc.startswith("# Discovery: I need a tool to track restaurant inventory")
    assert "Date:" in doc
    assert "Provider: claude" in doc
    assert "Messages: 6" in doc
    assert "## Problem" in doc
    assert "poor expiry tracking" in doc
    assert "## Users" in doc
    assert "kitchen staff" in doc
    assert "## Use Cases" in doc
    assert "Track expiry dates" in doc
    assert "## Success Criteria" in doc
    assert "30% reduction" in doc
    assert "## Raw Conversation" in doc


def test_format_structured_discovery_without_synthesis() -> None:
    """_format_structured_discovery uses placeholders when no synthesis occurred."""
    doc = _format_structured_discovery(SAMPLE_MESSAGES_NO_SYNTHESIS, provider="ollama")

    assert "# Discovery: I need help with project planning" in doc
    assert "Provider: ollama" in doc
    assert "Messages: 3" in doc
    assert "## Problem" in doc
    assert "[Not yet extracted from conversation]" in doc
    assert "## Raw Conversation" in doc
    assert "dog walkers" in doc


def test_format_structured_discovery_empty_messages() -> None:
    """_format_structured_discovery handles empty message list."""
    doc = _format_structured_discovery([])
    assert "# Discovery: Untitled Discovery" in doc
    assert "Messages: 0" in doc


def test_format_structured_discovery_title_truncation() -> None:
    """_format_structured_discovery truncates long titles to 80 chars."""
    long_msg = "A" * 200
    messages = [{"role": "user", "content": long_msg}]
    doc = _format_structured_discovery(messages)
    # Title line should have truncated content
    title_line = doc.splitlines()[0]
    # "# Discovery: " is 14 chars, plus 80 chars of content = 94 max
    assert len(title_line) <= 100


def test_format_structured_discovery_no_provider() -> None:
    """_format_structured_discovery defaults provider to 'unknown'."""
    doc = _format_structured_discovery(SAMPLE_MESSAGES_NO_SYNTHESIS)
    assert "Provider: unknown" in doc


def test_save_discovery_structured_writes_sections(tmp_project: Path) -> None:
    """save_discovery with structured=True creates doc with Problem/Users/Use Cases sections."""
    tmp_project.mkdir(parents=True)

    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = tool_save_discovery(
            slug="test-project",
            structured=True,
            messages=SAMPLE_MESSAGES_WITH_SYNTHESIS,
            provider="claude",
        )

    assert "saved" in result.lower() or "Discovery" in result

    seed_dir = tmp_project / "docs" / "seed"
    seed_files = list(seed_dir.glob("discovery-*.md"))
    assert len(seed_files) == 1

    content = seed_files[0].read_text()
    assert "## Problem" in content
    assert "poor expiry tracking" in content
    assert "## Users" in content
    assert "## Use Cases" in content
    assert "## Success Criteria" in content
    assert "## Raw Conversation" in content


def test_save_discovery_structured_false_writes_raw(tmp_project: Path) -> None:
    """save_discovery with structured=False writes raw content (backward compat)."""
    tmp_project.mkdir(parents=True)

    raw = "# Just some raw notes\nHello world."
    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = tool_save_discovery(slug="test-project", content=raw)

    seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
    assert len(seed_files) == 1
    assert seed_files[0].read_text() == raw


def test_save_discovery_structured_without_messages_writes_content(tmp_project: Path) -> None:
    """save_discovery structured=True but no messages falls back to content."""
    tmp_project.mkdir(parents=True)

    raw = "# Fallback content"
    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = tool_save_discovery(slug="test-project", content=raw, structured=True)

    seed_files = list((tmp_project / "docs" / "seed").glob("discovery-*.md"))
    assert seed_files[0].read_text() == raw


def test_execute_tool_save_discovery_structured(tmp_project: Path) -> None:
    """execute_tool routes structured save_discovery correctly."""
    tmp_project.mkdir(parents=True)

    with patch("bot.tools._find_project_root", return_value=tmp_project):
        result = execute_tool("save_discovery", {
            "slug": "test",
            "content": "",
            "structured": True,
            "messages": SAMPLE_MESSAGES_WITH_SYNTHESIS,
            "provider": "test-provider",
        })

    assert "saved" in result.lower() or "Discovery" in result


def test_extract_section_target_audience_fallback() -> None:
    """_format_structured_discovery falls back to 'Target Audience' for Users."""
    messages = [
        {"role": "user", "content": "Build me an app"},
        {"role": "assistant", "content": "## Target Audience\nDevelopers and designers.\n"},
    ]
    doc = _format_structured_discovery(messages)
    assert "Developers and designers" in doc.split("## Users")[1].split("##")[0]


# -- resolve_slug tests --

MOCK_PROJECTS_RESPONSE = {
    "projects": [
        {"slug": "bot-customerobsessed", "name": "Customer Obsessed Bot (No Prob Bob)"},
        {"slug": "fsm-generic", "name": "FSM-generic (Voice OS)"},
        {"slug": "grassyknoll", "name": "grassyknoll"},
    ],
    "activeProject": "bot-customerobsessed",
}


def _mock_httpx_get(url, **kwargs):
    """Mock httpx.get that returns project list."""
    mock = MagicMock()
    if "/api/projects" in url:
        mock.status_code = 200
        mock.json.return_value = MOCK_PROJECTS_RESPONSE
    elif "/api/project/" in url and "/status" in url:
        mock.status_code = 200
        mock.json.return_value = {
            "slug": "bot-customerobsessed",
            "latestSprint": 19,
            "totalSprints": 19,
            "openBugs": 0,
            "totalFeatures": 5,
            "recentSessions": [],
        }
    elif "/api/project/" in url and "/sprints" in url:
        mock.status_code = 200
        mock.json.return_value = {
            "sprints": [
                {"number": 19, "title": "Sprint 19", "summary": "Markdown rendering", "agentCount": 2},
            ]
        }
    else:
        mock.status_code = 404
        mock.json.return_value = {"error": "not found"}
    return mock


def test_resolve_slug_exact_match() -> None:
    """resolve_slug returns exact slug match."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        assert resolve_slug("bot-customerobsessed") == "bot-customerobsessed"


def test_resolve_slug_name_match() -> None:
    """resolve_slug matches by project name."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        assert resolve_slug("Customer Obsessed Bot (No Prob Bob)") == "bot-customerobsessed"


def test_resolve_slug_substring_match() -> None:
    """resolve_slug matches substring in slug or name."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        assert resolve_slug("bob") == "bot-customerobsessed"


def test_resolve_slug_word_overlap() -> None:
    """resolve_slug matches by word overlap."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        assert resolve_slug("voice os") == "fsm-generic"


def test_resolve_slug_no_match() -> None:
    """resolve_slug returns None when nothing matches."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        assert resolve_slug("nonexistent-xyz") is None


def test_resolve_slug_api_failure() -> None:
    """resolve_slug returns None when dashboard is unreachable."""
    import httpx as _httpx
    with patch("bot.tools.httpx.get", side_effect=_httpx.ConnectError("refused")):
        assert resolve_slug("bob") is None


def test_list_project_slugs() -> None:
    """list_project_slugs returns slug list from dashboard."""
    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        slugs = list_project_slugs()
    assert "bot-customerobsessed" in slugs
    assert "fsm-generic" in slugs
    assert len(slugs) == 3


# -- API-backed tool_get_sprint_status tests --


def test_tool_get_sprint_status_via_api() -> None:
    """tool_get_sprint_status calls dashboard API and returns status JSON."""
    from bot.tools import set_config

    mock_config = MagicMock()
    mock_config.active_project = "bot-customerobsessed"
    mock_config.projects = {}
    set_config(mock_config)

    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        result = tool_get_sprint_status(slug="bot-customerobsessed")

    data = json.loads(result)
    assert data["latestSprint"] == 19
    assert data["slug"] == "bot-customerobsessed"

    set_config(None)


def test_tool_get_sprint_status_fuzzy_fallback() -> None:
    """tool_get_sprint_status fuzzy-matches slug when exact match returns 404."""
    from bot.tools import set_config

    call_count = {"n": 0}

    def mock_get(url, **kwargs):
        call_count["n"] += 1
        m = MagicMock()
        if "/api/projects" in url:
            m.status_code = 200
            m.json.return_value = MOCK_PROJECTS_RESPONSE
        elif "/api/project/bob/status" in url:
            m.status_code = 404
            m.json.return_value = {"error": "not found"}
        elif "/api/project/bot-customerobsessed/status" in url:
            m.status_code = 200
            m.json.return_value = {"slug": "bot-customerobsessed", "latestSprint": 19}
        else:
            m.status_code = 404
            m.json.return_value = {"error": "not found"}
        return m

    mock_config = MagicMock()
    mock_config.active_project = ""
    mock_config.projects = {}
    set_config(mock_config)

    with patch("bot.tools.httpx.get", side_effect=mock_get):
        result = tool_get_sprint_status(slug="bob")

    data = json.loads(result)
    assert data["latestSprint"] == 19

    set_config(None)


# -- API-backed tool_feedback_on_sprint tests --


def test_tool_feedback_on_sprint_via_api() -> None:
    """tool_feedback_on_sprint calls dashboard sprints API."""
    from bot.tools import set_config

    mock_config = MagicMock()
    mock_config.active_project = "bot-customerobsessed"
    mock_config.projects = {}
    set_config(mock_config)

    with patch("bot.tools.httpx.get", side_effect=_mock_httpx_get):
        result = tool_feedback_on_sprint(slug="bot-customerobsessed")

    assert "Sprint 19" in result
    assert "Markdown rendering" in result
    assert "match what you expected" in result.lower()

    set_config(None)


def test_tool_feedback_on_sprint_no_sprints() -> None:
    """tool_feedback_on_sprint returns message when no sprints exist."""
    from bot.tools import set_config

    def mock_get(url, **kwargs):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"sprints": []}
        return m

    mock_config = MagicMock()
    mock_config.active_project = "bot-customerobsessed"
    mock_config.projects = {}
    set_config(mock_config)

    with patch("bot.tools.httpx.get", side_effect=mock_get):
        result = tool_feedback_on_sprint(slug="bot-customerobsessed")

    assert "no sprints" in result.lower()

    set_config(None)
