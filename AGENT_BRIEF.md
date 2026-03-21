agentA-scroll-shortcuts — Sprint 26

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 25: Stop generating button (F-064), Pause/Resume hands-free (F-065)
- 674 tests pass
- Bot UI is feature-rich: 68 features, voice, markdown, conversations, debug panel
- Long conversations hard to navigate — need scroll-to-bottom
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add scroll-to-bottom floating button for long conversations (F-066)
- Generate PROJECT_STATUS docs for Sprints 24-25 so dashboard stays current
- Add keyboard shortcuts help tooltip (F-068)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Add scroll-to-bottom floating action button
- Add keyboard shortcuts help

Tasks
1. **Scroll-to-bottom FAB** (F-066):
   - Add a floating button (↓ arrow) that appears when the user scrolls up in the messages area
   - Position: bottom-right of the messages container, above the input area
   - Show only when not at the bottom (use `scroll` event + check if `scrollTop + clientHeight < scrollHeight - 100`)
   - Click: smooth scroll to bottom
   - Style: circular, accent color, subtle shadow, small (36px), with transition
   - Auto-hide when user reaches the bottom
   - Also auto-hide during streaming (auto-scroll already handles this)

2. **Keyboard shortcuts help** (F-068):
   - Add a small "⌨" button in the header bar (near Debug/Docs) or as a section in the Docs panel
   - Shows a tooltip/modal listing shortcuts:
     - Enter — Send message
     - Escape — Stop speaking / Stop generating
     - Ctrl+N — New conversation (if not already bound)
   - Keep it simple — a small popover that appears on click

3. **Update backlog** — Mark F-066, F-068 as Complete (Sprint 26)

Acceptance Criteria
- Scroll up in a long conversation → ↓ button appears
- Click ↓ → smooth scroll to bottom, button disappears
- Keyboard shortcuts help is accessible from the UI
- `.venv/bin/python3 -m pytest tests/ -v` — all pass
