agentB-server-api — Sprint 22

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 21: favicon, localhost auth bypass, copy button on all messages, Escape key, voice waveform, send button paste fix
- 636 tests pass
- Conversation persistence broken: old conversations don't restore from sidebar, new conversations don't appear in sidebar
- Docs panel stats hardcoded, Active Project dropdown empty
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix conversation restore — clicking saved conversation shows only welcome message, not history (B-030)
- Fix new conversations not saving to sidebar (B-031, F-058)
- Update Docs panel stats from hardcoded "20 sprints" to dynamic counts (B-032)
- Fix Active Project dropdown empty in Settings (B-028)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/ — agentA MUST NOT touch these


Objective
- Fix Active Project dropdown to show available projects
- Write tests for conversation-related API endpoints

Tasks
1. **Fix Active Project dropdown** (B-028):
   - In `bot/server.py`, find how the `/api/health` or settings data is returned
   - Add a `/api/projects` endpoint (or extend health) that returns the list of available Afterburner projects
   - Read from `~/.config/afterburner/registry.json` if it exists, or return a single entry for the current project
   - Response format: `{"projects": [{"slug": "noprobbob", "name": "No Prob Bob"}]}`
   - The frontend (agentA's territory) already has the dropdown — it just needs data. agentA will wire it up.

2. **Write tests for API endpoints**:
   - Test GET `/api/projects` returns valid JSON with at least one project
   - Test GET `/api/health` returns 200 with expected fields
   - Test POST `/api/conversations/new` returns a valid conversation_id

3. **Update backlog** — Mark B-028, F-058 as Complete (Sprint 22)

Acceptance Criteria
- GET `/api/projects` returns JSON list of projects
- All existing + new tests pass
- `.venv/bin/python3 -m pytest tests/ -v` — all pass
