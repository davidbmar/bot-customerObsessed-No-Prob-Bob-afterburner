"""Afterburner API tool implementations.

These are called when the LLM invokes tool_calls. Each function
executes a real action (writing files, calling dashboard APIs).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)

DASHBOARD_URL = "http://127.0.0.1:1201"


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Dispatch a tool call by name, return result as text."""
    dispatch = {
        "save_discovery": tool_save_discovery,
        "get_project_summary": tool_get_project_summary,
        "add_to_backlog": tool_add_to_backlog,
        "get_sprint_status": tool_get_sprint_status,
    }
    fn = dispatch.get(name)
    if not fn:
        return f"Unknown tool: {name}"
    try:
        return fn(**arguments)
    except Exception as exc:
        log.exception("Tool %s failed", name)
        return f"Tool error: {exc}"


def tool_save_discovery(slug: str, content: str) -> str:
    """Write a seed document into a project's docs/seed/ directory."""
    project_root = _find_project_root(slug)
    if not project_root:
        return f"Project '{slug}' not found in dashboard registry."

    seed_dir = project_root / "docs" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"discovery-{ts}.md"
    filepath = seed_dir / filename
    filepath.write_text(content)
    log.info("Saved discovery doc to %s", filepath)
    return f"Discovery notes saved to {filepath}"


