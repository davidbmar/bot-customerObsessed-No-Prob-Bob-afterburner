# Sprint 22 — Agent Notes

*Started: 2026-03-21 17:25 UTC*

Phase 1 Agents: 2
- agentA-conversation-fixes
- agentB-server-api

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-conversation-fixes

*Completed: 2026-03-21 17:27 UTC*

**Files changed:**
- `bot/chat_ui.html` — 3 fixes (markdown preservation, sidebar refresh, docs stats)
- `docs/project-memory/backlog/README.md` — marked B-030, B-031, B-032, F-058 as Complete

**Commands run:**
- `git pull origin main` — already up to date
- `python3 -m pytest tests/ -v` — 636 passed
- `git commit` + `git push -u origin HEAD`

**Notes / follow-on work:**
- B-028 (Active Project dropdown empty in Settings) is assigned to agentB per the constraints
- The docs stats line is still hardcoded HTML; a future enhancement could fetch counts dynamically (the brief suggested adding `id="docsStats"` — skipped as optional to keep changes scoped)


---

## agentB-server-api

*Completed: 2026-03-21 17:28 UTC*

### Files changed
- **bot/server.py** — Pass `config=cfg` to Gateway in `main()`; update `_handle_get_projects` to return `[{"slug": "...", "name": "..."}]` objects
- **tests/test_sprint22_api.py** — New file: 7 integration tests for `/api/projects`, `/api/health`, `POST /api/conversations/new`
- **docs/project-memory/backlog/README.md** — Marked B-028 and F-058 as Complete (Sprint 22)
- **docs/project-memory/sessions/S-2026-03-21-1727-sprint22-server-api.md** — Session doc

### Commands run
- `git pull origin main` — already up to date
- `pytest tests/test_sprint22_api.py -v` — 7 passed
- `pytest tests/ -v` — 643 passed
- `git push -u origin HEAD` — pushed to `agentB-server-api`

### Notes / follow-on work
- Project display names are derived from slugs (`slug.replace("-", " ").title()`). If the registry adds a `name` field in the future, the endpoint should prefer that.
- agentA still needs to wire the frontend dropdown to call `GET /api/projects` and use the `{slug, name}` objects.

