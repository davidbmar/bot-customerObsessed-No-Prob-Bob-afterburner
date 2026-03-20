# Sprint 10

Goal
- UX polish from live testing: welcome message, debug panel default hidden, new conversation button, better loading state
- Fix server entry point so it can run directly

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent to avoid merge conflicts

Merge Order
1. agentA-ux-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -3
```

Previous Sprint
- Sprint 9: fixed CLI crash, added conversation export and personality hot-reload — 144 tests pass
- Live Playwright test: bot works end-to-end, responds with customer discovery principles
- UX issues found: empty chat on load (no welcome), debug panel always visible, no new conversation button in header, "Thinking..." is too simple for 20s waits

## agentA-ux-polish

Objective
- Fix all UX issues found during live testing

Tasks
1. Welcome message (F-018):
   - When chat UI loads, show an initial bot message: "Hi! I'm the Customer Discovery Agent. Tell me about what you're building or a problem you're trying to solve, and I'll help you understand it deeply."
   - Style it as a bot message with timestamp
   - Don't save to conversation memory — it's just UI decoration

2. Debug panel default hidden (F-019):
   - On page load, debug panel should be collapsed/hidden
   - Debug button toggles it open/closed
   - When visible, it slides in from the right
   - Remember preference in localStorage

3. New Conversation button (F-020):
   - Add a "+" or "New Chat" button in the chat header next to the settings gear
   - Clicking it clears the chat messages, generates a new conversation_id, shows welcome message again
   - Keep it simple — no confirmation dialog needed

4. Better loading indicator (F-021):
   - Replace "Thinking..." with an animated typing indicator (three dots bouncing)
   - Add elapsed time counter that updates every second: "Thinking... (5s)"
   - If response takes >30s, show "Still thinking — local models can take a moment..."

5. Server entry point (F-022):
   - Add `bot/__main__.py` that calls the server start function
   - `python3 -m bot` should start the server on port 1203
   - Also make `python3 bot/server.py` work by adding `if __name__` block that handles relative imports

6. Update backlog: mark F-018 through F-022 as Complete (Sprint 10)

Acceptance Criteria
- Chat UI shows welcome message on load
- Debug panel hidden by default, toggleable
- New Chat button in header works
- Loading shows animated dots + elapsed time
- `python3 -m bot` starts the server
- `.venv/bin/python3 -m pytest tests/ -v` — 144+ tests, 0 failures
- Backlog updated
