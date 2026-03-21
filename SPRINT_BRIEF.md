# Sprint 29

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

Merge Order
1. agentB-filter-docs
2. agentA-discard-button

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 28: Voice personality awareness, PROJECT_STATUS Sprint 27, dynamic Docs stats
- 690+ tests pass
- Hands-free mode picks up TV/movie audio and sends it as user messages
- No way to discard a bad voice transcription before it's sent

## agentA-discard-button

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

## agentB-filter-docs

Objective
- Improve server-side input filter to catch more background noise
- Generate PROJECT_STATUS doc for Sprint 28

Tasks
1. **Improve input quality filter** (B-038):
   - In `bot/gateway.py` or wherever the input filter runs, add additional heuristics:
     a. **Long monologue detection**: if transcribed text is > 200 words from a single VAD segment, it's likely background media, not directed speech. Flag or truncate.
     b. **Repeated phrase detection**: if the same phrase appears 3+ times ("on the mat, on the mat, on the mat"), it's likely media.
     c. **No question/greeting detection**: if a long message (>50 words) has no question marks, no greetings ("hello", "hey", "ok"), and no first-person pronouns ("I", "my", "we"), it's likely not directed at the bot.
   - When detected as background noise, return a filter response like: "It sounds like there might be background audio. If you're talking to me, try again — I'm listening!"
   - Don't silently drop — always let the user know

2. **Generate PROJECT_STATUS doc**:
   - `docs/PROJECT_STATUS_2026-03-21-sprint28.md` — Sprint 28: Voice personality, PROJECT_STATUS Sprint 27
   - Follow PROJECT_STATUS_TEMPLATE.md format

3. **Write tests for improved filter**:
   - Test that a 300-word movie transcript is detected as background noise
   - Test that a normal user message ("I want to build a feedback tool") passes through
   - Test that repeated phrases are caught

4. **Update backlog** — Mark B-038 as Complete (Sprint 29)

Acceptance Criteria
- Long movie transcripts are caught by filter
- Normal user messages pass through unchanged
- Repeated phrases are detected
- PROJECT_STATUS doc exists for Sprint 28
- All tests pass
