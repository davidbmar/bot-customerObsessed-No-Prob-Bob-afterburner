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

# Global config reference — set by Gateway or server at startup
_config: Any = None


def set_config(config: Any) -> None:
    """Set the global config reference for project-aware tools."""
    global _config
    _config = config


def _resolve_project_root(slug: str | None = None) -> Path | None:
    """Resolve project root: use slug if given, else fall back to active project."""
    if slug:
        # Check config.projects first
        if _config and slug in getattr(_config, "projects", {}):
            return Path(_config.projects[slug])
        return _find_project_root(slug)
    # Fall back to active project
    if _config:
        root = getattr(_config, "active_project_root", None)
        if root:
            return root
    return None


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Dispatch a tool call by name, return result as text."""
    dispatch = {
        "save_discovery": tool_save_discovery,
        "get_project_summary": tool_get_project_summary,
        "add_to_backlog": tool_add_to_backlog,
        "get_sprint_status": tool_get_sprint_status,
        "generate_vision": tool_generate_vision,
        "feedback_on_sprint": tool_feedback_on_sprint,
        "list_projects": tool_list_projects,
    }
    fn = dispatch.get(name)
    if not fn:
        return f"Unknown tool: {name}"
    try:
        return fn(**arguments)
    except Exception as exc:
        log.exception("Tool %s failed", name)
        return f"Tool error: {exc}"


def tool_save_discovery(
    slug: str = "",
    content: str = "",
    structured: bool = False,
    messages: list[dict[str, str]] | None = None,
    provider: str = "",
) -> str:
    """Write a seed document into a project's docs/seed/ directory.

    When structured=True, formats the output with Problem/Users/Use Cases/
    Success Criteria sections extracted from the conversation messages.
    """
    project_root = _resolve_project_root(slug or None)
    if not project_root:
        return f"Project '{slug}' not found in dashboard registry."

    if structured and messages:
        content = _format_structured_discovery(messages, provider=provider)

    try:
        seed_dir = project_root / "docs" / "seed"
        seed_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"discovery-{ts}.md"
        filepath = seed_dir / filename
        filepath.write_text(content)
    except OSError as exc:
        log.error("Failed to write discovery doc to %s: %s", project_root, exc)
        return f"Failed to save discovery doc: {exc}"

    log.info("Saved discovery doc to %s", filepath)
    return f"Discovery notes saved to {filepath}"


def _format_structured_discovery(
    messages: list[dict[str, str]],
    provider: str = "",
) -> str:
    """Format conversation messages into a structured seed document.

    Extracts Problem/Users/Use Cases/Success Criteria sections from the
    conversation if the bot has already synthesized them; otherwise creates
    placeholder sections and includes the raw conversation.
    """
    # Build title from first user message
    first_user_msg = ""
    for msg in messages:
        if msg.get("role") == "user":
            first_user_msg = msg.get("content", "").strip()
            break
    title = first_user_msg[:80].rstrip(".!? ") if first_user_msg else "Untitled Discovery"

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg_count = len(messages)

    # Combine all assistant messages to search for synthesized sections
    assistant_text = "\n".join(
        msg.get("content", "")
        for msg in messages
        if msg.get("role") == "assistant"
    )

    sections = {
        "Problem": _extract_section(assistant_text, "Problem"),
        "Users": _extract_section(assistant_text, "Users")
        or _extract_section(assistant_text, "Target Audience")
        or _extract_section(assistant_text, "Target Users"),
        "Use Cases": _extract_section(assistant_text, "Use Cases"),
        "Success Criteria": _extract_section(assistant_text, "Success Criteria"),
    }

    # Build the document
    lines = [
        f"# Discovery: {title}",
        f"Date: {date_str}",
        f"Provider: {provider or 'unknown'}",
        f"Messages: {msg_count}",
        "",
        "## Problem",
        sections["Problem"] or "[Not yet extracted from conversation]",
        "",
        "## Users",
        sections["Users"] or "[Not yet extracted from conversation]",
        "",
        "## Use Cases",
        sections["Use Cases"] or "[Not yet extracted from conversation]",
        "",
        "## Success Criteria",
        sections["Success Criteria"] or "[Not yet extracted from conversation]",
        "",
        "## Raw Conversation",
    ]

    for msg in messages:
        role = msg.get("role", "unknown").title()
        content = msg.get("content", "")
        lines.append(f"**{role}:** {content}")
        lines.append("")

    return "\n".join(lines)


def tool_get_project_summary(slug: str = "") -> str:
    """Get project summary from the Afterburner dashboard API."""
    project_root = _resolve_project_root(slug or None)
    try:
        resp = httpx.post(
            f"{DASHBOARD_URL}/api/lifecycle/load-all",
            json={"projectRoot": str(project_root or "")},
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
    slug: str = "", kind: str = "", title: str = "", priority: str = "Medium"
) -> str:
    """Add a bug or feature to the project's backlog README.md."""
    project_root = _resolve_project_root(slug or None)
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
        data = json.loads(projects_json.read_text())
        # Handle both formats: plain list or {projects: [...], activeProject: "..."}
        if isinstance(data, dict):
            projects = data.get("projects", [])
        elif isinstance(data, list):
            projects = data
        else:
            return None
        for p in projects:
            if not isinstance(p, dict):
                continue
            if p.get("slug") == slug:
                root = p.get("rootPath", "").replace("~", str(Path.home()))
                return Path(root)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return None


