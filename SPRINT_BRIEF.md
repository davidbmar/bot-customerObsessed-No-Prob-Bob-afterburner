# Sprint 18

Goal
- Fix debug panel CSS so it's truly hidden by default — the CSS must start it as hidden, not rely on JS (B-022)
- Collapse sidebar by default on first visit — only show when user clicks hamburger (B-023)
- Detect system color preference with prefers-color-scheme media query (B-024)
- Add conversation title editing — click title in sidebar to rename (F-041)
- Generate PROJECT_STATUS doc for Sprint 17 so dashboard stays current

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent — all changes are in interconnected UI files

Merge Order
1. agentA-final-polish

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
ls docs/PROJECT_STATUS_*.md | wc -l
```

Previous Sprint
- Sprint 17: provider label fix, PROJECT_STATUS docs for 12-16, typing dots animation. 445 tests pass.
- Debug panel still visible on fresh page load (even after localStorage.clear()) — CSS default is wrong
- Sidebar shows on desktop by default — takes up space before user has conversations to browse
- Light theme defaults regardless of system preference
- 16 PROJECT_STATUS docs — Sprint 17 is missing
- Conversation title editing (F-041) is the last open feature

## agentA-final-polish

Objective
- Fix all first-use experience issues and add conversation title editing

Tasks
1. **Fix debug panel CSS default** (B-022):
   - The debug panel container in chat_ui.html must have `display: none` in its CSS by default
   - The "Debug" button click should toggle it to `display: block`
   - Do NOT rely on JavaScript or localStorage to hide it initially — the CSS must hide it
   - On page load, if localStorage says debug was open, JS sets `display: block`
   - This way, even without JS, the panel is hidden

2. **Collapse sidebar by default** (B-023):
   - Sidebar container should start with `display: none` or `transform: translateX(-100%)`
   - Hamburger (☰) click toggles it open
   - Once opened, save preference to localStorage
   - On subsequent visits, respect the saved preference

3. **System color preference** (B-024):
   - Add `@media (prefers-color-scheme: dark)` in CSS
   - If no localStorage theme preference, use the system preference
   - If localStorage has a saved preference, use that instead
   - This means: first visit on macOS dark mode → dark theme; first visit on light mode → light theme

4. **Conversation title editing** (F-041):
   - In sidebar, clicking the conversation title text makes it editable (contenteditable or input)
   - Press Enter or blur saves the new title to localStorage
   - Default title remains the truncated first message

5. **Generate PROJECT_STATUS for Sprint 17**:
   - Run or extend `scripts/generate_sprint_history.py` to include Sprint 17
   - Verify with `ls docs/PROJECT_STATUS_*.md | wc -l` → 17

6. **Write tests**:
   - Test debug panel default hidden state
   - Test sidebar default collapsed state
   - Test title editing saves to localStorage
   - Target: 455+ total tests

7. **Update backlog** — Mark B-022, B-023, B-024, F-041 as Complete (Sprint 18)

Acceptance Criteria
- Clear localStorage, reload → debug panel hidden, sidebar collapsed
- System in dark mode → dark theme on first visit
- Click conversation title → editable, saves on Enter
- `ls docs/PROJECT_STATUS_*.md | wc -l` returns 17
- `.venv/bin/python3 -m pytest tests/ -v` — 455+ tests, 0 failures
