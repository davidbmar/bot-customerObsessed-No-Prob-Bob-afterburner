agentB-telegram-tools — Sprint 2

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 1 delivered: personality framework with inheritance (9 principles), LLM client (OllamaClient), memory system (JSONL), web chat UI skeleton
- Merge conflicts between agents B and C left import mismatches: gateway.py references OllamaLLM but llm.py exports OllamaClient, config field names don't match between modules, server.py can't start
- Personality and memory work correctly in isolation
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix all critical merge bugs so the bot actually runs (B-001, B-002, B-003, B-004)
- Add Telegram transport + discovery tools (F-001, F-002)
- Deliver a working bot on both web chat AND Telegram

Constraints
- Use the project venv: .venv/bin/python3
- Ollama must be running for LLM calls (qwen3.5:latest)
- Agents run non-interactively — MUST NOT ask for confirmation
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v


Objective
- Add Telegram polling transport and the save_discovery tool

Tasks
- Implement `bot/polling.py` with a `TelegramPoller` class:
  - Uses httpx to poll Telegram Bot API (getUpdates long polling)
  - Configurable bot token via `BotConfig.telegram_token`
  - Routes incoming messages through the same Gateway as web chat
  - Sends responses back via sendMessage API
  - Handles /start command (welcome message with personality intro)
  - Non-blocking: runs in asyncio alongside the web server
  - Graceful shutdown on SIGINT
- Add `telegram_token` field to `bot/config.py` `BotConfig` (default: empty string, polling disabled when empty)
- Implement `bot/tools.py` with the `save_discovery` tool:
  - Receives structured discovery output (problem, users, use_cases, success_criteria)
  - Writes a seed document to a configurable Afterburner project path
  - Filename: `discovery-{timestamp}.md` in the project's `docs/seed/` directory
  - Markdown format matching Afterburner seed doc conventions
  - Register it as a tool the LLM can call (add to tool definitions in llm.py)
- Update `cli.py` to add `--telegram` flag to the `start` command that enables polling
- Write tests in `tests/test_tools.py`:
  - save_discovery writes correct markdown to the right path
  - Tool registration includes save_discovery
- Update backlog: mark F-001 and F-002 as "Complete (Sprint 2)"

Acceptance Criteria
- `from bot.polling import TelegramPoller` imports without error
- save_discovery tool writes a valid seed doc markdown file
- `.venv/bin/python3 -m pytest tests/test_tools.py -v` passes
- `python3 cli.py start --telegram` starts server + polling (exits cleanly if no token configured)
- Backlog updated
