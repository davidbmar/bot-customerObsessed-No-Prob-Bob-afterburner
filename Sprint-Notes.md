# Sprint 12 — Agent Notes

*Started: 2026-03-20 05:54 UTC*

Phase 1 Agents: 2
- agentA-streaming-and-polish
- agentB-sprint-history

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentB-sprint-history

*Completed: 2026-03-20 05:59 UTC*

### Files changed
- **`bot/llm.py`** — Added `LLM_PROVIDERS` dict, `OpenAICompatibleClient`, `AnthropicClient`, `get_client()` factory, `_openai_tools_to_anthropic()` converter. Kept `OllamaClient` for backward compatibility.
- **`bot/llm_config.py`** (new) — Per-provider config persistence with `load_provider_config()`, `save_provider_config()`, `get_active_provider()`, `set_active_provider()`.
- **`bot/gateway.py`** — Added `switch_provider()` method, `provider_id` tracking, updated `health_check()` to include provider info.
- **`bot/server.py`** — Added 4 endpoints: `GET /api/llm/providers`, `POST /api/llm/switch`, `GET /api/llm/config`, `POST /api/llm/config`.
- **`bot/chat_ui.html`** — Provider cards grid, model dropdown, API key field, base URL field, Test Connection button, dynamic header updates.
- **`tests/test_llm.py`** (new) — 39 new tests covering providers, factory, clients, config persistence, gateway switching, server endpoints, and UI.

### Commands run
- `.venv/bin/pip install anthropic openai pyyaml` 
- `.venv/bin/python3 -m pytest tests/ -v` — **183 tests passed** (target: 155+)
- `git push -u origin HEAD`

### Notes / follow-on work
- `OllamaClient` (native Ollama `/api/chat` endpoint) is preserved for backward compat. The new `OpenAICompatibleClient` uses Ollama's `/v1` OpenAI-compatible endpoint instead.
- API keys are stored in `~/.config/afterburner-bots/llm-providers.json` with env var fallback (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
- The Test Connection button currently uses `/api/health` which tests the *active* provider — a more targeted per-provider test could be added later.


---

## agentA-streaming-and-polish

*Completed: 2026-03-20 06:01 UTC*

```
---

## Summary

### Files Changed
- **`bot/gateway.py`** — Added `process_message_stream()` generator method that yields `{"type": "token", "content": ...}` dicts, with fallback for LLM clients without `chat_stream()`
- **`bot/server.py`** — Added `POST /api/chat/stream` SSE endpoint and `_classify_llm_error()` helper (503 for unreachable, 401 for bad API key)
- **`bot/chat_ui.html`** — SSE streaming client with `fetch()` + `ReadableStream` reader, conversation persistence via `localStorage`, error messages with red-tinted bubbles and retry button
- **`tests/test_streaming.py`** — 26 new tests covering gateway streaming, error classification, SSE endpoint routing, and UI elements
- **`docs/project-memory/backlog/README.md`** — F-025, F-028, F-029 marked Complete (Sprint 12)

### Commands Run
- `git pull origin main` — synced with main
- `python3 -m pytest tests/ -v` — **209 tests passed, 0 failures**
- `git commit` — committed all changes
- `git push -u origin HEAD` — **blocked by GitHub push protection** (pre-existing secret in commit `f2ff413`, not from this branch)

### Notes / Follow-on Work
- **Push blocked**: GitHub Secret Scanning blocks the push due to an Anthropic API key in `.env` at commit `f2ff413` (predates this branch — it's in `main`'s history). The repo owner needs to either:
  1. Allow the secret via the unblock URL GitHub provided, or
  2. Rewrite history to remove the secret from commit `f2ff413`
- **AnthropicClient streaming**: The gateway falls back to non-streaming for `AnthropicClient` since it has no `chat_stream()`. Adding `chat_stream()` to `AnthropicClient` using `client.messages.stream()` would be a good Sprint 13 task.
- **F-026 (Enter to send)**: Already works — `onkeydown` handler on the textarea handles Enter. The backlog item may be stale.
```

