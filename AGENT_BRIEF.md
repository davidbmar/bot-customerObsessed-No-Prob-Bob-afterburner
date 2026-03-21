agentB-hands-free-vad — Sprint 20

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
- Add hands-free continuous speech mode with browser-side VAD and echo cancellation

Tasks
1. **Add Silero VAD to `bot/chat_ui.html`**:
   - Load @ricky0123/vad-web from CDN: `https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.19/dist/bundle.min.js`
   - Also needs ONNX runtime WASM: `https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort-wasm-simd.wasm`
   - Initialize VAD with `MicVAD.new({ onSpeechEnd: (audio) => { ... } })`
   - VAD callbacks:
     - `onSpeechStart`: show recording indicator (red border)
     - `onSpeechEnd(audio)`: convert Float32Array to PCM int16, send to `/api/voice/transcribe`
     - `onVADMisfire`: short speech segment, ignore (accidental noise)
   - VAD config:
     - `positiveSpeechThreshold: 0.8` (high = less false triggers)
     - `negativeSpeechThreshold: 0.3`
     - `redemptionFrames: 8` (~480ms of silence before end-of-speech)
     - `minSpeechFrames: 5` (~300ms minimum speech to trigger)

2. **Hands-free toggle button**:
   - Add a toggle button next to the mic button: "Hands-free" or a headphone icon
   - When ON:
     - Hide the push-to-talk mic button
     - Show a "Listening..." indicator with a pulsing green dot
     - VAD continuously listens and auto-sends speech segments
     - The silence threshold (redemptionFrames) determines when speech "ends"
   - When OFF (default):
     - Show the push-to-talk mic button (existing behavior)
     - VAD is not loaded/running (saves resources)
   - Save preference to localStorage

3. **Echo cancellation** (F-050):
   - When TTS audio is playing (bot speaking), pause the VAD
   - Listen for the audio element's `play` and `ended` events
   - On `play`: call `vad.pause()` and show "Bot speaking..." indicator
   - On `ended`: call `vad.start()` and show "Listening..." indicator
   - This prevents the mic from picking up the bot's own voice

4. **Silence threshold setting** (F-051):
   - In the Settings panel (⚙), add a "Silence threshold" slider
   - Range: 0.5s to 3.0s (default 1.5s)
   - Maps to VAD `redemptionFrames`: `Math.round(threshold_seconds / 0.064)`
   - Label: "How long to wait after you stop speaking"
   - Save to localStorage, apply on next VAD init

5. **Visual feedback**:
   - Hands-free active: pulsing green border on the input area
   - Speech detected: border turns red (recording)
   - Processing STT: border turns yellow
   - Bot speaking: border turns blue, mic paused
   - Filtered (garbage): brief gray flash, no message sent
   - Show transcription text briefly before sending (so user sees what was heard)

6. **Handle filtered responses from server**:
   - When `/api/voice/transcribe` returns `filtered: true`, show a brief toast: "Filtered: [reason]" in debug mode, or silently ignore in normal mode
   - Don't send filtered text to the chat

7. **Update backlog** — Mark F-049, F-050, F-051 as Complete (Sprint 20)

Acceptance Criteria
- Toggle "Hands-free" → mic listens continuously, sends speech segments automatically
- Speak naturally → text appears in chat after 1.5s silence
- Bot speaks back → mic pauses, resumes after TTS ends
- Garbage speech ("um") → filtered, nothing sent to LLM
- Silence threshold slider in settings → changing it affects when speech "ends"
- Push-to-talk still works when hands-free is OFF
