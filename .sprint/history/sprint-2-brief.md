# Sprint 2

Goal
- Fix all critical merge bugs so the bot actually runs (B-001, B-002, B-003, B-004)
- Add Telegram transport + discovery tools (F-001, F-002)
- Deliver a working bot on both web chat AND Telegram

Constraints
- Use the project venv: .venv/bin/python3
- Ollama must be running for LLM calls (qwen3.5:latest)
- Agents run non-interactively — MUST NOT ask for confirmation
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v

Merge Order
1. agentA-fix-imports
2. agentB-telegram-tools

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from bot.personality import PersonalityLoader; p = PersonalityLoader('personalities'); pd = p.load('customer-discovery'); print('Personality:', pd.name, len(pd.principles), 'principles')"
.venv/bin/python3 -c "from bot.gateway import Gateway; print('Gateway: OK')"
.venv/bin/python3 -c "from bot.server import create_app; print('Server: OK')"
.venv/bin/python3 -c "from bot.memory import ConversationMemory; print('Memory: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 1 delivered: personality framework with inheritance (9 principles), LLM client (OllamaClient), memory system (JSONL), web chat UI skeleton
- Merge conflicts between agents B and C left import mismatches: gateway.py references OllamaLLM but llm.py exports OllamaClient, config field names don't match between modules, server.py can't start
- Personality and memory work correctly in isolation

## agentA-fix-imports

Objective
- Fix all import and API mismatches so the bot starts and the full pipeline works end-to-end

Tasks
- Fix `bot/gateway.py`: change `from .llm import OllamaLLM` to match the actual class name exported by `bot/llm.py` (which is `OllamaClient`). Also fix any other import references (like `LLMResponse`, `TOOL_DEFINITIONS`) — check what `llm.py` actually exports and align gateway.py's imports
- Fix `bot/config.py`: ensure `BotConfig` has all fields that other modules expect: `model_name`, `ollama_url`, `personality_name`, `data_dir`. Check what `gateway.py`, `server.py`, and `llm.py` reference and add any missing fields with sensible defaults
- Fix `bot/server.py`: ensure it imports correctly from gateway, config, personality. Test that `from bot.server import create_app` works. The server must start on port 1203 and serve the chat UI at GET /
- Install pytest in venv: `.venv/bin/pip install pytest` (B-004)
- Run ALL existing tests and fix any failures: `.venv/bin/python3 -m pytest tests/ -v`
- Test the full pipeline manually: personality loads → gateway creates → server starts → POST /api/chat returns response structure (even if Ollama isn't running, should return error JSON not crash)
- Update backlog: mark B-001, B-002, B-003, B-004 as Fixed

Acceptance Criteria
- `from bot.gateway import Gateway` works without errors
- `from bot.server import create_app` works without errors
- `.venv/bin/python3 -m pytest tests/ -v` passes all tests
- `python3 bot/server.py` starts on port 1203 (test with curl)
- Backlog updated

## agentB-telegram-tools

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
