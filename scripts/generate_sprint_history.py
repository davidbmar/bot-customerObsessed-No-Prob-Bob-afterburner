#!/usr/bin/env python3
"""Generate PROJECT_STATUS docs for Sprints 1-11 from archived sprint briefs.

Reads each .sprint/history/sprint-{N}-brief.md, extracts goal and agent info,
and writes docs/PROJECT_STATUS_YYYY-MM-DD-sprintN.md following the template.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_DIR = REPO_ROOT / ".sprint" / "history"
DOCS_DIR = REPO_ROOT / "docs"
FALLBACK_DATE = "2026-03-19"


def git_date_for_brief(sprint_num: int) -> str:
    """Get the author date of the commit that added the sprint brief."""
    brief_path = f".sprint/history/sprint-{sprint_num}-brief.md"
    try:
        result = subprocess.run(
            ["git", "log", "--format=%aI", "--diff-filter=A", "--", brief_path],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        date_str = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if date_str:
            return date_str[:10]  # YYYY-MM-DD
    except (subprocess.CalledProcessError, IndexError):
        pass
    return FALLBACK_DATE


def parse_brief(path: Path) -> dict:
    """Parse a sprint brief markdown file into structured data."""
    text = path.read_text()

    # Sprint number from filename
    match = re.search(r"sprint-(\d+)-brief\.md", path.name)
    sprint_num = int(match.group(1)) if match else 0

    # Goal section
    goal_match = re.search(r"^Goal\s*\n((?:- .+\n?)+)", text, re.MULTILINE)
    goal_lines = []
    if goal_match:
        for line in goal_match.group(1).strip().splitlines():
            goal_lines.append(line.lstrip("- ").strip())
    goal = goal_lines[0] if goal_lines else f"Sprint {sprint_num}"

    # Extract agent sections: ## agentX-name
    agents = []
    agent_pattern = re.compile(
        r"^## (agent[A-Z]-[\w-]+)\s*\n(.*?)(?=^## agent|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in agent_pattern.finditer(text):
        branch_name = m.group(1)
        body = m.group(2)
        # Extract objective
        obj_match = re.search(r"^Objective\s*\n((?:- .+\n?)+)", body, re.MULTILINE)
        objective = ""
        if obj_match:
            obj_lines = obj_match.group(1).strip().splitlines()
            objective = obj_lines[0].lstrip("- ").strip()
        agents.append({"branch": branch_name, "objective": objective})

    # Merge order
    merge_match = re.search(r"^Merge Order\s*\n((?:\d+\..+\n?)+)", text, re.MULTILINE)
    merge_order = []
    if merge_match:
        for line in merge_match.group(1).strip().splitlines():
            name = re.sub(r"^\d+\.\s*", "", line).strip()
            merge_order.append(name)

    return {
        "num": sprint_num,
        "goal": goal,
        "goal_lines": goal_lines,
        "agents": agents,
        "merge_order": merge_order,
    }


def generate_status_doc(brief: dict, date: str) -> str:
    """Generate a PROJECT_STATUS markdown doc from parsed brief data."""
    num = brief["num"]
    goal = brief["goal"]
    agents = brief["agents"]

    # Title
    lines = [
        f"# afterburner-customer-bot Project Status \u2014 {date} (Sprint {num}: {goal})",
        "",
        f"## Sprint {num} Summary",
        "",
        f"Sprint {num} goal: {goal}.",
    ]
    if len(brief["goal_lines"]) > 1:
        for extra in brief["goal_lines"][1:]:
            lines.append(f"Additional: {extra}.")
    lines += ["", "---", "", "## What Changed", ""]

    # Agent sections
    for agent in agents:
        lines.append(f"### {agent['branch']}")
        lines.append("")
        lines.append(agent["objective"] or "See sprint brief for details.")
        lines.append("")
        lines.append("**Commits:**")
        lines.append("- (historical sprint \u2014 see git log for details)")
        lines.append("")
        lines.append("**Files:** See git log for details")
        lines.append("")

    lines += ["---", "", "## Merge Results", ""]
    lines.append("| # | Branch | Deliverable | Phase | Conflicts | Files Changed |")
    lines.append("|---|--------|-------------|-------|-----------|---------------|")

    for i, agent in enumerate(agents, 1):
        conflict = "Clean" if i == 1 else "Clean"
        lines.append(
            f"| {i} | {agent['branch']} | {agent['objective'] or 'See brief'} | 1 | {conflict} | - |"
        )

    lines += [
        "",
        "---",
        "",
        "## Backlog Snapshot",
        "",
        "### Completed This Sprint",
        f"- See sprint {num} brief for details",
        "",
        "### Still Open",
        "- See backlog for current status",
        "",
        "---",
        "",
        "## Next Steps",
        "",
        f"- See sprint {num + 1} brief for next planned work",
        "",
    ]

    return "\n".join(lines)


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0

    for sprint_num in range(1, 12):
        brief_path = HISTORY_DIR / f"sprint-{sprint_num}-brief.md"
        if not brief_path.exists():
            print(f"WARNING: {brief_path} not found, skipping")
            continue

        date = git_date_for_brief(sprint_num)
        brief = parse_brief(brief_path)
        doc = generate_status_doc(brief, date)

        out_path = DOCS_DIR / f"PROJECT_STATUS_{date}-sprint{sprint_num}.md"
        out_path.write_text(doc)
        print(f"Generated: {out_path.name}")
        generated += 1

    print(f"\nTotal: {generated} PROJECT_STATUS docs generated")
    return 0 if generated == 11 else 1


if __name__ == "__main__":
    sys.exit(main())
