agentA-new-tool-tests — Sprint 39

Previous Sprint Summary
─────────────────────────────────────────
# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 37: Worktree venv symlink, sprint docs)

## Sprint 37 Summary

Sprint 37 attempted to implement worktree venv symlink support and generate sprint documentation. Both agents modified only their AGENT_BRIEF.md files without producing substantive code changes.

---

## What Changed

### agentA-worktree-venv

Attempted to implement worktree venv symlink support so agents in worktrees can use the project's Python virtual environment. Agent updated its brief but did not produce code changes.

**Commits:**
- d0d6b96 agentA-worktree-venv: implement sprint 37 tasks

**Files:** AGENT_BRIEF.md

### agentB-sprint-docs

Attempted to generate sprint documentation. Agent updated its brief but did not produce code changes.

**Commits:**
- e7d5d53 agentB-sprint-docs: implement sprint 37 tasks

**Files:** AGENT_BRIEF.md

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentA-worktree-venv | Worktree venv symlink attempt | 1 | Clean | 1 |
| 2 | agentB-sprint-docs | Sprint docs attempt | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- (No items resolved — agents had minimal output)

### Still Open
- B-010: GitHub not configured in dashboard project entry
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-046: Bot reports stale sprint data until rebuild runs
- B-048: sprint-config venv test issues
- F-075: Active Project dropdown improvements

---

## Next Steps

- Debug agent execution — Sprints 34-37 all had minimal output
- Consider agent environment fixes (venv, config) before retrying feature work
- Address stale data and config backlog items
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add tests for list_projects, read_project_doc, and the enriched get_project_summary tools
- Generate PROJECT_STATUS doc for Sprint 38

Constraints
- agentA owns `tests/test_tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files


Objective
- Add comprehensive tests for list_projects, read_project_doc, and the enriched get_project_summary

Tasks
- In `tests/test_tools.py`, import `tool_list_projects` and `tool_read_project_doc` from `bot.tools`
- Add these tests:
  1. `test_tool_list_projects_returns_formatted_list` — mock httpx.get to return project data, verify "Registered projects:" header and project entries in output
  2. `test_tool_list_projects_dashboard_offline` — mock httpx.get to raise ConnectError, verify "Dashboard unavailable" message
  3. `test_tool_read_project_doc_reads_readme` — create tmp dir with README.md, mock `_find_project_root` to return it, call `tool_read_project_doc(slug="test", path="README.md")`, verify content
  4. `test_tool_read_project_doc_blocks_path_traversal` — call with `path="../../etc/passwd"`, verify "Cannot read files outside" message
  5. `test_tool_read_project_doc_missing_file` — call with `path="nonexistent.md"`, verify "File not found" message
  6. `test_tool_read_project_doc_missing_project` — call with unknown slug, verify "not found" message
  7. `test_tool_registration_includes_list_projects` — verify "list_projects" in TOOL_DEFINITIONS names
  8. `test_tool_registration_includes_read_project_doc` — verify "read_project_doc" in TOOL_DEFINITIONS names
  9. `test_execute_tool_dispatches_list_projects` — verify execute_tool routes correctly
  10. `test_get_project_summary_includes_sprint_data` — mock httpx.get for status API, verify sprint data included in output
- Run `.venv/bin/python3 -m pytest tests/test_tools.py -v` to verify

Acceptance Criteria
- All 10 new tests pass
- All existing tests still pass
- Test count increases from 726 to 736+
