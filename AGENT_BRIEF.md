agentA-synthesis-and-fixes — Sprint 13

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 12: SSE streaming, conversation persistence (localStorage), error handling, PROJECT_STATUS docs for Sprints 1-11. 209 tests pass.
- Streaming works but total latency increased to ~39s (was 22s). Token count may be inflated (1378 out for 20 words).
- `python3 bot/server.py` broken — relative import error, must use `python3 -m bot.server`
- Conversation persists across page reloads via localStorage
- Dashboard shows 11 sprints, 9 sessions, 276 keywords
- Published to CloudFront: https://d3gb25yycyv0d9.cloudfront.net
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix server direct-run regression so `python3 bot/server.py` works again (B-017)
- Add "Save as Seed Doc" button in web chat that calls save_discovery tool from the UI (F-033)
- Add auto-synthesis: after 5+ exchanges, bot generates Problem/Users/Use Cases/Success Criteria summary (F-034)
- Auto-scroll chat to bottom on new messages and streaming (F-031)
- Mobile-responsive web chat with viewport meta and responsive CSS (F-027)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- agentA owns bot/ and tests/ — agentB MUST NOT touch these directories
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html


Objective
- Fix server direct-run, add save_discovery UI integration, add auto-synthesis

Tasks
1. **Fix `python3 bot/server.py` direct run** (B-017):
   - The fallback import block in server.py line 23-26 catches ImportError for relative imports and tries absolute imports
   - But gateway.py also uses relative imports internally, causing a chain failure
   - Fix: add `__main__.py` to bot/ that does `from bot.server import main; main()` OR fix all imports to work both ways
   - Simplest fix: ensure `bot/__main__.py` exists and works, and fix server.py to handle both cases

2. **Save as Seed Doc API endpoint** — Add `POST /api/tools/save_discovery` to `bot/server.py`:
   - Accepts: `{project_slug, conversation_id}`
   - Reads conversation history for that conversation_id
   - Calls `save_discovery(slug, content)` tool with a formatted summary of the conversation
   - Returns: `{ok: true, path: "docs/seed/discovery-YYYY-MM-DD.md"}`
   - This bridges the web chat UI to the Afterburner pipeline

3. **Auto-synthesis after 5+ exchanges** — Update `bot/gateway.py`:
   - Track exchange count per conversation (count user messages)
   - After the 5th user message, append to the system prompt: "You have had enough exchanges. In your next response, synthesize the conversation into a structured summary with sections: Problem, Users, Use Cases, Success Criteria. Present this as a formatted summary."
   - This triggers the bot's discovery synthesis behavior
   - Add a `synthesis_triggered` flag to prevent re-triggering

4. **Write tests**:
   - Test server direct-run imports work
   - Test save_discovery API endpoint
   - Test synthesis triggers after 5 exchanges
   - Target: 220+ total tests

5. **Update backlog** — Mark B-017, F-033, F-034 as Complete (Sprint 13)

Acceptance Criteria
- `python3 bot/server.py` starts without import errors
- After 5+ message exchanges, bot produces a structured summary
- POST /api/tools/save_discovery writes a seed doc to the target project
- `.venv/bin/python3 -m pytest tests/ -v` — 220+ tests, 0 failures
