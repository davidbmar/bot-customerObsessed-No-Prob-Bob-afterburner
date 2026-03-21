agentA-tool-tests — Sprint 38

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
- Verify worktree .venv symlink works — agents should complete successfully (test B-051 fix)
- Add tests for the new read_project_doc and list_projects tools

Constraints
- agentA owns `tests/test_tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files


Objective
- Add tests for list_projects and read_project_doc tools

Tasks
- In `tests/test_tools.py`, add tests:
  - `test_tool_list_projects_returns_projects` — mock httpx.get to return project list, verify formatted output
  - `test_tool_list_projects_dashboard_offline` — mock httpx.get to raise ConnectError, verify error message
  - `test_tool_read_project_doc_reads_file` — create temp project dir with README.md, mock _find_project_root, verify file content returned
  - `test_tool_read_project_doc_blocks_traversal` — verify path traversal (../../etc/passwd) is blocked
  - `test_tool_read_project_doc_missing_file` — verify "File not found" for nonexistent path
  - `test_tool_registration_includes_list_projects` — verify list_projects is in TOOL_DEFINITIONS
  - `test_tool_registration_includes_read_project_doc` — verify read_project_doc is in TOOL_DEFINITIONS
- Run `.venv/bin/python3 -m pytest tests/ -x -q` to verify all tests pass

Acceptance Criteria
- All new tests pass
- All existing 726 tests still pass
- Total test count increases by 7+
