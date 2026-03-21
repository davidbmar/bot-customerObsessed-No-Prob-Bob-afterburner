agentA-conversation-fixes — Sprint 22

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 21: favicon, localhost auth bypass, copy button on all messages, Escape key, voice waveform, send button paste fix
- 636 tests pass
- Conversation persistence broken: old conversations don't restore from sidebar, new conversations don't appear in sidebar
- Docs panel stats hardcoded, Active Project dropdown empty
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix conversation restore — clicking saved conversation shows only welcome message, not history (B-030)
- Fix new conversations not saving to sidebar (B-031, F-058)
- Update Docs panel stats from hardcoded "20 sprints" to dynamic counts (B-032)
- Fix Active Project dropdown empty in Settings (B-028)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/ — agentA MUST NOT touch these


Objective
- Fix conversation save/restore so switching between conversations works correctly
- Fix sidebar refresh so new conversations appear immediately

Tasks
1. **Fix saveConversation() to preserve markdown source** (B-030):
   - In `saveConversation()` (~line 2813), change how assistant message content is extracted
   - Currently: `var content = bodyEl ? bodyEl.textContent : ''` — this loses markdown
   - Fix: For assistant messages, prefer `bodyEl.dataset.markdown` (set at line 2041) over `textContent`
   - Updated line: `var content = bodyEl ? (bodyEl.dataset.markdown || bodyEl.textContent) : ''`
   - This preserves the original markdown for proper re-rendering on restore

2. **Fix sidebar refresh after conversation changes** (B-031, F-058):
   - In `newConversation()` (~line 2526): after `showWelcomeMessage()`, call `refreshConversationList()`
   - In `saveConversation()` (~line 2813): after successful save to localStorage, call `refreshConversationList()`
   - BUT: avoid infinite loops — `refreshConversationList` should not trigger `saveConversation`
   - Simple approach: add `refreshConversationList()` call at the end of `saveConversation()` (after the try/catch), and at the end of `newConversation()` (both success and catch paths)

3. **Update Docs panel stats** (B-032):
   - Find the hardcoded line "Built across 20 sprints · 631 tests · 57 features" in the Docs panel HTML (~search for "Built across")
   - Update to: "Built across 21 sprints · 636 tests · 59 features · 9 eval scenarios"
   - Or better: add `id="docsStats"` to the element so it can be updated dynamically later

4. **Update backlog** — Mark B-030, B-031, B-032 as Complete (Sprint 22)

Acceptance Criteria
- Create a new chat, send a message → conversation appears in sidebar immediately
- Switch away and back → conversation restores with all messages and formatting
- Bot messages show proper markdown (bold, italic, paragraphs) after restore
- Docs panel shows updated sprint/test/feature counts
