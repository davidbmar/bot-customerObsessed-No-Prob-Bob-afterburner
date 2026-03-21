# Sprint 29 — Agent Notes

*Started: 2026-03-21 19:22 UTC*

Phase 1 Agents: 2
- agentA-discard-button
- agentB-filter-docs

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-discard-button

*Completed: 2026-03-21 19:27 UTC*

### Files changed
- `bot/chat_ui.html` — Added voice transcription preview with discard button (F-069)
- `docs/project-memory/backlog/F-069-voice-discard-button.md` — New feature doc
- `docs/project-memory/backlog/README.md` — Added F-069 entry
- `docs/project-memory/sessions/S-2026-03-21-1926-sprint29-voice-discard.md` — Session doc

### Commands run
- `git pull origin main` — Already up to date
- `.venv/bin/python3 -m pytest tests/ -v` — **694 tests passed**
- `git push -u origin HEAD` — Pushed to `agentA-discard-button`

### What was implemented
1. **Voice transcription preview**: Both PTT and VAD paths now show transcribed text in the input field instead of auto-sending
2. **Discard button (✕)**: Appears next to input, clears transcription and returns to listening
3. **Countdown timer**: "Sending in 3... 2... 1..." auto-sends after 3 seconds
4. **Edit cancels auto-send**: If user starts typing, countdown stops but discard stays available
5. **Keyboard shortcuts**: Enter confirms, Escape discards
6. **Garbled warning**: Yellow border when transcription looks like noise (short, non-alpha heavy)

### Notes / follow-on work
- B-038 (TV/movie audio filtering) is being handled by agentB on the server side — this discard button is the client-side safety net
- The 3-second auto-send timeout is a hardcoded constant; could be made configurable in Settings panel in a future sprint if users want different delays


---

## agentB-filter-docs

*Completed: 2026-03-21 19:29 UTC*

### Files changed
- `bot/input_filter.py` — Added `BACKGROUND_NOISE` enum, `BACKGROUND_NOISE_MESSAGE`, three detection heuristics (long monologue, repeated phrases, no engagement markers)
- `bot/server.py` — Import `BACKGROUND_NOISE_MESSAGE`, return `filter_message` in STT response for background noise
- `tests/test_input_filter.py` — 18 new tests across 4 new test classes (87 total in file)
- `docs/PROJECT_STATUS_2026-03-21-sprint28.md` — Sprint 28 status doc
- `docs/project-memory/backlog/README.md` — B-038 marked Complete (Sprint 29)
- `docs/project-memory/sessions/S-2026-03-21-1928-sprint29-filter-docs.md` — Session doc

### Commands run
- `git fetch origin main`
- `python3 -m pytest tests/test_input_filter.py -v` (87 passed)
- `python3 -m pytest tests/ -v` (709 passed, 3 warnings)
- `git commit` + `git push -u origin HEAD`

### Notes / follow-on work
- The UI (chat_ui.html, owned by agentA) should check for `filter_message` in the STT response and display it to the user instead of silently ignoring filtered input
- The >200 word monologue check is intentionally aggressive — even user messages over 200 words get flagged. This is a reasonable trade-off since voice input of 200+ words in a single VAD segment is almost certainly media, not a user talking to a bot

