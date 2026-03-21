# F-069: Voice Transcription Discard Button

## Summary
Add a "discard" option when voice transcription appears so user can cancel before sending. Shows transcribed text as preview in input field with a countdown timer and discard button instead of auto-sending immediately.

## Priority
High

## Status
Complete (Sprint 29)

## Details
- Voice transcription (both PTT and VAD) now shows text in input field as preview
- Discard button (X) lets user cancel the transcription
- Auto-sends after 3 seconds if user takes no action (keeps hands-free flow smooth)
- User can edit transcription before sending (cancels auto-send timer)
- Enter confirms immediately, Escape discards
- Garbled transcriptions (short, non-alpha) shown with yellow warning border
- Blue border indicates "voice transcription pending" state
