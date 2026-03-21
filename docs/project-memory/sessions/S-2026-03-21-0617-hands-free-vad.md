# Session

Session-ID: S-2026-03-21-0617-hands-free-vad
Title: Hands-free continuous speech with browser-side VAD
Date: 2026-03-21
Author: agentB (Claude)

## Goal

Add hands-free continuous speech mode with browser-side VAD, echo cancellation, silence threshold settings, and visual feedback to chat_ui.html (F-049, F-050, F-051).

## Context

Sprint 20 — voice push-to-talk works but requires holding a button. Users want hands-free mode for natural conversation. agentA handles server-side input filter; agentB (this session) owns chat_ui.html only.

## Plan

1. Load Silero VAD via @ricky0123/vad-web CDN
2. Add hands-free toggle button next to mic
3. Implement VAD callbacks (onSpeechStart/End/Misfire)
4. Add echo cancellation (pause VAD during TTS playback)
5. Add silence threshold slider in settings
6. Add visual feedback (color-coded border states)
7. Handle filtered responses from server
8. Update backlog

## Changes Made

- `bot/chat_ui.html`: Added Silero VAD (vad-web 0.0.19) and ONNX runtime CDN scripts
- `bot/chat_ui.html`: Added CSS for hands-free mode (toggle button, VAD status indicator, color-coded input borders, transcript preview, slider)
- `bot/chat_ui.html`: Added hands-free toggle button and VAD status indicator in voice controls
- `bot/chat_ui.html`: Added silence threshold slider (0.5s-3.0s) in settings panel
- `bot/chat_ui.html`: Added transcript preview area above input
- `bot/chat_ui.html`: Implemented full VAD lifecycle (init, start, pause, destroy) with Float32Array to PCM int16 conversion
- `bot/chat_ui.html`: Implemented echo cancellation via ttsAudioEl play/ended/error events
- `bot/chat_ui.html`: Added filtered response handling for both push-to-talk and hands-free modes
- `bot/chat_ui.html`: localStorage persistence for hands-free preference and silence threshold
- `docs/project-memory/backlog/README.md`: Marked F-049, F-050, F-051 as Complete (Sprint 20)

## Decisions Made

- Used vad-web 0.0.19 CDN (pinned version) rather than npm for simplicity in single-file HTML app
- VAD audio comes as Float32Array at 16kHz — convert directly to PCM int16 base64, skipping the MediaRecorder/AudioContext decode pipeline used by push-to-talk
- Echo cancellation uses simple play/ended event listeners on the existing ttsAudioEl rather than more complex WebAudio-based cancellation
- Silence threshold maps to VAD redemptionFrames via Math.round(seconds / 0.064)
- Hands-free restore has 1.5s delay to ensure VAD library is loaded from CDN

## Open Questions

- ONNX WASM file loading: vad-web may need explicit WASM path configuration depending on CDN caching behavior
- Mobile Safari may have additional constraints on continuous mic access in background tabs

## Links

Commits:
- (to be filled after commit)
