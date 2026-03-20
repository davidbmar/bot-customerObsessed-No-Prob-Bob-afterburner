agentA-e2e-integration — Sprint 16

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 15: 9 eval scenarios (was 3), delete/search conversations, dark/light theme toggle. 363 tests pass.
- save_discovery tool exists and API endpoint POST /api/tools/save_discovery exists (Sprint 13)
- But no automated test proves the full loop: chat → synthesis → save seed → file appears in target project
- README.md is minimal — no getting-started guide, no screenshots, no API reference
- Debug panel still shows by default on page load (B-013 open since Sprint 12)
- CLI evaluate command works but output is plain text with no color coding
─────────────────────────────────────────

Sprint-Level Context

Goal
- Prove the end-to-end value loop: discovery conversation → save seed doc → verify seed doc exists in an Afterburner project (F-039)
- Write a comprehensive README with getting-started guide, screenshots, and API reference (F-042)
- Fix debug panel showing by default on page load (B-013)
- Improve CLI evaluate output with pass/fail colors (F-043)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns tests/, bot/server.py, bot/gateway.py, bot/tools.py — agentB MUST NOT touch these
- agentB owns README.md, bot/chat_ui.html, evaluations/runner.py — agentA MUST NOT touch these


Objective
- Write integration tests proving the full discovery-to-seed-doc pipeline

Tasks
1. **End-to-end integration test** — Create `tests/test_e2e_pipeline.py`:
   - Test 1: Create a temporary project directory with `docs/seed/`
   - Test 2: Simulate 5 message exchanges through the Gateway (mock LLM responses)
   - Test 3: Call `save_discovery(project_root, conversation_summary)`
   - Test 4: Verify a seed doc file was created in `{project_root}/docs/seed/`
   - Test 5: Verify the seed doc contains the expected synthesis sections (Problem, Users, Use Cases)
   - Test 6: Test the `/api/tools/save_discovery` HTTP endpoint returns 200 and creates the file
   - Use `tempfile.mkdtemp()` for test project directories, clean up in teardown

2. **Fix save_discovery to handle missing project gracefully**:
   - If the target project doesn't exist or `docs/seed/` doesn't exist, create it
   - Return clear error message if project_root is invalid

3. **Write tests for edge cases**:
   - save_discovery with empty content
   - save_discovery with invalid project path
   - save_discovery when docs/seed/ doesn't exist (should create it)
   - Target: 380+ total tests

4. **Update backlog** — Mark F-039 as Complete (Sprint 16)

Acceptance Criteria
- `tests/test_e2e_pipeline.py` proves the full loop
- save_discovery creates `docs/seed/` if missing
- `.venv/bin/python3 -m pytest tests/ -v` — 380+ tests, 0 failures
