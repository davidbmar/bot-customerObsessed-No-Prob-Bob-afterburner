# Sprint 36

Goal
- Generate PROJECT_STATUS docs for Sprints 33-35 so dashboard is complete (B-049)
- Add "list all projects" capability to bot tools so users can ask "what projects are there?" (F-076)

Constraints
- agentA owns `bot/tools.py` and `bot/llm.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files

Merge Order
1. agentB-sprint-docs
2. agentA-list-projects

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-list-projects

Objective
- Add a `list_projects` tool the bot can call when users ask "what projects are there?" (F-076)

Tasks
- In `bot/tools.py`, add a `tool_list_projects()` function that calls `list_project_slugs()` (already exists) and returns a formatted list with slug + name for each project
- In `bot/llm.py`, add `list_projects` to the `TOOL_DEFINITIONS` array with description "List all registered Afterburner projects"
- In `bot/tools.py`, add `list_projects` to the `execute_tool` dispatch dict
- Add tests in `tests/test_tools.py`:
  - Test that `tool_list_projects()` returns formatted project list when dashboard is available
  - Test that `tool_list_projects()` returns error message when dashboard is unavailable
  - Test that `list_projects` is in `TOOL_DEFINITIONS`

Acceptance Criteria
- User asks "what projects are there?" and bot calls list_projects tool
- Tool returns formatted list of all registered projects with slugs and names
- All existing + new tests pass

## agentB-sprint-docs

Objective
- Generate PROJECT_STATUS docs for Sprints 33, 34, and 35 (B-049)

Tasks
- Create `docs/PROJECT_STATUS_2026-03-21-sprint33.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 33 delivered: auto-rebuild after sprint merge (F-074), Sprint 32 PROJECT_STATUS doc (B-047), Active Project dropdown UI fix (F-075)
  - Agents: agentA-project-dropdown, agentB-auto-rebuild
  - Use git log between commits `5b702b4` and `deeea3f` for details
- Create `docs/PROJECT_STATUS_2026-03-21-sprint34.md`
  - Sprint 34 delivered: sprint-config venv test (B-048 partial), Active Project dropdown fix attempt
  - Agents: agentA-project-fix, agentB-config-docs
  - Use git log between commits `37e3950` and `f68fb2b` for details
- Create `docs/PROJECT_STATUS_2026-03-21-sprint35.md`
  - Sprint 35 delivered: UI polish attempt (agents had minimal output)
  - Agents: agentA-ui-polish, agentB-test-cmd-docs
  - Use git log between commits `d47b78c` and `71e3c0a` for details
- Create a session doc for this sprint

Acceptance Criteria
- All three PROJECT_STATUS docs exist with correct summaries
- Dashboard shows Sprints 33-35 after rebuild (35 total sprints)
- Docs follow PROJECT_STATUS_TEMPLATE format with merge table
