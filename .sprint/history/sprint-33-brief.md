# Sprint 33

Goal
- Auto-rebuild dashboard data after sprint merges so bot always returns current sprint info (F-074, B-046)
- Generate PROJECT_STATUS doc for Sprint 32 and fix Active Project dropdown (B-047, B-045, F-075)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `.sprint/scripts/` and `docs/` files
- No two agents may modify the same files

Merge Order
1. agentB-auto-rebuild
2. agentA-project-dropdown

Merge Verification
- python3 -m pytest tests/ -x -q

## agentA-project-dropdown

Objective
- Fix the empty Active Project dropdown in Settings panel (B-045, F-075)

Tasks
- In `bot/chat_ui.html`, find the Active Project combobox in the Settings panel
- On Settings panel open, fetch project list from `/api/projects` (the bot server proxies or the dashboard serves this)
- Populate the dropdown with project slugs and names from the response
- Pre-select the currently active project
- When the user selects a different project, send a POST to update the active project in the bot config
- If only one project is registered, still show it (don't hide the dropdown)

Acceptance Criteria
- Settings panel Active Project dropdown shows all registered Afterburner projects
- Selecting a different project updates the active project for tool calls
- Dropdown is populated on every Settings panel open (not cached stale)

## agentB-auto-rebuild

Objective
- Add auto-rebuild to sprint-run.sh so dashboard data is always current (F-074)
- Generate PROJECT_STATUS for Sprint 32 (B-047)

Tasks
- In `.sprint/scripts/sprint-run.sh`, after the merge+push step, add a curl call to rebuild dashboard data:
  ```bash
  curl -sf -X POST http://localhost:1201/api/rebuild-data \
    -H 'Content-Type: application/json' \
    -d "{\"projectRoot\":\"$PROJECT_ROOT\",\"slug\":\"$PROJECT_SLUG\"}" || true
  ```
- Place the rebuild call right after `git push` in the merge phase
- Also add it after manual merge completion (the fallback path)
- Create `docs/PROJECT_STATUS_2026-03-21-sprint32.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 32 delivered: ONNX warning suppression (B-044), PROJECT_STATUS docs for Sprints 30-31 (B-043/F-073), sprint-run.sh zsh fix (B-008)
  - Use git log for commit details
- Create a session doc for this sprint

Acceptance Criteria
- `sprint-run.sh` calls `/api/rebuild-data` after merge+push
- `docs/PROJECT_STATUS_2026-03-21-sprint32.md` exists with correct summary
- Dashboard shows Sprint 32 after rebuild
- Rebuild failure (dashboard offline) doesn't break sprint-run.sh (|| true)
