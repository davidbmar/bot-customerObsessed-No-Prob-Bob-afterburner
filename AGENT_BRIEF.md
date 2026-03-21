agentB-docs-summary — Sprint 30

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 29: Input filter improvements, transcription discard button
- 700+ tests pass
- Bot has 70+ features, 29 sprints, zero open bugs
- Long conversations (39 msgs) are hard to follow — need summary
─────────────────────────────────────────

Sprint-Level Context

Goal
- Generate PROJECT_STATUS doc for Sprint 29
- Add conversation summary — show a brief AI-generated summary at the top of long conversations (F-070)
- Suppress ONNX console warnings to clean up browser console (B-029)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Generate PROJECT_STATUS doc for Sprint 29
- Add test for conversation summary feature

Tasks
1. **Generate PROJECT_STATUS doc**:
   - `docs/PROJECT_STATUS_2026-03-21-sprint29.md` — Sprint 29: Input filter, transcription discard
   - Follow PROJECT_STATUS_TEMPLATE.md format

2. **Add server-side conversation summary endpoint** (supports F-070):
   - Add `GET /api/conversations/{id}/summary` endpoint that returns a brief summary
   - For now, return the first user message as the summary (client can enhance later)
   - Response: `{"summary": "User asked about building a voice-enabled customer service bot", "message_count": 37}`

3. **Write tests**:
   - Test the summary endpoint returns valid JSON
   - Test it handles missing conversation IDs gracefully

4. **Update backlog** — Verify items marked Complete

Acceptance Criteria
- PROJECT_STATUS doc exists for Sprint 29
- `/api/conversations/{id}/summary` returns valid response
- All tests pass
