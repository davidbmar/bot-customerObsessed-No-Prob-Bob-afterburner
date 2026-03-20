agentA-fix-imports — Sprint 2

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
