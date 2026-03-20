agentB-cli-e2e — Sprint 3

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
