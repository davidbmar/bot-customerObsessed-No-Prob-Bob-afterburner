# Sprint 21

Goal
- Fix Copy button so it appears on all bot messages, not just the first (B-027, F-055)
- Add Escape key shortcut to stop bot speaking (F-054)
- Add localhost dev auth bypass — skip Google SSO when running on localhost (F-057)
- Add favicon so browser tab has an icon and no 404 (F-056)
- Voice activity waveform visualization during recording (F-053)
- Fix Send button not enabling on paste/autofill (B-025)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/server.py, bot/auth.py, bot/static/ (NEW), tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html

Merge Order
1. agentA-server-polish
2. agentB-chat-ux-fixes

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
curl -sf http://localhost:1203/favicon.ico -o /dev/null && echo "Favicon: OK" || echo "Favicon: MISSING"
```

Previous Sprint
- Sprint 20: Hands-free VAD, input filter, echo cancellation, fast path. All features complete.
- Voice interrupt/stop fixes landed post-sprint (barge-in, VAD state reset)
- Copy button only appears on first bot message — needs to be on all
- Google SSO blocks localhost testing without valid client ID
- No favicon causes 404 on every page load
- 631+ tests pass

## agentA-server-polish

Objective
- Add favicon, localhost auth bypass, fix server-side polish items

Tasks
1. **Add favicon** (F-056):
   - Create a simple SVG favicon in `bot/static/favicon.svg` — a chat bubble or robot icon
   - Also create `bot/static/favicon.ico` (can be a minimal 16x16 ICO or just serve the SVG)
   - Add a route in `bot/server.py` to serve `/favicon.ico` from `bot/static/`
   - Add `<link rel="icon">` injection when serving `chat_ui.html` (similar to how Google Client ID is injected)

2. **Localhost auth bypass** (F-057):
   - In `bot/server.py` where `__GOOGLE_CLIENT_ID__` is injected into the HTML:
     - If `GOOGLE_CLIENT_ID` env var is empty/unset, inject `window.__GOOGLE_CLIENT_ID__ = ""` so the frontend skips the auth overlay
     - This already works per the frontend logic (line ~3297: `if (window.__GOOGLE_CLIENT_ID__ && window.google)`)
     - But ALSO: if the request comes from `localhost` or `127.0.0.1` AND no `GOOGLE_CLIENT_ID` is set, log a message: "Auth disabled (no GOOGLE_CLIENT_ID set, localhost access)"
   - Verify: when `.env` has no `GOOGLE_CLIENT_ID`, the chat loads without the auth overlay

3. **Write tests** for favicon serving:
   - Test that GET `/favicon.ico` returns 200 with content
   - Test that the HTML includes `<link rel="icon">`

4. **Update backlog** — Mark F-056, F-057 as Complete (Sprint 21)

Acceptance Criteria
- `curl http://localhost:1203/favicon.ico` returns 200
- Chat page HTML includes `<link rel="icon">`
- With `GOOGLE_CLIENT_ID` unset, chat loads without auth overlay on localhost
- `.venv/bin/python3 -m pytest tests/ -v` — all tests pass

## agentB-chat-ux-fixes

Objective
- Fix Copy button, add Escape shortcut, add voice waveform, fix Send button

Tasks
1. **Copy button on all bot messages** (B-027, F-055):
   - Find where the Copy button is added to bot messages in `bot/chat_ui.html`
   - The issue is likely that `addCopyButton()` or equivalent is only called for the first/welcome message
   - Ensure every bot message bubble gets a Copy button
   - Copy button should copy the message text (not HTML) to clipboard

2. **Escape key stops bot speaking** (F-054):
   - Add a `keydown` event listener for the Escape key
   - If `isBotSpeaking` is true, call `stopAgentSpeaking()`
   - Only when the text input is NOT focused (don't steal Escape from other uses) — actually, Escape to stop speaking should work even when typing, since it's a safety/interrupt action

3. **Voice activity waveform** (F-053):
   - Add a small canvas element next to the hands-free indicator
   - When VAD state is 'recording', draw a simple waveform using the Web Audio API's AnalyserNode
   - Connect to the existing microphone stream (from VAD's audio context)
   - Draw 3-5 animated bars or a simple oscilloscope line
   - Hide when not recording
   - Keep it small — fits in the input area next to "Hearing speech..."

4. **Fix Send button on paste/autofill** (B-025):
   - Find the event listener that enables/disables the Send button
   - Add `keyup` and `change` event listeners in addition to `input`
   - Or: use a MutationObserver on the input's value, or check in a `requestAnimationFrame` loop (simpler: just add `keyup`)

5. **Update backlog** — Mark B-025, B-027, F-053, F-054, F-055 as Complete (Sprint 21)

Acceptance Criteria
- Every bot message has a Copy button (not just the first)
- Click Copy on any message → text copied to clipboard
- Press Escape while bot is speaking → TTS stops immediately
- Voice waveform visible during recording in hands-free mode
- Paste text into input → Send button enables
- `.venv/bin/python3 -m pytest tests/ -v` — all tests pass
