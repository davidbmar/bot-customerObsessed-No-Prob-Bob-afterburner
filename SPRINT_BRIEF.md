# Sprint 12

Goal
- Wire up streaming responses via SSE so users see text as it generates (F-025)
- Generate PROJECT_STATUS docs for Sprints 1-11 so dashboard shows sprint history (F-024, B-014)
- Add conversation persistence across page reloads (F-028)
- Add error handling when LLM is unreachable (F-029)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- chat_stream() already exists in bot/llm.py — wire it through gateway and server, don't rewrite
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- PROJECT_STATUS docs must follow the template in docs/project-memory/tools/PROJECT_STATUS_TEMPLATE.md
- agentA owns bot/ and tests/ — agentB MUST NOT touch these directories
- agentB owns scripts/ and docs/ — agentA MUST NOT touch these directories

Merge Order
1. agentB-sprint-history
2. agentA-streaming-and-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from bot.gateway import Gateway; print('Gateway: OK')"
.venv/bin/python3 -c "from bot.server import BotHTTPHandler; print('Server: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
ls docs/PROJECT_STATUS_*.md | wc -l
```

Previous Sprint
- Sprint 11: multi-provider LLM (Ollama + Claude + ChatGPT) with runtime switching from settings panel. 183 tests pass.
- chat_stream() exists in bot/llm.py (OllamaClient line 316) but gateway.py uses non-streaming chat() (line 108)
- AnthropicClient also has chat() but no streaming variant yet
- Web chat has Enter-to-send (chat_ui.html line 586), welcome message, debug panel toggle, progress indicator
- No PROJECT_STATUS docs exist for any sprint — dashboard shows 0 sprints
- 11 sprint briefs archived in .sprint/history/

## agentA-streaming-and-polish

Objective
- Wire streaming through gateway and server, add conversation persistence and error handling

Tasks
1. **SSE streaming endpoint** — Add `POST /api/chat/stream` to `bot/server.py`:
   - Returns `text/event-stream` content type
   - Gateway calls `chat_stream()` instead of `chat()` when streaming
   - Yields SSE events: `data: {"type": "token", "content": "word"}` for each chunk
   - Final event: `data: {"type": "done", "response": "full text", "tools_called": [...], "principles_active": [...], "tokens": {...}, "duration_ms": N}`
   - Keep existing `POST /api/chat` working (non-streaming fallback)

2. **Gateway streaming support** — Add `process_message_stream()` to `bot/gateway.py`:
   - Same logic as `process_message()` but yields chunks from `llm.chat_stream()`
   - After streaming completes, run fact extraction and memory update (same as non-streaming path)
   - For AnthropicClient: if no `chat_stream()` method, fall back to non-streaming and yield the full response as one chunk

3. **Web chat SSE client** — Update `bot/chat_ui.html`:
   - `sendMessage()` uses `fetch()` with streaming reader on `/api/chat/stream`
   - Show bot message bubble immediately, append text as chunks arrive
   - Update debug panel with final event data (tools, principles, tokens, latency)
   - Progress indicator shows "Streaming..." instead of "Thinking..." when streaming
   - Fall back to `/api/chat` if stream endpoint fails

4. **Conversation persistence** — Update `bot/chat_ui.html`:
   - On each message exchange, save conversation to `localStorage` keyed by conversation ID
   - On page load, check localStorage for existing conversation and restore messages
   - "New Chat" button clears localStorage for current conversation
   - Store: `{conversationId, messages: [{role, content, timestamp}], provider, model}`

5. **Error handling** — Update `bot/chat_ui.html` and `bot/server.py`:
   - Server: catch `ConnectionError`, `httpx.ConnectError`, timeout in chat endpoints → return `{"error": "LLM unreachable", "detail": "..."}` with 503 status
   - UI: on error response, show red-tinted message bubble: "Could not reach [provider]. Check that Ollama is running / API key is valid."
   - UI: add retry button on error messages
   - Server: catch `anthropic.AuthenticationError` → return `{"error": "Invalid API key", "detail": "..."}` with 401 status

6. **Write tests** in `tests/test_server_api.py` and `tests/test_llm.py`:
   - Test SSE endpoint returns proper event-stream content type
   - Test SSE endpoint yields token events then done event
   - Test error handling returns 503 when LLM unreachable
   - Test error handling returns 401 for bad API key
   - Target: 200+ total tests

7. **Update backlog** — Mark F-025, F-028, F-029 as Complete (Sprint 12)

Acceptance Criteria
- Open web chat, send message → text streams in word-by-word (not all-at-once after 20s)
- Refresh page → conversation is restored from localStorage
- Stop Ollama, send message → red error bubble with retry button
- `.venv/bin/python3 -m pytest tests/ -v` — 200+ tests, 0 failures

## agentB-sprint-history

Objective
- Generate PROJECT_STATUS docs for Sprints 1-11 so the dashboard shows sprint history

Tasks
1. **Create `scripts/generate_sprint_history.py`**:
   - Read each `.sprint/history/sprint-{N}-brief.md` for N=1..11
   - Read the PROJECT_STATUS template from `docs/project-memory/tools/PROJECT_STATUS_TEMPLATE.md`
   - For each sprint, generate a `docs/PROJECT_STATUS_YYYY-MM-DD-sprintN.md` with:
     - Sprint number, date (from git log of the brief archive commit)
     - Goal (from brief)
     - Agent list and objectives (from brief)
     - Merge table with "Clean" status (all sprints merged successfully)
     - Status: Complete
   - Use git log dates: `git log --format=%aI --diff-filter=A -- .sprint/history/sprint-N-brief.md`
   - If git log returns no date, use 2026-03-19 as fallback

2. **Run the script** to generate all 11 docs:
   ```bash
   .venv/bin/python3 scripts/generate_sprint_history.py
   ```

3. **Verify**: `ls docs/PROJECT_STATUS_*.md | wc -l` should return 11

4. **Update backlog** — Mark F-024 and B-014 as Complete (Sprint 12)

Acceptance Criteria
- `ls docs/PROJECT_STATUS_*.md | wc -l` returns 11
- Each doc follows PROJECT_STATUS_TEMPLATE.md format
- Each doc has correct sprint number, goal, and agent list from the brief
- Merge table uses format: `| # | Branch | Deliverable | Phase | Conflicts |`
