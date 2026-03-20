# Sprint 7

Goal
- Polish the web chat UI: debug panel showing real data, settings panel, better UX
- Add get_sprint_status tool for Afterburner integration

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- Single agent to avoid merge conflicts

Merge Order
1. agentA-webchat-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from bot.server import BotHTTPHandler; print('Server: OK')"
.venv/bin/python3 -c "from bot.tools import get_sprint_status; print('Tool: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -3
```

Previous Sprint
- Sprint 6 delivered: EvaluationRunner (3 scenarios passing), get_project_summary, add_to_backlog, FactExtractor, CLI evaluate — 87 tests pass
- Web chat UI exists at bot/chat_ui.html with basic chat bubbles and a debug panel skeleton (31 references to "debug" in HTML)
- /api/chat already returns: response, tools_called, principles_active, memory_count, input_tokens, output_tokens, duration_ms
- Missing: debug panel doesn't render the data, no settings panel, no way to switch personality or model from UI

## agentA-webchat-polish

Objective
- Make the web chat UI production-quality with working debug panel and settings

Tasks
1. Upgrade `bot/chat_ui.html` debug panel to actually display data from /api/chat responses:
   - After each bot response, show a collapsible debug section below the message
   - Display: personality name, active principles (as pills/badges), tools called (with arguments), input/output token counts, response latency in ms, extracted facts (from bot.facts)
   - Toggle button in header to show/hide all debug panels
   - Style: dark theme, monospace for technical data, accent color for highlights

2. Add settings panel to `bot/chat_ui.html`:
   - Slide-out panel or modal triggered by a gear icon in the chat header
   - Settings: personality name (dropdown populated from GET /api/personalities), model name (text input), Ollama URL (text input)
   - "New Conversation" button that clears chat and starts fresh conversation_id
   - "Clear History" button
   - Show current conversation_id

3. Add API endpoints to `bot/server.py`:
   - `GET /api/personalities` — lists available personalities from the personalities/ directory
   - `GET /api/config` — returns current bot config (model, ollama_url, personality)
   - `POST /api/config` — update config at runtime (switch personality, change model)
   - `POST /api/conversations/new` — create new conversation, return new conversation_id

4. Implement `get_sprint_status` in `bot/tools.py` (F-011):
   - Reads .agent-done-* files and SPRINT_BRIEF.md from a project
   - Returns: sprint number, agent count, agents done, agents running
   - Register as LLM tool

5. Improve chat UX in `bot/chat_ui.html`:
   - Auto-focus input after bot response
   - Show typing indicator while waiting for response
   - Markdown rendering in bot responses (bold, code, lists)
   - Timestamps on messages
   - Responsive layout for mobile

6. Write tests:
   - `tests/test_tools.py`: add test for get_sprint_status
   - Test the new API endpoints return correct JSON structure

7. Update backlog: mark F-007, F-010, F-011 as Complete (Sprint 7)

Acceptance Criteria
- Debug panel shows real data (principles, tokens, latency) after each bot response
- Settings panel opens, shows personality list, allows switching
- GET /api/personalities returns list of available personalities
- get_sprint_status tool works
- `.venv/bin/python3 -m pytest tests/ -v` — 90+ tests, 0 failures
- Chat UI looks polished with typing indicator, timestamps, markdown rendering
- Backlog updated
