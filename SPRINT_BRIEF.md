# Sprint 30

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

Merge Order
1. agentB-docs-summary
2. agentA-conv-summary

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 29: Input filter improvements, transcription discard button
- 700+ tests pass
- Bot has 70+ features, 29 sprints, zero open bugs
- Long conversations (39 msgs) are hard to follow — need summary

## agentA-conv-summary

Objective
- Add conversation summary banner for long conversations
- Suppress ONNX console warnings

Tasks
1. **Conversation summary banner** (F-070):
   - When a conversation has > 10 messages, show a collapsible summary banner at the top of the chat
   - The summary is generated client-side by extracting the first user message and the bot's synthesis (if any)
   - Format: "📋 Summary: [first user question] — [key topics discussed]"
   - Clicking expands to show more detail
   - Collapsed by default, subtle styling (muted background, small text)
   - Update when new messages are added

2. **Suppress ONNX warnings** (B-029):
   - The Silero VAD ONNX runtime logs 10 warnings on every page load
   - These come from the ONNX WebAssembly runtime, not our code
   - Suppress by setting `ort.env.logLevel = 'error'` before loading the VAD model
   - Or wrap the VAD initialization in a console.warn override that filters ONNX messages
   - The simplest approach: before creating the VAD, set `ort.env.logSeverityLevel = 3` (error only)

3. **Update backlog** — Mark F-070, B-029 as Complete (Sprint 30)

Acceptance Criteria
- Long conversations show a summary banner at the top
- No ONNX warnings in browser console
- All tests pass

## agentB-docs-summary

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
