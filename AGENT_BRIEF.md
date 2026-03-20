agentB-debug-panel-tools — Sprint 4

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 3: all 56 tests pass, save_discovery works, CLI chat/status commands work, e2e test proves conversation→seed doc pipeline
- Bot runs: personality loads (9 principles), gateway pipelines messages, memory persists, server starts on 1203
- Remaining roadmap items: evaluation framework, more tools, web chat polish
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add evaluation framework to test bot behavior against scenarios (F-005)
- Add web chat debug panel showing tools, principles, tokens, latency (F-010)
- Add more Afterburner tools: get_project_summary, add_to_backlog (F-003, F-012)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step)


Objective
- Add debug panel to web chat UI and more Afterburner integration tools

Tasks
- Update `bot/chat_ui.html` to add a collapsible debug panel:
  - Shows after each bot response (not always visible — toggle button)
  - Displays: active personality name, principles list, tools called (if any), input/output token count, response latency in ms
  - Dark themed, matches existing chat UI style
  - Data comes from the /api/chat response (which already returns tools_called, principles_active, input_tokens, output_tokens, duration_ms)
- Implement `get_project_summary` in `bot/tools.py` (F-003):
  - Reads a project's Vision, Plan, and Roadmap from `docs/lifecycle/`
  - Returns a structured summary (title, problem statement, current sprint status)
  - Register as LLM tool
- Implement `add_to_backlog` in `bot/tools.py` (F-012):
  - Appends a bug or feature entry to a project's `docs/project-memory/backlog/README.md`
  - Accepts: type (bug/feature), title, priority, description
  - Auto-assigns next ID (B-NNN or F-NNN)
  - Register as LLM tool
- Write tests for both new tools in `tests/test_tools.py`
- Update backlog: mark F-003, F-010, F-012 as Complete

Acceptance Criteria
- Web chat debug panel shows principles, tools, tokens after each response
- `from bot.tools import get_project_summary, add_to_backlog` works
- `.venv/bin/python3 -m pytest tests/test_tools.py -v` passes with new tool tests
- Backlog updated
