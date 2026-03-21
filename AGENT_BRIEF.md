agentA-input-filter-fastpath — Sprint 20

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 19: markdown rendering, date grouping, structured seed export. 485 tests pass.
- Voice push-to-talk works (STT via Faster-Whisper, TTS via Piper)
- No input quality filtering — every mic press hits the LLM even for garbage/silence
- No continuous speech mode — user must hold button to record
- Reference: ~/src/voice-calendar-scheduler-FSM/engine-repo/engine/input_filter.py has proven input filter
- Reference: ~/src/voice-calendar-scheduler-FSM/engine-repo/engine/fast_path.py has fast path for time/date queries
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add hands-free continuous speech mode with browser-side VAD — no push-to-talk needed (F-049)
- Port input quality filter from voice-calendar-scheduler to reject garbage STT before hitting LLM (F-048)
- Add echo cancellation — mute mic while TTS is playing back (F-050)
- Add configurable silence threshold for hands-free mode (F-051)
- Add fast path for simple queries without LLM (F-052)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/input_filter.py (NEW), bot/fast_path.py (NEW), bot/server.py, bot/stt.py, tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html
- Reference implementation: ~/src/voice-calendar-scheduler-FSM/engine-repo/engine/input_filter.py and fast_path.py
- Tag v2.0-before-continuous-speech marks the rollback point


Objective
- Port input quality filter and fast path from voice-calendar-scheduler, wire into server

Tasks
1. **Create `bot/input_filter.py`** — Port from `~/src/voice-calendar-scheduler-FSM/engine-repo/engine/input_filter.py`:
   - Copy the file and adapt imports (no external dependencies needed, just `re` and `logging`)
   - `InputQuality` enum: VALID, GARBAGE, LOW_QUALITY
   - `classify(text, no_speech_prob, avg_logprob, audio_duration_s)` function
   - Keep the garbage word list, hallucination patterns, and all thresholds
   - Add discovery-specific garbage words if needed (but don't remove greetings — "hi" is valid for a discovery bot)

2. **Create `bot/fast_path.py`** — Simplified version of `~/src/voice-calendar-scheduler-FSM/engine-repo/engine/fast_path.py`:
   - `try_fast_path(text) -> Optional[str]`
   - Fast paths for the discovery bot context:
     - "help" / "what can you do" → describe the bot's purpose
     - "reset" / "start over" → clear conversation, return welcome message
     - "who are you" / "what are you" → personality description
   - Do NOT port the time/date fast paths (not relevant for discovery bot)
   - Return None for anything that should go to the LLM

3. **Wire into `bot/server.py`** — Update the voice transcribe handler and chat endpoints:
   - After STT transcription, run `classify()` on the result
   - If GARBAGE or LOW_QUALITY, return `{"text": "", "filtered": true, "reason": "garbage"}` with 200 status (not an error — just silently filtered)
   - Before sending to gateway, run `try_fast_path()` — if it returns a response, send that directly without LLM
   - Add `audio_duration_s` to the transcribe response (calculate from audio_bytes length / sample_rate)
   - Update `/api/voice/transcribe` response to include `{"filtered": bool, "quality": "valid|garbage|low", "duration_s": float}`

4. **Write tests** in `tests/test_input_filter.py` and `tests/test_fast_path.py`:
   - Test garbage words are filtered ("um", "uh", "the")
   - Test greetings are NOT filtered ("hello", "hi", "hey")
   - Test short audio (< 0.6s) is filtered
   - Test high no_speech_prob is filtered
   - Test hallucination patterns are filtered
   - Test fast path responses for "help", "reset", "who are you"
   - Test fast path returns None for real questions
   - Target: 510+ total tests

5. **Update backlog** — Mark F-048, F-052 as Complete (Sprint 20)

Acceptance Criteria
- `from bot.input_filter import classify, InputQuality` works
- `classify("um", 0.0, 0.0, 1.0)` returns GARBAGE
- `classify("We need better reporting", 0.0, -0.5, 3.0)` returns VALID
- `try_fast_path("help")` returns a help message
- `try_fast_path("We need a dashboard")` returns None
- STT endpoint returns `filtered: true` for garbage input
- `.venv/bin/python3 -m pytest tests/ -v` — 510+ tests, 0 failures
