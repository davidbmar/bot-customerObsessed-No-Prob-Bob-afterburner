agentA-auto-rebuild-switch — Sprint 40

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
- Auto-rebuild dashboard data when a project has none — bot triggers rebuild on first query (F-080)
- Bot auto-switches active project when user asks about a different project (F-078)

Constraints
- agentA owns `bot/tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files


Objective
- Auto-rebuild when project has no dashboard data (F-080)
- Auto-switch active project on query (F-078)

Tasks
- In `bot/tools.py`, modify `tool_get_project_summary()`:
  - After calling `/api/project/{slug}/status`, if it returns 404 or empty data (latestSprint=0, totalSprints=0), auto-trigger a rebuild:
    ```python
    httpx.post(f"{DASHBOARD_URL}/api/rebuild-data",
               json={"projectRoot": str(project_root), "slug": slug},
               timeout=30.0)
    ```
  - Then retry the status API call
  - Log: "Auto-rebuilt dashboard data for {slug}"
- In `bot/tools.py`, modify `tool_get_project_summary()` and `tool_get_sprint_status()`:
  - After successfully returning data, if `_config` is available and `_config.active_project != slug`, auto-switch:
    ```python
    if _config and hasattr(_config, 'switch_project'):
        _config.switch_project(slug)
    ```
  - This way when user asks "status of grassyknoll", the active project switches to grassyknoll
- Add a test: `test_get_project_summary_triggers_rebuild` — mock status API to return empty first, then full data after rebuild call

Acceptance Criteria
- Asking about a project with no dashboard data auto-triggers rebuild
- Active project switches when user queries a different project
- All existing tests pass + 1 new test
