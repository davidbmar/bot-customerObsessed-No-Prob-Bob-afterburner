# Sprint 3

Goal
- Fix remaining bugs (B-006, B-007) so all tests pass and save_discovery works
- Add end-to-end test proving conversation → seed doc pipeline (F-004)
- Add CLI chat and status commands (F-008, F-009)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation

Merge Order
1. agentA-fix-tools-tests
2. agentB-cli-e2e

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from bot.tools import save_discovery; print('save_discovery: OK')"
.venv/bin/python3 -c "from bot.gateway import Gateway; print('Gateway: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 2 fixed critical import bugs (B-001 to B-004), added Telegram polling (F-001), added save_discovery tool structure
- 50 of 51 tests pass — one test uses wrong field name (chat_id vs conversation_id)
- save_discovery exists in tools.py but isn't properly exported/importable
- Personality (9 principles), Gateway, Server, Memory, LLM client all work

## agentA-fix-tools-tests

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

## agentB-cli-e2e

Objective
- Add CLI chat/status commands and an end-to-end integration test

Tasks
- Add `chat` subcommand to `cli.py`: interactive terminal loop that reads user input, sends to Gateway, prints bot response. Uses readline for input. Type `exit` or Ctrl+D to quit. Shows personality name on startup
- Add `status` subcommand to `cli.py`: prints bot status — is server running (check port 1203)? which personality is loaded? how many conversations exist? Ollama reachable?
- Write `tests/test_e2e.py` — end-to-end test that:
  - Creates a temporary project directory with `docs/seed/`
  - Initializes Gateway with customer-discovery personality
  - Sends a sequence of discovery messages (simulating a customer conversation)
  - Verifies the gateway returns responses (doesn't need Ollama — mock the LLM response)
  - Calls save_discovery with structured output
  - Verifies a seed doc markdown file was written to the temp project's `docs/seed/`
  - Verifies the seed doc contains expected sections (Problem, Users, Use Cases, Success Criteria)
- Update backlog: mark F-004, F-008, F-009 as Complete

Acceptance Criteria
- `python3 cli.py chat` starts interactive loop (exits on EOF)
- `python3 cli.py status` prints status info without crashing
- `.venv/bin/python3 -m pytest tests/test_e2e.py -v` passes
- Backlog updated