def resolve_slug(user_input: str) -> str | None:
    """Match user input like 'the Bob project' to a dashboard project slug.

    Tries exact match, then substring, then word overlap.
    Returns the best matching slug or None.
    """
    try:
        resp = httpx.get(f"{DASHBOARD_URL}/api/projects", timeout=5.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
    except (httpx.HTTPError, ValueError):
        return None

    projects = data.get("projects", [])
    if not projects:
        return None

    query = user_input.lower().strip()

    # Exact slug match
    for p in projects:
        if p.get("slug", "").lower() == query:
            return p["slug"]

    # Exact name match
    for p in projects:
        if p.get("name", "").lower() == query:
            return p["slug"]

    # Substring match in slug or name
    for p in projects:
        slug = p.get("slug", "").lower()
        name = p.get("name", "").lower()
        if query in slug or query in name:
            return p["slug"]

    # Word overlap — split query into words and find best match
    query_words = set(query.split())
    best_slug = None
    best_score = 0
    for p in projects:
        slug = p.get("slug", "").lower()
        name = p.get("name", "").lower()
        candidate_words = set(slug.replace("-", " ").split()) | set(name.split())
        score = len(query_words & candidate_words)
        if score > best_score:
            best_score = score
            best_slug = p["slug"]

    return best_slug if best_score > 0 else None


def list_project_slugs() -> list[str]:
    """Return all registered project slugs from the dashboard."""
    try:
        resp = httpx.get(f"{DASHBOARD_URL}/api/projects", timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            return [p.get("slug", "") for p in data.get("projects", []) if p.get("slug")]
    except (httpx.HTTPError, ValueError):
        pass
    return []


def tool_list_projects() -> str:
    """List all registered Afterburner projects with slugs and names."""
    try:
        resp = httpx.get(f"{DASHBOARD_URL}/api/projects", timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            projects = data.get("projects", [])
            if not projects:
                return "No projects registered in the dashboard."
            lines = ["Registered projects:"]
            for p in projects:
                slug = p.get("slug", "unknown")
                name = p.get("name", slug)
                lines.append(f"  - {name} (slug: {slug})")
            return "\n".join(lines)
    except httpx.HTTPError as exc:
        log.warning("Dashboard unavailable for list_projects: %s", exc)
        return "Dashboard unavailable. Cannot list projects right now."
    return "No projects found."


def tool_get_sprint_status(slug: str = "") -> str:
    """Get sprint status for a project via the dashboard API."""
    resolved = slug or (_config.active_project if _config else "")
    if not resolved:
        return "No project specified and no active project set."

    # Try dashboard API first
    dashboard_err = ""
    try:
        resp = httpx.get(
            f"{DASHBOARD_URL}/api/project/{resolved}/status",
            timeout=10.0,
        )
        if resp.status_code == 200:
            return json.dumps(resp.json())
        if resp.status_code == 404:
            # Try fuzzy match
            matched = resolve_slug(resolved)
            if matched and matched != resolved:
                resp = httpx.get(
                    f"{DASHBOARD_URL}/api/project/{matched}/status",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    return json.dumps(resp.json())
            return f"Project '{slug}' not found in dashboard."
    except httpx.HTTPError as exc:
        dashboard_err = str(exc)
        log.warning("Dashboard unavailable for sprint status: %s", dashboard_err)

    # Fall back to filesystem reading
    project_root = _resolve_project_root(slug or None)
    if not project_root:
        if dashboard_err:
            return f"Dashboard unavailable, using local data — but project '{slug}' not found locally either."
        return f"Project '{slug}' not found in dashboard registry."
    result = get_sprint_status(project_root)
    if dashboard_err:
        result["_note"] = "Dashboard unavailable, using local data"
    return json.dumps(result)


def get_sprint_status(project_root: Path) -> dict[str, Any]:
    """Read .agent-done-* files and SPRINT_BRIEF.md to determine sprint status.

    Filesystem fallback — used only when dashboard API is unavailable.
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


def tool_generate_vision(
    problem: str = "",
    users: str = "",
    use_cases: str = "",
    differentiators: str = "",
    success_criteria: str = "",
    product_name: str = "",
    slug: str = "",
) -> str:
    """Generate a Vision markdown document from structured discovery data."""
    project_root = _resolve_project_root(slug or None)
    if not project_root:
        return "No active project set. Switch to a project first."

    return generate_vision(
        project_root,
        problem=problem,
        users=users,
        use_cases=use_cases,
        differentiators=differentiators,
        success_criteria=success_criteria,
        product_name=product_name,
    )


def generate_vision(
    project_root: Path,
    problem: str = "",
    users: str = "",
    use_cases: str = "",
    differentiators: str = "",
    success_criteria: str = "",
    product_name: str = "",
) -> str:
    """Generate a Vision.md in Afterburner format and write it to the project.

    Returns a status message.
    """
    name = product_name or project_root.name.replace("-", " ").title()

    sections = [
        f"# {name}",
        "",
        "## Problem",
        problem or "TBD",
        "",
        "## Target Audience",
        users or "TBD",
        "",
        "## Key Differentiators",
        differentiators or "TBD",
        "",
        "## Solution Overview",
    ]
    if use_cases:
        for uc in use_cases.split("\n"):
            uc = uc.strip()
            if uc:
                if not uc.startswith("- "):
                    uc = f"- {uc}"
                sections.append(uc)
    else:
        sections.append("TBD")

    sections.extend([
        "",
        "## Success Criteria",
    ])
    if success_criteria:
        for sc in success_criteria.split("\n"):
            sc = sc.strip()
            if sc:
                if not sc.startswith("- "):
                    sc = f"- {sc}"
                sections.append(sc)
    else:
        sections.append("TBD")

    sections.extend(["", "## FAQ", "", "TBD", ""])

    vision_content = "\n".join(sections)

    lifecycle_dir = project_root / "docs" / "lifecycle"
    lifecycle_dir.mkdir(parents=True, exist_ok=True)
    vision_path = lifecycle_dir / "VISION.md"
    vision_path.write_text(vision_content)

    log.info("Generated Vision doc at %s", vision_path)
    return f"Vision document generated at {vision_path}"


def tool_feedback_on_sprint(slug: str = "") -> str:
    """Get latest sprint summary via the dashboard API, with filesystem fallback."""
    resolved = slug or (_config.active_project if _config else "")

    # Try dashboard API first
    if resolved:
        try:
            resp = httpx.get(
                f"{DASHBOARD_URL}/api/project/{resolved}/sprints",
                timeout=10.0,
            )
            if resp.status_code == 404:
                matched = resolve_slug(resolved)
                if matched and matched != resolved:
                    resp = httpx.get(
                        f"{DASHBOARD_URL}/api/project/{matched}/sprints",
                        timeout=10.0,
                    )
            if resp.status_code == 200:
                data = resp.json()
                sprints = data.get("sprints", [])
                if sprints:
                    latest = sprints[0]
                    parts = [f"Sprint {latest.get('number', '?')} summary:"]
                    if latest.get("summary"):
                        parts.append(f"\n{latest['summary']}")
                    if latest.get("agentCount"):
                        parts.append(f"\nAgents: {latest['agentCount']}")
                    parts.append(f"\nDoes this match what you expected from Sprint {latest.get('number', '?')}?")
                    return "\n".join(parts)
                return "No sprints found in dashboard data. Has a sprint been completed?"
        except httpx.HTTPError as exc:
            log.warning("Dashboard unavailable for sprint feedback: %s", exc)

    # Filesystem fallback
    project_root = _resolve_project_root(slug or None)
    if not project_root:
        return "No active project set. Switch to a project first."

    return feedback_on_sprint(project_root)


def feedback_on_sprint(project_root: Path) -> str:
    """Read the latest PROJECT_STATUS doc and return a structured summary.

    Returns a summary string the bot can present to the user.
    """
    # Find PROJECT_STATUS docs (sprint-merge.sh generates these)
    status_files = sorted(project_root.glob("docs/PROJECT_STATUS*.md"), reverse=True)
    if not status_files:
        # Also check root-level status files
        status_files = sorted(project_root.glob("PROJECT_STATUS*.md"), reverse=True)
    if not status_files:
        return "No PROJECT_STATUS documents found. Has a sprint been completed and merged?"

    latest = status_files[0]
    content = latest.read_text()

    # Extract sprint number
    sprint_match = re.search(r"[Ss]print\s+(\d+)", content)
    sprint_num = sprint_match.group(1) if sprint_match else "?"

    # Extract deliverables (look for list items under common headings)
    deliverables: list[str] = []
    in_deliverables = False
    for line in content.splitlines():
        lower = line.lower().strip()
        if any(h in lower for h in ["## delivered", "## completed", "## changes", "## what shipped", "## summary"]):
            in_deliverables = True
            continue
        if in_deliverables and line.startswith("##"):
            in_deliverables = False
            continue
        if in_deliverables and line.strip().startswith(("- ", "* ", "1.", "2.", "3.")):
            deliverables.append(line.strip().lstrip("-*0123456789. "))

    # If no structured deliverables found, extract all list items
    if not deliverables:
        deliverables = [
            line.strip().lstrip("-* ")
            for line in content.splitlines()
            if line.strip().startswith(("- ", "* "))
        ][:10]

    summary_parts = [f"Sprint {sprint_num} summary from {latest.name}:"]
    if deliverables:
        summary_parts.append("\nDeliverables:")
        for d in deliverables:
            summary_parts.append(f"  - {d}")
    else:
        summary_parts.append("\n(No structured deliverables extracted. Review the full status doc.)")

    summary_parts.append(f"\nDoes this match what you expected from Sprint {sprint_num}?")
    return "\n".join(summary_parts)


def _extract_section(text: str, heading: str) -> str:
    """Extract content under a markdown ## heading from text.

    Returns the text between the heading and the next ## heading (or end),
    stripped of leading/trailing whitespace. Returns empty string if not found.
    """
    pattern = re.compile(
        rf"^##\s*{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)",
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if match:
        content = match.group(1).strip()
        if content:
            return content
    return ""


# Public aliases for tool dispatch compatibility
save_discovery = tool_save_discovery
