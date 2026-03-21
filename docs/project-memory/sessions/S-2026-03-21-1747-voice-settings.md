# Session

Session-ID: S-2026-03-21-1747-voice-settings
Title: Add configurable VAD and barge-in settings panel (F-061)
Date: 2026-03-21
Author: agentA (Sprint 24)

## Goal

Add a Voice Detection section to the Settings panel with configurable Silero VAD parameters (speech sensitivity, min speech duration) and a barge-in toggle.

## Context

Sprint 23 shipped hands-free VAD with hardcoded thresholds (positiveSpeechThreshold: 0.8, minSpeechFrames: 5) and always-on barge-in. User requested configurable thresholds similar to the apartment locator admin panel.

## Plan

1. Add Voice Detection UI section to Settings panel (2 sliders + 1 checkbox)
2. Wire sliders to localStorage persistence and VAD instance restart
3. Add barge-in guard to both VAD onSpeechStart and push-to-talk startVoiceRecording
4. Restore settings on page load
5. Update backlog F-061 status

## Changes Made

- `bot/chat_ui.html`: Added Voice Detection section with Speech Sensitivity slider (0.50-0.95), Min Speech Duration slider (1-15), and Barge-in toggle checkbox
- `bot/chat_ui.html`: Added JS functions: getVadSensitivity(), getVadMinSpeech(), isBargeInEnabled(), updateVadSensitivityLabel(), updateVadMinSpeechLabel(), toggleBargeIn(), restartVADIfActive()
- `bot/chat_ui.html`: VAD init now uses getVadSensitivity() and getVadMinSpeech() instead of hardcoded values
- `bot/chat_ui.html`: Barge-in guard added to both onSpeechStart (VAD) and startVoiceRecording (push-to-talk) — checks isBargeInEnabled()
- `bot/chat_ui.html`: restoreHandsfreePrefs() now restores voice detection settings from localStorage
- `docs/project-memory/backlog/README.md`: F-061 marked Complete (Sprint 24)

## Decisions Made

- Slider changes trigger VAD destroy+recreate (restartVADIfActive) since Silero VAD doesn't support live option updates
- Barge-in guard applies to both VAD hands-free mode AND push-to-talk for consistency
- Default values match previous hardcoded values (sensitivity 0.80, min speech 5, barge-in on) for zero-change upgrade

## Open Questions

None.

## Links

Commits:
- (pending commit)
