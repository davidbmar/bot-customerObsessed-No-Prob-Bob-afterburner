agentA-pause-play — Sprint 31

Previous Sprint Summary
─────────────────────────────────────────
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
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix the broken pause/play hands-free behavior so Pause stops BOTH speaking AND listening (B-039, B-040, F-071)
- Fix dashboard backlog showing 0 items by correcting the backlog file path in build-sprint-data.sh (B-015)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `scripts/build-sprint-data.sh` in the afterburner repo AND `bot/tools.py` in this repo
- No two agents may modify the same files


Objective
- Fix Pause/Play toggle so it stops BOTH TTS and VAD listening (B-039, B-040, F-071)
- Prevent hands-free from auto-starting on page load (B-041)

Tasks
- In `bot/chat_ui.html`, make the Pause button (⏸) call BOTH `stopAgentSpeaking()` AND set `vadPaused = true` so VAD stops capturing audio
- Make the Play button (▶) set `vadPaused = false` to resume VAD listening
- In the TTS `ended` event handler, do NOT reset `vadPaused` — respect user's explicit pause state
- On page load, set `vadPaused = true` by default — user must click Play or the Hands-free toggle to start listening
- The "Stop speaking" banner button (`#stopSpeakingBtn`) should also pause VAD (set `vadPaused = true`)
- Add visual indicator: when paused, show "Paused" text next to the button instead of "Listening..."

Acceptance Criteria
- Clicking Pause stops TTS playback AND stops mic listening — no phantom messages
- Clicking Play resumes listening — VAD starts detecting speech again
- "Stop speaking" also pauses the mic
- Fresh page load does NOT auto-listen — user must explicitly activate hands-free
- Existing keyboard shortcut (Escape to stop speaking) also pauses VAD
