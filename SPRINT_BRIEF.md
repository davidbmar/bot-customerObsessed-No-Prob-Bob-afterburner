# Sprint 35

Goal
- Fix sprint-config.sh to use venv python so sprint-run.sh verification passes (B-048)
- Generate PROJECT_STATUS docs for Sprints 33-34 so dashboard shows all sprints (B-049)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `.sprint/scripts/` and `docs/` files
- No two agents may modify the same files

Merge Order
1. agentB-test-cmd-docs
2. agentA-ui-polish

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-ui-polish

Objective
- Minor UI polish: ensure the Active Project dropdown pre-selects the current active project correctly

Tasks
- In `bot/chat_ui.html`, when populating the Active Project dropdown from `/api/projects`, set the `selected` attribute on the option matching `active_project` from the response
- If no active project is set, default to the first project in the list
- After user selects a project and clicks "Save & Switch", the dropdown should reflect the new selection on next Settings open

Acceptance Criteria
- Active Project dropdown pre-selects the currently active project
- Changing active project persists across Settings panel opens
- No regressions in existing Settings panel behavior

## agentB-test-cmd-docs

Objective
- Fix DEFAULT_TEST_CMD to use venv python (B-048)
- Generate PROJECT_STATUS docs for Sprints 33-34 (B-049)

Tasks
- In `.sprint/scripts/sprint-config.sh`, change DEFAULT_TEST_CMD to:
  `cd ${ROOT_CFG} && .venv/bin/python3 -m pytest tests/ -x -q`
- Create `docs/PROJECT_STATUS_2026-03-21-sprint33.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 33 delivered: auto-rebuild after merge (F-074), Sprint 32 PROJECT_STATUS doc (B-047), Active Project dropdown fix attempt (F-075)
- Create `docs/PROJECT_STATUS_2026-03-21-sprint34.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 34 delivered: venv test command in sprint-config.sh (B-048 partial), Sprint 33 PROJECT_STATUS doc (B-049 partial), Active Project dropdown UI fix (F-075)
- Create a session doc for this sprint

Acceptance Criteria
- `.sprint/scripts/sprint-config.sh` DEFAULT_TEST_CMD uses `.venv/bin/python3 -m pytest`
- sprint-run.sh verification passes (no "No module named pytest")
- Both PROJECT_STATUS docs exist with correct summaries
- Dashboard shows Sprints 33-34 after rebuild
