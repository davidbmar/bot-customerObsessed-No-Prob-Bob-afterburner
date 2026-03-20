agentB-chat-ux — Sprint 15

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 14: conversation sidebar, token count fix, provider label fix, cost display. 271 tests pass.
- Evaluation framework exists with 3 scenarios (surface-request, vague-requirements, pushback)
- Sidebar shows past conversations with first message preview, timestamp, message count
- Published to CloudFront: https://d3gb25yycyv0d9.cloudfront.net
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add more evaluation scenarios — expand from 3 to 8+ scenarios with diverse customer types (F-035)
- Delete conversation from sidebar — right-click or swipe to remove old chats (F-036)
- Search conversations — filter sidebar by keyword (F-037)
- Dark/light theme toggle (F-038)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- agentA owns evaluations/ and tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html


Objective
- Add conversation deletion, search, and theme toggle to web chat

Tasks
1. **Delete conversation** — Update `bot/chat_ui.html`:
   - Add a small "×" button on each conversation entry in the sidebar
   - Click "×" → confirm dialog "Delete this conversation?" → remove from localStorage
   - If deleting the active conversation, switch to a new empty chat
   - Also support long-press on mobile (or a "Delete" option in a context menu)

2. **Search conversations** — Update `bot/chat_ui.html`:
   - Add a search input at the top of the sidebar
   - Filter conversations by matching keyword against all message content
   - Show matching conversations with the matching text highlighted
   - Clear search restores full list

3. **Dark/light theme toggle** — Update `bot/chat_ui.html`:
   - Add a sun/moon icon button in the header (next to Debug button)
   - Light theme: white background, dark text, light blue bubbles
   - Dark theme: current colors (default)
   - Save preference to localStorage
   - Use CSS custom properties for all colors so the toggle just swaps a class

4. **Update backlog** — Mark F-036, F-037, F-038 as Complete (Sprint 15)

Acceptance Criteria
- Can delete a conversation from sidebar
- Typing in search filters conversations by content
- Sun/moon button toggles between dark and light themes
- Theme preference persists across page reloads
