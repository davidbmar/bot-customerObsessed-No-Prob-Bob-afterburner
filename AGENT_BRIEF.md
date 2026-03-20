agentB-docs-and-polish — Sprint 16

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
