# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 24: VAD settings, PROJECT_STATUS catch-up, tool error handling)

## Sprint 24 Summary

Sprint 24 added configurable VAD/barge-in settings (sensitivity, min speech duration, barge-in toggle) as sliders in the Settings panel, generated PROJECT_STATUS docs for Sprints 20-23 to keep the dashboard current, and improved tool error messages to show tool name and reason instead of raw exceptions.

---

## What Changed

### agentA-voice-settings

Configurable VAD sensitivity, min speech duration, and barge-in toggle (F-061) — exposed Silero VAD thresholds as sliders in the Settings panel.

**Commits:**
- 3907b5a feat: add configurable VAD sensitivity, min speech, and barge-in toggle (F-061)

**Files:** 5 files changed, +188, -62

### agentB-server-docs

PROJECT_STATUS docs for Sprints 20-23 (F-062), improved tool error messages in gateway.py (F-063), tool error unit tests.

**Commits:**
- b4ef716 feat: PROJECT_STATUS docs for Sprints 20-23, improve tool error messages

**Files:** 10 files changed, +525, -65

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-server-docs | PROJECT_STATUS docs Sprints 20-23 (F-062), tool error messages (F-063) | 1 | Clean | 10 |
| 2 | agentA-voice-settings | Configurable VAD/barge-in settings (F-061) | 1 | Clean | 5 |

---

## Backlog Snapshot

### Completed This Sprint
- F-061: Configurable VAD/barge-in settings
- F-062: Generate PROJECT_STATUS docs for Sprints 20-23
- F-063: Better tool error messages

### Still Open
- F-064: Stop generating button
- F-065: Hands-free pause/resume
- F-066: Scroll-to-bottom FAB
- B-008: sprint-run.sh crashes with `local -A` on zsh

---

## Next Steps

- Implement Stop Generating button (F-064) — cancel streaming mid-generation
- Add Hands-free pause/resume toggle (F-065)
