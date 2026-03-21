# S-2026-03-21-1926-sprint29-voice-discard

## Title
Sprint 29: Voice Transcription Discard Button (F-069)

## Goal
Add a discard option for voice transcriptions so users can cancel before sending, preventing bad STT results from reaching the LLM.

## Context
- Hands-free mode picks up TV/movie audio and sends it as user messages (B-038)
- No way to discard a bad voice transcription before it's sent
- Sprint 29, Agent A task

## Plan
1. Modify VAD and PTT handlers to show transcription preview instead of auto-sending
2. Add discard (X) button and countdown timer to input area
3. Detect garbled transcriptions and show warning border
4. Allow editing, Enter to confirm, Escape to discard
5. Update backlog with F-069

## Changes Made
- `bot/chat_ui.html`: Added voice preview CSS (blue/yellow borders, discard button, countdown)
- `bot/chat_ui.html`: Added discard button and countdown span to input area HTML
- `bot/chat_ui.html`: Added voice preview state machine JS (showVoicePreview, discardVoicePreview, confirmVoicePreview, isGarbledTranscription)
- `bot/chat_ui.html`: Modified sendVADToServer to use showVoicePreview instead of immediate sendMessage
- `bot/chat_ui.html`: Modified PTT transcription handler to use showVoicePreview
- `bot/chat_ui.html`: Extended Escape key handler to discard voice preview
- `bot/chat_ui.html`: Extended Enter key handler to confirm voice preview
- `bot/chat_ui.html`: sendMessage() now clears voice preview UI
- `docs/project-memory/backlog/F-069-voice-discard-button.md`: Created feature doc
- `docs/project-memory/backlog/README.md`: Added F-069 to feature table

## Decisions Made
- 3-second auto-send timer preserves hands-free flow while giving users a chance to discard
- User typing in the input cancels auto-send but keeps text (editing mode)
- Garbled detection heuristic: < 3 chars, no multi-char words, or < 40% alpha characters
- Yellow border for garbled, blue border for normal voice preview
