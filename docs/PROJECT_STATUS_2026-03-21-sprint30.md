# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 30: Conversation summary banner, ONNX warning suppression)

## Sprint 30 Summary

Sprint 30 added a conversation summary banner for long conversations (F-070) and suppressed ONNX runtime console warnings from Silero VAD initialization (B-029). agentA built the client-side summary banner UI and ONNX warning suppression in chat_ui.html. agentB generated the Sprint 29 PROJECT_STATUS doc and added a server-side conversation summary endpoint.

---

## What Changed

### agentB-docs-summary

Generated Sprint 29 PROJECT_STATUS doc. Added server-side `/api/conversations/{id}/summary` endpoint returning the first user message as a brief summary with message count. Added tests for the summary endpoint.

**Commits:**
- 3558695 agentB-docs-summary: implement sprint 30 tasks
- bfe64b2 feat: Sprint 29 PROJECT_STATUS doc, conversation summary endpoint (F-070)

**Files:** docs/PROJECT_STATUS_2026-03-21-sprint29.md, bot/server.py, tests/

### agentA-conv-summary

Added conversation summary banner (F-070) that shows a collapsible summary at the top of long conversations (>10 messages). Suppressed ONNX runtime warnings (B-029) by setting `ort.env.logSeverityLevel = 3` before VAD initialization.

**Commits:**
- e386a90 agentA-conv-summary: implement sprint 30 tasks
- 7683fd9 feat: add conversation summary banner (F-070) + suppress ONNX warnings (B-029)

**Files:** bot/chat_ui.html

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-docs-summary | Sprint 29 status doc, summary endpoint | 1 | Clean | 3+ |
| 2 | agentA-conv-summary | Conversation summary banner (F-070), ONNX fix (B-029) | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- F-070: Conversation summary banner for long conversations
- B-029: Console shows 10 ONNX runtime warnings on every page load

### Still Open
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-010: GitHub not configured in dashboard project entry
- B-015: Dashboard backlog counts show 0
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written

---

## Test Results

700+ tests passing.

---

## Next Steps

- Fix pause/play toggle to stop both TTS and VAD listening (B-039, B-040, F-071)
- Fix dashboard backlog showing 0 items (B-015)
