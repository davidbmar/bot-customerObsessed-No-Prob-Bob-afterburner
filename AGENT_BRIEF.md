agentA-export-and-history — Sprint 19

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 18: debug panel CSS fix, sidebar collapse, system theme detection, conversation title editing. 470 tests pass.
- Bot messages render as plain text — no markdown formatting even when the LLM outputs **bold** or `code`
- save_discovery writes raw text — no structured format with Problem/Users/Use Cases sections
- All timestamps show "HH:MM AM" with no date grouping — older messages have no date context
- 17 PROJECT_STATUS docs (Sprint 18 missing)
─────────────────────────────────────────

Sprint-Level Context

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
