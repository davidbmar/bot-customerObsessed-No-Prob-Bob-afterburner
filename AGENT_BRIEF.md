agentA-fix-tools-tests — Sprint 3

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 2 fixed critical import bugs (B-001 to B-004), added Telegram polling (F-001), added save_discovery tool structure
- 50 of 51 tests pass — one test uses wrong field name (chat_id vs conversation_id)
- save_discovery exists in tools.py but isn't properly exported/importable
- Personality (9 principles), Gateway, Server, Memory, LLM client all work
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix remaining bugs (B-006, B-007) so all tests pass and save_discovery works
- Add end-to-end test proving conversation → seed doc pipeline (F-004)
- Add CLI chat and status commands (F-008, F-009)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation


Objective
- Fix save_discovery export and the failing test so all 51 tests pass

Tasks
- Fix `bot/tools.py`: ensure `save_discovery` is a properly importable function. Check the current file — it may define the function under a different name or inside a class. Make `from bot.tools import save_discovery` work
- Fix `tests/test_llm_webchat.py` test `test_api_chat_uses_chat_id`: the server uses `conversation_id` not `chat_id`. Either update the test to check for `conversation_id`, or update the server to also accept `chat_id` as an alias
- Run full test suite: `.venv/bin/python3 -m pytest tests/ -v` — all tests must pass
- If any other test failures are found, fix them
- Update backlog: mark B-006 and B-007 as Fixed

Acceptance Criteria
- `from bot.tools import save_discovery` works
- `.venv/bin/python3 -m pytest tests/ -v` — all tests pass, 0 failures
- Backlog updated
