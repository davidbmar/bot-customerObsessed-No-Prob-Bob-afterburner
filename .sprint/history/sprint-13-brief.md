# Sprint 13

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

Merge Order
1. agentA-synthesis-and-fixes
2. agentB-ui-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 bot/server.py &
sleep 2
curl -sf http://localhost:1203/api/health | python3 -c "import json,sys; print(json.load(sys.stdin))"
kill %1 2>/dev/null
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 12: SSE streaming, conversation persistence (localStorage), error handling, PROJECT_STATUS docs for Sprints 1-11. 209 tests pass.
- Streaming works but total latency increased to ~39s (was 22s). Token count may be inflated (1378 out for 20 words).
- `python3 bot/server.py` broken — relative import error, must use `python3 -m bot.server`
- Conversation persists across page reloads via localStorage
- Dashboard shows 11 sprints, 9 sessions, 276 keywords
- Published to CloudFront: https://d3gb25yycyv0d9.cloudfront.net

## agentA-synthesis-and-fixes

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

## agentB-ui-polish

Objective
- Add auto-scroll, "Save as Seed" button, mobile responsive CSS

Tasks
1. **Auto-scroll** — Update `bot/chat_ui.html`:
   - After appending any message (user, bot, or streaming chunk), scroll chat container to bottom
   - Use `element.scrollTop = element.scrollHeight` after DOM update
   - Also scroll on initial page load after restoring conversation from localStorage

2. **"Save as Seed Doc" button** — Update `bot/chat_ui.html`:
   - Add a button in the chat header or below the last bot message: "Save as Seed Doc"
   - Button only appears after 3+ exchanges (meaningful conversation)
   - On click: POST to `/api/tools/save_discovery` with current conversation_id and active project slug
   - Show success toast: "Saved seed doc to [project]" or error message
   - Button text changes to "Saved ✓" after successful save

3. **Mobile responsive** — Update `bot/chat_ui.html`:
   - Add `<meta name="viewport" content="width=device-width, initial-scale=1">` to head
   - Debug panel: hidden by default on mobile (screen width < 768px), shown via toggle
   - Settings panel: full-width overlay on mobile instead of side panel
   - Chat input: full width, larger touch targets for Send button
   - Provider cards in settings: stack vertically on mobile
   - Message bubbles: max-width 95% on mobile (currently ~80%)

4. **Update backlog** — Mark F-031, F-027 as Complete (Sprint 13)

Acceptance Criteria
- Chat auto-scrolls when new messages arrive
- "Save as Seed Doc" button appears after 3+ exchanges
- On mobile viewport (375px wide), chat is usable with no horizontal scroll
- Debug panel hidden by default on mobile
