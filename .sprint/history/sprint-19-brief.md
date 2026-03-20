# Sprint 19

Goal
- Render markdown in bot messages — bold, italic, code blocks, lists, headers (F-044)
- Export full conversation as structured seed doc with Problem/Users/Use Cases sections (F-047)
- Group message timestamps by date — "Today", "Yesterday", "Mar 19" (F-045)
- Generate PROJECT_STATUS doc for Sprint 18

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/server.py, bot/gateway.py, bot/tools.py, scripts/, docs/PROJECT_STATUS_*, tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html

Merge Order
1. agentA-export-and-history
2. agentB-markdown-and-dates

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
ls docs/PROJECT_STATUS_*.md | wc -l
```

Previous Sprint
- Sprint 18: debug panel CSS fix, sidebar collapse, system theme detection, conversation title editing. 470 tests pass.
- Bot messages render as plain text — no markdown formatting even when the LLM outputs **bold** or `code`
- save_discovery writes raw text — no structured format with Problem/Users/Use Cases sections
- All timestamps show "HH:MM AM" with no date grouping — older messages have no date context
- 17 PROJECT_STATUS docs (Sprint 18 missing)

## agentA-export-and-history

Objective
- Improve seed doc export with structured sections, generate Sprint 18 PROJECT_STATUS

Tasks
1. **Structured seed doc export** (F-047):
   - Update `bot/tools.py` `save_discovery()` to accept an optional `structured=True` parameter
   - When structured=True, format the output as:
     ```markdown
     # Discovery: [first user message truncated]
     Date: YYYY-MM-DD
     Provider: [active provider]
     Messages: [count]

     ## Problem
     [extracted from conversation]

     ## Users
     [extracted from conversation]

     ## Use Cases
     [extracted from conversation]

     ## Success Criteria
     [extracted from conversation]

     ## Raw Conversation
     [full message history]
     ```
   - Use the gateway's synthesis logic to extract sections (reuse the auto-synthesis prompt)
   - Update `/api/tools/save_discovery` endpoint to pass `structured=True`

2. **Generate PROJECT_STATUS for Sprint 18**:
   - Run or extend `scripts/generate_sprint_history.py`
   - Verify: `ls docs/PROJECT_STATUS_*.md | wc -l` → 18

3. **Write tests**:
   - Test structured seed doc format
   - Test save_discovery with structured=True creates proper sections
   - Target: 485+ total tests

4. **Update backlog** — Mark F-047 as Complete (Sprint 19)

Acceptance Criteria
- save_discovery with structured=True produces a doc with Problem/Users/Use Cases/Success Criteria sections
- `ls docs/PROJECT_STATUS_*.md | wc -l` returns 18
- `.venv/bin/python3 -m pytest tests/ -v` — 485+ tests, 0 failures

## agentB-markdown-and-dates

Objective
- Render markdown in bot messages, add date grouping to timestamps

Tasks
1. **Markdown rendering** (F-044):
   - Bot messages should render markdown: **bold**, *italic*, `inline code`, ```code blocks```, - lists, ## headers
   - Use a lightweight markdown-to-HTML converter — either:
     - A simple regex-based converter (no dependency) for basic markdown
     - Or include a small inline markdown library (marked.js minified is ~30KB)
   - Apply to bot message content before inserting into DOM
   - User messages remain plain text (they're the user's input, not markdown)
   - Code blocks should have a dark background and monospace font
   - Sanitize HTML output to prevent XSS (no raw HTML passthrough)

2. **Date grouping** (F-045):
   - Before each message group from a different date, show a date separator
   - Format: "Today", "Yesterday", or "Mon, Mar 19" for older dates
   - Separator is a centered line with the date text (like chat apps)
   - Apply to both restored conversations (from localStorage) and new messages
   - CSS: `text-align: center; color: #888; font-size: 0.8em; margin: 1em 0;`

3. **Update backlog** — Mark F-044, F-045 as Complete (Sprint 19)

Acceptance Criteria
- Bot message with "**bold** and `code`" renders with bold text and inline code styling
- Code blocks render with dark background and monospace font
- Messages from different dates show date separators
- User messages remain plain text (no markdown rendering)
