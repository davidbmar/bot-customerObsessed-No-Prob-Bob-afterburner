agentA-project-dropdown — Sprint 33

Previous Sprint Summary
─────────────────────────────────────────
# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 31: Pause/play fix, dashboard backlog fix)

## Sprint 31 Summary

Sprint 31 fixed the broken pause/play hands-free behavior so Pause stops both TTS speaking and VAD listening (B-039, B-040, F-071, B-041), and fixed the dashboard backlog showing 0 items by correcting the backlog file path in build-sprint-data.sh (B-015, B-042). agentA rewired the pause/play toggle in chat_ui.html. agentB fixed the backlog path in the build script and added error handling to bot tools.

---

## What Changed

### agentB-backlog-tools

Fixed dashboard backlog showing 0 items (B-015) by updating `build-sprint-data.sh` to check `backlog/README.md` in addition to `backlog.md`. Added error handling in `bot/tools.py` so dashboard API connection errors return a friendly message instead of raising exceptions (B-042).

**Commits:**
- e659e98 agentB-backlog-tools: implement sprint 31 tasks
- 079e964 fix: dashboard backlog parsing + bot tool error handling (B-015, B-042)

**Files:** bot/tools.py, scripts/build-sprint-data.sh (afterburner repo)

### agentA-pause-play

Fixed pause/play toggle to stop both TTS playback and VAD listening (B-039, B-040, F-071). Pause button now calls `stopAgentSpeaking()` and sets `vadPaused = true`. Fresh page load no longer auto-listens — user must explicitly activate hands-free (B-041). Escape key and "Stop speaking" button also pause VAD.

**Commits:**
- 5944b03 agentA-pause-play: implement sprint 31 tasks
- 5e0e78e feat: fix pause/play to stop both TTS and VAD listening (B-039, B-040, F-071, B-041)

**Files:** bot/chat_ui.html

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-backlog-tools | Dashboard backlog fix (B-015, B-042) | 1 | Clean | 2 |
| 2 | agentA-pause-play | Pause/play fix (B-039, B-040, F-071, B-041) | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- B-039: Pause button doesn't stop VAD listening
- B-040: Phantom messages when paused
- B-041: Hands-free auto-starts on page load
- B-015: Dashboard backlog counts show 0
- B-042: Bot tools show raw errors when dashboard unreachable
- F-071: Pause/play toggle improvements

### Still Open
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-010: GitHub not configured in dashboard project entry
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written

---

## Test Results

700+ tests passing.

---

## Next Steps

- Generate missing PROJECT_STATUS docs for Sprints 30-31 (B-043, F-073)
- Fix sprint-run.sh `local -A` crash on zsh (B-008)
─────────────────────────────────────────

Sprint-Level Context

Goal
- Auto-rebuild dashboard data after sprint merges so bot always returns current sprint info (F-074, B-046)
- Generate PROJECT_STATUS doc for Sprint 32 and fix Active Project dropdown (B-047, B-045, F-075)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `.sprint/scripts/` and `docs/` files
- No two agents may modify the same files


Objective
- Fix the empty Active Project dropdown in Settings panel (B-045, F-075)

Tasks
- In `bot/chat_ui.html`, find the Active Project combobox in the Settings panel
- On Settings panel open, fetch project list from `/api/projects` (the bot server proxies or the dashboard serves this)
- Populate the dropdown with project slugs and names from the response
- Pre-select the currently active project
- When the user selects a different project, send a POST to update the active project in the bot config
- If only one project is registered, still show it (don't hide the dropdown)

Acceptance Criteria
- Settings panel Active Project dropdown shows all registered Afterburner projects
- Selecting a different project updates the active project for tool calls
- Dropdown is populated on every Settings panel open (not cached stale)
