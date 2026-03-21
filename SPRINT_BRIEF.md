# Sprint 23

Goal
- Fix paragraph spacing in restored bot messages — old conversations saved as textContent lose line breaks (B-034)
- Add notification sound on bot response with toggle in settings (F-046)
- Add code block syntax highlighting in bot messages (F-059)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/ — agentA MUST NOT touch these

Merge Order
1. agentB-server-polish
2. agentA-chat-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 22: conversation persistence fixed (save markdown, sidebar refresh), /api/projects endpoint, Active Project dropdown wired, Docs stats updated
- 643 tests pass
- Hotfix: tool result format fixed for Claude API (B-033)
- Restored old conversations lose paragraph spacing (B-034)

## agentA-chat-polish

Objective
- Fix paragraph spacing in restored conversations
- Add notification sound toggle
- Add code syntax highlighting

Tasks
1. **Fix paragraph spacing in restored conversations** (B-034):
   - In `saveConversation()` (~line 2821), for assistant messages: already using `bodyEl.dataset.markdown || bodyEl.textContent`
   - The issue is that OLD conversations were saved with `textContent` which has no paragraph breaks
   - Add a one-time migration in `restoreConversation()` and `switchToConversation()`:
     - When loading messages from localStorage, if the content has no newlines but has patterns like `.A` or `?A` or `!A` (period/question/exclamation followed immediately by capital letter with no space), insert `\n\n` before the capital letter
   - This heuristic fixes "understand.So" → "understand.\n\nSo" and "else?I'm" → "else?\n\nI'm"
   - Apply the fix: `content = content.replace(/([.!?])([A-Z])/g, '$1\n\n$2')`
   - Only apply when content has NO existing newlines (old format), so new markdown content is untouched

2. **Add notification sound on bot response** (F-046):
   - Add a subtle notification sound when the bot finishes a response (not during streaming, only on completion)
   - Use the Web Audio API to generate a short, pleasant chime — no external audio files needed
   - Example: two short sine wave tones (440Hz then 554Hz, 80ms each) with quick fade
   - Add a toggle in the Settings panel: "Notification sound" checkbox, default OFF
   - Save preference in localStorage (`notifySound`)
   - Play sound in the streaming `done` event handler, only if `notifySound` is enabled and tab is not focused (`!document.hasFocus()`)
   - Do NOT play if TTS is about to speak (the voice IS the notification)

3. **Add code block syntax highlighting** (F-059):
   - In `renderMarkdownToDOM()`, when rendering `<pre><code>` blocks:
   - Add a lightweight syntax highlighter — not a full library, just basic token coloring:
     - Keywords (function, const, let, var, if, else, return, import, class, def, for, while, try, catch) → accent color
     - Strings (single/double quoted, backtick) → green
     - Comments (// and #) → muted color
     - Numbers → orange
   - Apply via CSS classes on `<span>` elements inside `<code>`
   - Add corresponding CSS rules using `var(--accent)` and other theme variables
   - Keep it simple — ~30 lines of JS, no external dependencies

4. **Update backlog** — Mark B-034, F-046, F-059 as Complete (Sprint 23)

Acceptance Criteria
- Old restored conversations show proper paragraph breaks (no "word.Next")
- Settings has "Notification sound" toggle
- Sound plays when bot responds (only when tab not focused, sound enabled, TTS not active)
- Code blocks in bot messages have colored keywords/strings/comments
- `.venv/bin/python3 -m pytest tests/ -v` — all pass

## agentB-server-polish

Objective
- Add server-side tests and polish

Tasks
1. **Add test for tool result formatting** (B-033 regression guard):
   - In `tests/`, add a test that verifies `ToolCall.id` is stored and that `_handle_tool_calls` formats messages correctly for both Anthropic (with id) and OpenAI (without id) cases
   - Mock the LLM response to return a ToolCall with `id="test-123"` and verify the messages list has the correct Anthropic format
   - Also test with `id=""` and verify the OpenAI format is used

2. **Test conversation new endpoint robustness**:
   - Test POST `/api/conversations/new` multiple times returns unique IDs
   - Test that conversation IDs follow expected format

3. **Update Docs panel sprint count** (via server):
   - Add a `/api/stats` endpoint that returns `{"sprints": N, "tests": N, "features": N}` by counting:
     - Sprints: count `docs/PROJECT_STATUS_*.md` files
     - Tests: run `pytest --co -q 2>/dev/null | tail -1` and parse count (or hardcode for now)
     - Features: count lines matching `| F-` in `docs/project-memory/backlog/README.md`
   - This lets the frontend Docs panel auto-update stats in a future sprint

4. **Update backlog** — Mark items as Complete (Sprint 23)

Acceptance Criteria
- Tool result format test passes for both Anthropic and OpenAI paths
- `/api/stats` returns valid JSON with sprint/test/feature counts
- All existing + new tests pass
