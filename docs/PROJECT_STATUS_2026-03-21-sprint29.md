# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 29: Input filter improvements, transcription discard button)

## Sprint 29 Summary

Sprint 29 improved the input quality filter to catch TV/movie background audio (B-038) and added a voice transcription discard button (F-069). agentA built the discard button UI with countdown timer and preview in the input field. agentB improved the input filter with longer audio duration thresholds, multi-sentence detection, and dialogue pattern matching for background media.

---

## What Changed

### agentA-discard-button

Added voice transcription discard button (F-069). Voice transcription now shows text as preview in the input field with a 3-second countdown timer and discard (X) button instead of auto-sending immediately. User can edit, confirm with Enter, or discard with Escape. Garbled transcriptions shown with yellow warning border.

**Commits:**
- 5b32cfb feat: add voice transcription discard button (F-069)
- 05d8faa agentA-discard-button: implement sprint 29 tasks

**Files:** bot/chat_ui.html

### agentB-filter-docs

Improved input quality filter to catch background media audio (B-038). Added longer audio duration thresholds, multi-sentence detection, and dialogue pattern matching so TV/movie audio is filtered before reaching the LLM.

**Commits:**
- 1604f79 agentB-filter-docs: implement sprint 29 tasks
- f1ffb0e feat: improve input filter to catch background media audio (B-038)

**Files:** bot/input_filter.py, tests/test_input_filter.py

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-filter-docs | Input filter improvements (B-038) | 1 | Clean | 2 |
| 2 | agentA-discard-button | Voice transcription discard button (F-069) | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- B-038: Input filter lets TV/movie audio through
- F-069: Voice transcription discard button

### Still Open
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-010: GitHub not configured in dashboard project entry
- B-015: Dashboard backlog counts show 0
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written
- B-029: Console shows 10 ONNX runtime warnings on every page load

---

## Test Results

700+ tests passing.

---

## Next Steps

- Add conversation summary banner for long conversations (F-070)
- Suppress ONNX console warnings (B-029)
