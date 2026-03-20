# Sprint 8 — Agent Notes

*Started: 2026-03-20 02:02 UTC*

Phase 1 Agents: 1
- agentA-multi-project-vision

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-multi-project-vision

*Completed: 2026-03-20 02:10 UTC*

### Files changed (9)
- `bot/config.py` — Added `projects` dict, `active_project`, `add_project()`, `switch_project()`, `list_projects()`, `active_project_root` property, `_auto_discover_projects()`, persistence in save/load
- `bot/tools.py` — Added `set_config()`, `_resolve_project_root()`, `generate_vision()`, `feedback_on_sprint()`, tool wrappers; made all tools use `_resolve_project_root` instead of hardcoded lookup
- `bot/gateway.py` — Added `config` parameter, wires up `set_config()` on init
- `bot/llm.py` — Added `generate_vision` and `feedback_on_sprint` to `TOOL_DEFINITIONS`
- `bot/server.py` — Added `GET /api/projects`, `POST /api/projects/switch` endpoints
- `bot/chat_ui.html` — Added project selector dropdown in settings panel
- `tests/test_config.py` — **New file**: 15 tests for multi-project config
- `tests/test_tools.py` — Added 14 tests for generate_vision and feedback_on_sprint
- `docs/project-memory/backlog/README.md` — Marked F-013, F-014, F-015 as Complete (Sprint 8)

### Commands run
- `python3 -m venv .venv && pip install deps`
- `pytest tests/ -v` — **129 tests, 0 failures** (up from 100)
- `git commit` + `git push -u origin HEAD`

### Notes / follow-on work
- The `_auto_discover_projects()` function reads from `~/.config/afterburner/registry.json` first, falling back to the dashboard `projects.json`. If neither exists, projects dict starts empty.
- `generate_vision` writes to `docs/lifecycle/VISION.md` (uppercase) per the brief. Existing `get_project_summary` reads from `Vision.md` (mixed case) — a future cleanup could normalize these.
- The project switch in the settings panel fires a separate fetch to `/api/projects/switch` before applying other settings. A more robust approach would chain these sequentially, but this works for the current UI.

