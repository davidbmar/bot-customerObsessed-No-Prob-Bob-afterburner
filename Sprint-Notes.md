# Sprint 2 — Agent Notes

*Started: 2026-03-20 00:02 UTC*

Phase 1 Agents: 2
- agentA-fix-imports
- agentB-telegram-tools

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentB-telegram-tools

*Completed: 2026-03-20 00:07 UTC*

## Files changed

| File | Change |
|------|--------|
| `bot/gateway.py` | Fixed imports: `OllamaLLM` → `OllamaClient`, `Personality` → `PersonalityLoader` |
| `bot/polling.py` | Added `/start` command with welcome message |
| `bot/tools.py` | `save_discovery` now writes `discovery-{timestamp}.md` instead of fixed filename |
| `cli.py` | Added `--telegram` flag, wires up `TelegramPoller` in `cmd_start` |
| `tests/test_tools.py` | **New** — 7 tests for save_discovery and tool registration |
| `tests/test_llm_webchat.py` | Fixed 5 broken tests from Sprint 1 merge (model name, API field names) |
| `docs/project-memory/backlog/README.md` | Marked B-001 Fixed, F-001/F-002 Complete |
| `docs/project-memory/sessions/S-2026-03-20-0006-telegram-tools.md` | Session doc |

## Commands run

- `python3 -m venv .venv` + `pip install httpx pytest pyyaml`
- `.venv/bin/python3 -m pytest tests/ -v` — **51 passed, 0 failed**
- `git push -u origin HEAD`

## Notes / follow-on work

- **B-002** (config field naming) may still need attention — the default model in `BotConfig` is `qwen3:4b` while `llm.py` defaults to `qwen3.5:latest`. Currently gateway uses config defaults.
- **B-003** (server.py cascading import error) is now fixed by the gateway import fix.
- **B-004** (pytest not in venv) — recreated venv with pytest installed. The `.venv` is gitignored so other agents may need to recreate it.
- Telegram polling requires a valid `telegram.botToken` in config — without it, `--telegram` prints a warning and continues with web-only mode.


---

## agentA-fix-imports

*Completed: 2026-03-20 00:07 UTC*

## Files changed
- `bot/gateway.py` — Fixed imports (`OllamaLLM` → `OllamaClient`, `Personality` → `PersonalityLoader`), added `ChatMemory` wrapper + `_get_memory()`, default model `qwen3.5:latest`
- `bot/config.py` — Added `model_name` and `personality_name` properties
- `bot/server.py` — `chat_id` → `conversation_id`, `principles` → `principles_active`, added `create_app()` factory
- `bot/__main__.py` — New entry point for `python3 -m bot`
- `docs/project-memory/backlog/README.md` — Marked B-001–B-004 as Fixed
- `docs/project-memory/sessions/S-2026-03-20-0007-fix-imports.md` — Session doc

## Commands run
- `.venv/bin/pip install pytest httpx pyyaml` (created venv first)
- `.venv/bin/python3 -m pytest tests/ -v` — **44 passed**
- Import smoke tests: `from bot.gateway import Gateway`, `from bot.server import create_app` — both OK
- Server start test on port 1203: GET / → 200, POST /api/chat → returns JSON, GET /api/health → OK
- `git push -u origin HEAD`

## Notes / follow-on work
- The `create_app()` function was added since the acceptance criteria required `from bot.server import create_app` to work, but server.py only had `start_server()`
- `bot/__main__.py` was created so `python3 -m bot` can start the server (the old `python3 bot/server.py` doesn't work with relative imports)

