agentB-server-polish — Sprint 23

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 22: conversation persistence fixed (save markdown, sidebar refresh), /api/projects endpoint, Active Project dropdown wired, Docs stats updated
- 643 tests pass
- Hotfix: tool result format fixed for Claude API (B-033)
- Restored old conversations lose paragraph spacing (B-034)
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix paragraph spacing in restored bot messages — old conversations saved as textContent lose line breaks (B-034)
- Add notification sound on bot response with toggle in settings (F-046)
- Add code block syntax highlighting in bot messages (F-059)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/ — agentA MUST NOT touch these


Objective
- Add server-side tests and polish

Tasks
1. **Add test for tool result formatting** (B-033 regression guard):
   - In `tests/`, add a test that verifies `ToolCall.id` is stored and that `_handle_tool_calls` formats messages correctly for both Anthropic (with id) and OpenAI (without id) cases
   - Mock the LLM response to return a ToolCall with `id="test-123"` and verify the messages list has the correct Anthropic format
   - Also test with `id=""` and verify the OpenAI format is used

2. **Test conversation new endpoint robustness**:
   - Test POST `/api/conversations/new` multiple times returns unique IDs
   - Test that conversation IDs follow expected format

3. **Update Docs panel sprint count** (via server):
   - Add a `/api/stats` endpoint that returns `{"sprints": N, "tests": N, "features": N}` by counting:
     - Sprints: count `docs/PROJECT_STATUS_*.md` files
     - Tests: run `pytest --co -q 2>/dev/null | tail -1` and parse count (or hardcode for now)
     - Features: count lines matching `| F-` in `docs/project-memory/backlog/README.md`
   - This lets the frontend Docs panel auto-update stats in a future sprint

4. **Update backlog** — Mark items as Complete (Sprint 23)

Acceptance Criteria
- Tool result format test passes for both Anthropic and OpenAI paths
- `/api/stats` returns valid JSON with sprint/test/feature counts
- All existing + new tests pass
