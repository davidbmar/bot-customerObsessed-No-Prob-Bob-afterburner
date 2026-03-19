"""Afterburner API tool implementations.

These are called when the LLM invokes tool_calls. Each function
executes a real action (writing files, calling dashboard APIs).
"""

from __future__ import annotations

import json
import logging
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
    # Find project root from dashboard registry
    project_root = _find_project_root(slug)
    if not project_root:
        return f"Project '{slug}' not found in dashboard registry."

    seed_dir = project_root / "docs" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)

    # Write discovery doc
    filename = "customer-discovery.md"
    filepath = seed_dir / filename
    filepath.write_text(content)
    log.info("Saved discovery doc to %s", filepath)
    return f"Discovery notes saved to {filepath}"


def tool_get_project_summary(slug: str) -> str:
    """Get project summary from the Afterburner dashboard API."""
    try:
        # Try loading lifecycle docs
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
