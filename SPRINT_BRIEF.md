# Sprint 34

Goal
- Fix Active Project dropdown to show registered projects (B-045)
- Fix sprint-config.sh to use venv python for test verification (B-048)
- Generate PROJECT_STATUS doc for Sprint 33 (B-049)

Constraints
- agentA owns `bot/chat_ui.html` and `bot/config.py` exclusively
- agentB owns `.sprint/scripts/` and `docs/` files
- No two agents may modify the same files

Merge Order
1. agentB-config-docs
2. agentA-project-fix

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-project-fix

Objective
- Fix Active Project dropdown to correctly discover and display registered projects (B-045)

Tasks
- In `bot/config.py`, fix `_auto_discover_projects()` to handle the `projects.json` format which is `{"projects": [...], "activeProject": "slug"}` — currently expects a plain list
- The function should extract the `projects` array from the dict, then iterate over entries extracting `slug` and `rootPath`
- Also try the dashboard API at `http://127.0.0.1:1201/api/projects` as a discovery source — the dashboard is usually running
- In `bot/chat_ui.html`, ensure the Active Project dropdown fetches from the bot server's `/api/projects` endpoint on Settings panel open
- If projects are found, populate the dropdown with `{slug}: {name}` entries
- Pre-select the active project

Acceptance Criteria
- Settings panel Active Project dropdown shows registered Afterburner projects (not "No projects registered")
- Bot config correctly discovers projects from dashboard projects.json or API
- Existing tests pass

## agentB-config-docs

Objective
- Fix DEFAULT_TEST_CMD to use venv python (B-048)
- Generate Sprint 33 PROJECT_STATUS doc (B-049)

Tasks
- In `.sprint/scripts/sprint-config.sh`, change `DEFAULT_TEST_CMD` to use `.venv/bin/python3 -m pytest tests/ -x -q` instead of the system python3 personality check
- Create `docs/PROJECT_STATUS_2026-03-21-sprint33.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 33 delivered: auto-rebuild after merge (F-074), Sprint 32 PROJECT_STATUS doc (B-047), Active Project dropdown fix attempt (B-045/F-075)
  - Use git log for commit details
- Create a session doc for this sprint

Acceptance Criteria
- `.sprint/scripts/sprint-config.sh` DEFAULT_TEST_CMD uses `.venv/bin/python3`
- sprint-run.sh verification passes on macOS (no "No module named pytest" error)
- `docs/PROJECT_STATUS_2026-03-21-sprint33.md` exists with correct summary
- Dashboard shows Sprint 33 after rebuild
