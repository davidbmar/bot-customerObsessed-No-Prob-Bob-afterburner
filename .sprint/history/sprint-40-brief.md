# Sprint 40

Goal
- Auto-rebuild dashboard data when a project has none — bot triggers rebuild on first query (F-080)
- Bot auto-switches active project when user asks about a different project (F-078)

Constraints
- agentA owns `bot/tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files

Merge Order
1. agentB-sprint-docs
2. agentA-auto-rebuild-switch

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-auto-rebuild-switch

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

## agentB-sprint-docs

Objective
- Generate PROJECT_STATUS docs for Sprints 38-39

Tasks
- Create `docs/PROJECT_STATUS_2026-03-21-sprint38.md`:
  - Sprint 38 verified worktree .venv symlink fix — agents ran and tests passed
  - Agents: agentA-tool-tests, agentB-session-doc
- Create `docs/PROJECT_STATUS_2026-03-21-sprint39.md`:
  - Sprint 39 attempted tool tests — agents produced minimal output
  - Agents: agentA-new-tool-tests, agentB-sprint38-doc
- Create session doc for Sprint 40

Acceptance Criteria
- Both PROJECT_STATUS docs exist
- Dashboard shows 39 sprints after rebuild