def tool_get_project_summary(slug: str) -> str:
    """Get project summary from the Afterburner dashboard API."""
    try:
        resp = httpx.post(
            f"{DASHBOARD_URL}/api/lifecycle/load-all",
            json={"projectRoot": str(_find_project_root(slug) or "")},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            parts: list[str] = []
            for doc_type in ["vision", "plan", "roadmap"]:
                content = data.get(doc_type, "")
                if content:
                    parts.append(f"## {doc_type.title()}\n{content[:500]}")
            if parts:
                return "\n\n".join(parts)
            return f"Project '{slug}' exists but has no lifecycle docs yet."
        return f"Could not load project summary (HTTP {resp.status_code})."
    except httpx.HTTPError as exc:
        return f"Dashboard unavailable: {exc}"


def get_project_summary(project_root: Path) -> dict[str, Any]:
    """Read Vision.md, Plan.md, Roadmap.md from a project's docs/lifecycle/.

    Returns a dict with title, problem, appetite, and sprint_candidates
    extracted from the lifecycle documents.
    """
    lifecycle_dir = project_root / "docs" / "lifecycle"
    result: dict[str, Any] = {
        "title": "",
        "problem": "",
        "appetite": "",
        "sprint_candidates": [],
    }

    if not lifecycle_dir.exists():
        return result

    # Read Vision.md for title and problem
    vision_path = lifecycle_dir / "Vision.md"
    if vision_path.exists():
        vision_text = vision_path.read_text()
        # Extract title from first heading
        title_match = re.search(r"^#\s+(.+)$", vision_text, re.MULTILINE)
        if title_match:
            result["title"] = title_match.group(1).strip()
        # Extract problem section
        problem_match = re.search(
            r"##\s*Problem\s*\n(.*?)(?=\n##|\Z)", vision_text, re.DOTALL
        )
        if problem_match:
            result["problem"] = problem_match.group(1).strip()

    # Read Plan.md for appetite
    plan_path = lifecycle_dir / "Plan.md"
    if plan_path.exists():
        plan_text = plan_path.read_text()
        appetite_match = re.search(
            r"##\s*Appetite\s*\n(.*?)(?=\n##|\Z)", plan_text, re.DOTALL
        )
        if appetite_match:
            result["appetite"] = appetite_match.group(1).strip()

    # Read Roadmap.md for sprint candidates
    roadmap_path = lifecycle_dir / "Roadmap.md"
    if roadmap_path.exists():
        roadmap_text = roadmap_path.read_text()
        # Look for list items that mention sprints
        candidates = re.findall(r"[-*]\s+(.+)", roadmap_text)
        result["sprint_candidates"] = candidates

    return result


def tool_add_to_backlog(
    slug: str, kind: str, title: str, priority: str = "Medium"
) -> str:
    """Add a bug or feature to the project's backlog README.md."""
    project_root = _find_project_root(slug)
    if not project_root:
        return f"Project '{slug}' not found in dashboard registry."

    return add_to_backlog(project_root, kind=kind, title=title, priority=priority)


def add_to_backlog(
    project_root: Path,
    kind: str,
    title: str,
    priority: str = "Medium",
) -> str:
    """Add a bug or feature to a project's backlog README.md.

    Args:
        project_root: Path to the project root.
        kind: 'bug' or 'feature'.
        title: Short description of the item.
        priority: Priority level (Low, Medium, High, Critical).

    Returns:
        A message with the new item ID.
    """
    backlog_path = project_root / "docs" / "project-memory" / "backlog" / "README.md"
    if not backlog_path.exists():
        return f"Backlog not found at {backlog_path}"

    content = backlog_path.read_text()
    kind_lower = kind.lower()

    if kind_lower in ("bug", "bugs"):
        prefix = "B"
        section = "## Bugs"
    elif kind_lower in ("feature", "features"):
        prefix = "F"
        section = "## Features"
    else:
        return f"Unknown kind '{kind}'. Use 'bug' or 'feature'."

    # Find highest existing ID for this prefix
    pattern = re.compile(rf"\|\s*{prefix}-(\d+)\s*\|")
    ids = [int(m.group(1)) for m in pattern.finditer(content)]
    next_id = max(ids, default=0) + 1
    item_id = f"{prefix}-{next_id:03d}"

    # Build new row
    new_row = f"| {item_id} | {title} | {priority} | Open |\n"

    # Find the end of the appropriate table section
    if section in content:
        # Find the last row in this section's table
        section_start = content.index(section)
        # Find the next section or end of file
        next_section = re.search(r"\n## ", content[section_start + len(section) :])
        if next_section:
            insert_pos = section_start + len(section) + next_section.start()
        else:
            insert_pos = len(content)

        # Insert before the next section (or at end), after trailing newline
        content = content[:insert_pos].rstrip("\n") + "\n" + new_row + "\n" + content[insert_pos:].lstrip("\n")
    else:
        content += f"\n{section}\n\n| ID | Title | Priority | Status |\n|----|-------|----------|--------|\n{new_row}"

    backlog_path.write_text(content)
    log.info("Added %s to backlog: %s", item_id, title)
    return f"Added {item_id}: {title}"


def _find_project_root(slug: str) -> Path | None:
    """Look up project root from dashboard projects.json."""
    projects_json = Path.home() / "src" / "traceable-searchable-adr-memory-index" / "dashboard" / "projects.json"
    if not projects_json.exists():
        return None
    try:
        projects = json.loads(projects_json.read_text())
        for p in projects:
            if p.get("slug") == slug:
                root = p.get("rootPath", "").replace("~", str(Path.home()))
                return Path(root)
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def tool_get_sprint_status(slug: str) -> str:
    """Get sprint status for a project by reading sprint marker files."""
    project_root = _find_project_root(slug)
    if not project_root:
        return f"Project '{slug}' not found in dashboard registry."
    result = get_sprint_status(project_root)
    return json.dumps(result)


def get_sprint_status(project_root: Path) -> dict[str, Any]:
    """Read .agent-done-* files and SPRINT_BRIEF.md to determine sprint status.

    Returns a dict with sprint_number, agent_count, agents_done, agents_running.
    """
    result: dict[str, Any] = {
        "sprint_number": 0,
        "agent_count": 0,
        "agents_done": [],
        "agents_running": [],
    }

    # Try to extract sprint number from SPRINT_BRIEF.md
    brief_path = project_root / "SPRINT_BRIEF.md"
    if brief_path.exists():
        brief_text = brief_path.read_text()
        sprint_match = re.search(r"[Ss]print\s+(\d+)", brief_text)
        if sprint_match:
            result["sprint_number"] = int(sprint_match.group(1))

    # Count agent-done marker files
    done_files = list(project_root.glob(".agent-done-*"))
    done_agents = [f.name.replace(".agent-done-", "") for f in done_files]
    result["agents_done"] = sorted(done_agents)

    # Detect all agents from worktree branches or brief
    # Look for agent branches in .sprint/ config or AGENT_BRIEF files
    agent_briefs = list(project_root.glob("AGENT_BRIEF*.md"))
    all_agents: set[str] = set()

    # Check for .sprint/config.sh to get agent count
    sprint_config = project_root / ".sprint" / "config.sh"
    if sprint_config.exists():
        config_text = sprint_config.read_text()
        agents_match = re.search(r'AGENTS=\(([^)]+)\)', config_text)
        if agents_match:
            agents_str = agents_match.group(1)
            for agent in re.findall(r'"([^"]+)"', agents_str):
                all_agents.add(agent)

    # If no agents found from config, infer from done files
    if not all_agents and done_agents:
        all_agents = set(done_agents)

    result["agent_count"] = len(all_agents)
    result["agents_running"] = sorted(all_agents - set(done_agents))

    return result


# Public aliases
save_discovery = tool_save_discovery
