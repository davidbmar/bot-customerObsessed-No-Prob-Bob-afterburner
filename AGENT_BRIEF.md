agentB-button-tests — Sprint 25

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 24: VAD/barge-in settings panel, PROJECT_STATUS docs for Sprints 20-23, tool error handling
- 659 tests pass (+ 17 new Sprint 25 spec tests, 9 currently failing)
- Users need: stop generating during streaming, pause/resume in hands-free mode
- Test spec already written: tests/test_sprint25_button_states.py (9 failing = the spec)
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add Stop Generating button to cancel streaming responses mid-generation (F-064)
- Add Pause/Resume toggle for hands-free mode — Send button becomes ⏸/▶ (F-065)
- All 17 tests in tests/test_sprint25_button_states.py must pass

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns tests/ — agentB MUST NOT touch bot/chat_ui.html
- The test file tests/test_sprint25_button_states.py already exists and defines the spec — do NOT modify it


Objective
- Add additional integration tests to verify button behavior end-to-end
- Do NOT modify tests/test_sprint25_button_states.py — that is the spec
- Do NOT modify bot/chat_ui.html — that is agentA's territory

Tasks
1. **Add server-side streaming abort test**:
   - Test that the `/api/chat/stream` SSE endpoint handles client disconnection gracefully
   - Test that aborting mid-stream doesn't crash the server or leave zombie processes

2. **Add API test for concurrent requests**:
   - Test that sending a new message while streaming aborts the previous stream
   - Or test that the server handles overlapping requests cleanly

3. **Update backlog** — Verify F-064, F-065 marked Complete

Acceptance Criteria
- All existing + new tests pass
- `.venv/bin/python3 -m pytest tests/ -v` — all pass
