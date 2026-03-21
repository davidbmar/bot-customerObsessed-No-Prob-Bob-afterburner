agentA-discard-button — Sprint 29

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 28: Voice personality awareness, PROJECT_STATUS Sprint 27, dynamic Docs stats
- 690+ tests pass
- Hands-free mode picks up TV/movie audio and sends it as user messages
- No way to discard a bad voice transcription before it's sent
─────────────────────────────────────────

Sprint-Level Context

Goal
- Improve input quality filter to catch TV/movie audio and other background noise (B-038)
- Generate PROJECT_STATUS doc for Sprint 28
- Add "discard" button on transcribed voice messages so user can cancel before sending

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, bot/gateway.py, bot/stt.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Add a "discard" option when voice transcription appears so user can cancel before sending

Tasks
1. **Add transcription preview with discard** (F-069):
   - Currently, when VAD detects speech and sends audio to STT, the transcribed text is immediately sent to the LLM
   - Change the flow: show the transcribed text as a preview in the input field FIRST
   - Add a small "✕" (discard) button next to the text
   - User can either: click Send (or press Enter) to confirm, or click ✕ to discard
   - Auto-send after 3 seconds if user doesn't act (keeps the hands-free flow smooth)
   - If the transcription looks garbled (very short, no real words), show it with a yellow warning border

2. **Show transcription preview in input field**:
   - When STT returns text, put it in the input textbox instead of auto-sending
   - Change input border to a subtle blue to indicate "voice transcription pending"
   - Add a small countdown indicator: "Sending in 3... 2... 1..." or a progress bar
   - If user starts typing, cancel the auto-send (they want to edit)
   - If user clicks ✕, clear input and return to listening

3. **Update backlog** — Add F-069 and mark as Complete (Sprint 29)

Acceptance Criteria
- Voice transcription appears in input field as preview, not auto-sent
- ✕ button discards the transcription
- Enter or Send confirms it
- Auto-sends after 3 seconds if no action
- User can edit the transcription before sending
