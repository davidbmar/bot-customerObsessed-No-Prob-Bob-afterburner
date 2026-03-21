agentA-server-polish — Sprint 21

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 20: Hands-free VAD, input filter, echo cancellation, fast path. All features complete.
- Voice interrupt/stop fixes landed post-sprint (barge-in, VAD state reset)
- Copy button only appears on first bot message — needs to be on all
- Google SSO blocks localhost testing without valid client ID
- No favicon causes 404 on every page load
- 631+ tests pass
─────────────────────────────────────────

Sprint-Level Context

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
