# Sprint 16

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

Merge Order
1. agentA-e2e-integration
2. agentB-docs-and-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
cat README.md | head -5
```

Previous Sprint
- Sprint 15: 9 eval scenarios (was 3), delete/search conversations, dark/light theme toggle. 363 tests pass.
- save_discovery tool exists and API endpoint POST /api/tools/save_discovery exists (Sprint 13)
- But no automated test proves the full loop: chat → synthesis → save seed → file appears in target project
- README.md is minimal — no getting-started guide, no screenshots, no API reference
- Debug panel still shows by default on page load (B-013 open since Sprint 12)
- CLI evaluate command works but output is plain text with no color coding

## agentA-e2e-integration

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

## agentB-docs-and-polish

Objective
- Write comprehensive README, fix debug panel, improve evaluate CLI output

Tasks
1. **README.md** — Rewrite `README.md` with:
   - Project name and one-line description
   - Feature list with what's built (38 features across 15 sprints)
   - Quick start: clone, install, run, open web chat
   - Architecture overview (gateway pattern, personality framework, memory)
   - API reference: all HTTP endpoints (`/api/chat`, `/api/chat/stream`, `/api/tools/save_discovery`, `/api/llm/providers`, etc.)
   - Configuration: config file location, environment variables, personality docs
   - Evaluation: how to run scenarios, add new scenarios
   - Screenshots section (reference the existing screenshots or describe what to see)
   - Tech stack summary
   - Contributing guide (how to run tests, commit conventions)

2. **Fix debug panel default** (B-013) — Update `bot/chat_ui.html`:
   - On page load, debug panel should be hidden (collapsed)
   - Only show when user clicks "Debug" button
   - Check if there's a CSS class or JS state that controls initial visibility
   - Save debug panel state to localStorage so it remembers user preference

3. **CLI evaluate colors** (F-043) — Update `evaluations/runner.py`:
   - Use ANSI colors in terminal output: green for pass, red for fail, yellow for warnings
   - Show summary: "6/9 scenarios passed" with colored status per scenario
   - Show which principles were tested and whether they held
   - Add `--verbose` flag for detailed output, default is summary

4. **Update backlog** — Mark F-042, F-043, B-013 as Complete (Sprint 16)

Acceptance Criteria
- README.md has Quick Start, API Reference, Architecture sections
- Debug panel hidden on page load, toggled via button, state persisted
- `afterburner-bot evaluate` shows colored pass/fail output
