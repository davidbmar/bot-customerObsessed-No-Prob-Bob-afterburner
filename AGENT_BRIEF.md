agentA-provider-and-history — Sprint 17

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 16: e2e integration tests (discovery→seed doc pipeline proven), comprehensive README, CLI evaluate colors. 399 tests pass.
- Dashboard shows 11 sprints (Sprints 1-11 only) — Sprints 12-16 have no PROJECT_STATUS docs
- Health endpoint returns provider_label: "ollama" instead of "Qwen 3.5" — chat_ui.html header shows this wrong label
- Debug panel visible by default despite previous fix attempts — localStorage debug-panel state may override
- scripts/generate_sprint_history.py already exists and generates docs from sprint briefs
─────────────────────────────────────────

Sprint-Level Context

Goal
- Generate PROJECT_STATUS docs for Sprints 12-16 so dashboard shows all sprints (B-021)
- Fix provider label in health endpoint and header — should show "Qwen 3.5" not "ollama" (B-019)
- Fix debug panel defaulting to visible — should be hidden unless user opens it (B-022)
- Add typing indicator animation while bot is streaming (F-040)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/server.py, bot/llm.py, bot/gateway.py, scripts/, docs/PROJECT_STATUS_*, tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html


Objective
- Generate PROJECT_STATUS docs for Sprints 12-16, fix provider label in health endpoint

Tasks
1. **Generate PROJECT_STATUS docs for Sprints 12-16**:
   - Run `scripts/generate_sprint_history.py` or extend it to handle Sprints 12-16
   - Sprint briefs are in `.sprint/history/sprint-{12..16}-brief.md`
   - If briefs aren't archived yet, check SPRINT_BRIEF.md or git history
   - Each doc should follow the same format as Sprints 1-11 docs

2. **Fix provider label in health endpoint** (B-019):
   - In `bot/server.py`, the `/api/health` handler returns `provider_label`
   - Currently it returns the raw provider key ("ollama") instead of the display label from LLM_PROVIDERS
   - Fix: look up the active provider in LLM_PROVIDERS and return its `label` field (e.g., "Qwen 3.5")
   - Also fix the `/api/llm/providers` response to include an `active_label` field

3. **Write tests**:
   - Test health endpoint returns correct provider_label for each provider
   - Test PROJECT_STATUS docs exist for Sprints 12-16
   - Target: 410+ total tests

4. **Update backlog** — Mark B-019, B-021 as Complete (Sprint 17)

Acceptance Criteria
- `ls docs/PROJECT_STATUS_*.md | wc -l` returns 16
- `curl http://localhost:1203/api/health | jq .provider_label` returns "Qwen 3.5" (not "ollama")
- `.venv/bin/python3 -m pytest tests/ -v` — 410+ tests, 0 failures
