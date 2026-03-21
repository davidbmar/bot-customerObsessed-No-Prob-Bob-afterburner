agentA-voice-settings — Sprint 24

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 23: paragraph spacing fix, notification sound toggle, code syntax highlighting, /api/stats endpoint, tool result regression tests
- 654 tests pass
- Barge-in hotfix: VAD no longer paused during TTS, enables voice interruption
- User wants configurable VAD thresholds like the apartment locator admin panel
- Dashboard only shows Sprints 1-19, missing 20-23
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add configurable VAD and barge-in settings panel — expose Silero VAD thresholds as user-adjustable sliders (F-061)
- Generate PROJECT_STATUS docs for Sprints 20-23 so dashboard shows recent sprint history (F-062)
- Better error messages when bot tool calls fail — show what went wrong instead of generic error (F-063)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, bot/gateway.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Add a Voice Settings section in the Settings panel with configurable VAD and barge-in parameters

Tasks
1. **Add Voice Settings section to Settings panel** (F-061):
   - In the Settings overlay in `bot/chat_ui.html`, after the "Silence Threshold" slider, add a new section header: "Voice Detection"
   - Add these configurable sliders:
     a. **Speech Sensitivity** — controls `positiveSpeechThreshold` on the Silero VAD instance
        - Slider range: 0.5 (very sensitive) to 0.95 (strict, only clear speech)
        - Default: 0.8 (current hardcoded value at ~line 3876)
        - Label shows current value like "0.80"
        - Description: "How confident VAD must be that audio is speech. Lower = catches quieter speech but may false-trigger."
     b. **Barge-in Toggle** — checkbox to enable/disable interrupting the bot mid-speech
        - Default: ON (current behavior)
        - When OFF: the `onSpeechStart` handler should NOT call `stopAgentSpeaking()` even if `isBotSpeaking` is true
        - Description: "Allow voice to interrupt the bot while it's speaking"
     c. **Min Speech Duration** — controls `minSpeechFrames` on the VAD instance
        - Slider range: 1 (instant) to 15 (needs ~0.5s of speech)
        - Default: 5 (current hardcoded value)
        - Description: "How long speech must sustain before it's confirmed. Higher = fewer false triggers."

2. **Wire sliders to VAD instance**:
   - When sliders change, update the VAD instance's options if possible. Silero VAD may not support dynamic option changes — if so, destroy and recreate the VAD instance with new options.
   - Store preferences in localStorage: `vadSensitivity`, `bargeInEnabled`, `vadMinSpeech`
   - On page load, restore saved preferences and apply to VAD initialization
   - Replace the hardcoded values at ~line 3876 (`positiveSpeechThreshold: 0.8`, `minSpeechFrames: 5`) with the stored/default values

3. **Add barge-in guard**:
   - Read barge-in toggle state in `onSpeechStart` callback
   - If barge-in is disabled: skip the `stopAgentSpeaking()` call, just start recording

4. **Update backlog** — Add F-061 and mark as Complete (Sprint 24)

Acceptance Criteria
- Settings panel shows Voice Detection section with 2 sliders and 1 checkbox
- Changing Speech Sensitivity affects how easily VAD triggers
- Toggling Barge-in OFF prevents voice from interrupting TTS
- Settings persist across page reloads
- `.venv/bin/python3 -m pytest tests/ -v` — all pass
