# Session

Session-ID: S-2026-03-21-2051-fix-pause-play-vad
Title: Fix pause/play to stop both TTS and VAD listening
Date: 2026-03-21
Author: agentA

## Goal

Fix broken pause/play hands-free behavior so Pause stops BOTH speaking AND listening (B-039, B-040, F-071, B-041).

## Context

The pause button only toggled VAD but didn't stop TTS. Multiple handlers (TTS ended, error, setAgentSpeaking) would override the user's explicit pause by resetting to "listening" state. Page load auto-restored hands-free in listening mode.

## Plan

1. Make Pause stop TTS + pause VAD
2. Make Play resume VAD
3. Guard all auto-resume paths with vadPaused check
4. Default vadPaused=true on page load
5. Stop speaking button and Escape key also pause VAD
6. Barge-in uses stopAgentSpeakingOnly() to avoid pausing during active speech

## Changes Made

- Split stopAgentSpeaking into stopAgentSpeakingOnly (TTS only) and stopAgentSpeaking (TTS + pause VAD)
- toggleVadPause now calls stopAgentSpeakingOnly when pausing
- setAgentSpeaking(false) respects vadPaused state
- TTS ended/error handlers respect vadPaused state
- startVAD respects vadPaused on initialization
- Page load restores hands-free but starts paused
- Escape key and stop-speaking button now pause VAD via stopAgentSpeaking
- onVADMisfire and filtered timeout respect vadPaused
- Barge-in uses stopAgentSpeakingOnly to avoid pausing during user speech
- vadPaused defaults to true

## Decisions Made

- Split stopAgentSpeaking into two functions rather than adding a parameter — cleaner call sites
- Barge-in (onSpeechStart, startVoiceRecording) uses stopAgentSpeakingOnly because user is actively speaking
- User-initiated stops (Escape, stop button, pause button) use stopAgentSpeaking which pauses VAD
- toggleHandsfree sets vadPaused=false (user explicitly activating), but page-load restore keeps vadPaused=true

## Open Questions

None.

## Links

Commits:
- (pending commit)

PRs:
- (pending)
