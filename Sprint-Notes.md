# Sprint 21 — Agent Notes

*Started: 2026-03-21 16:51 UTC*

Phase 1 Agents: 2
- agentA-server-polish
- agentB-chat-ux-fixes

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-server-polish

*Completed: 2026-03-21 16:54 UTC*

### Files changed
- **`bot/static/favicon.svg`** (new) — SVG chat bubble favicon
- **`bot/static/favicon.ico`** (new) — 16x16 ICO favicon
- **`bot/server.py`** — Added `STATIC_DIR`, `/favicon.ico` + `/favicon.svg` routes, `_serve_static()` method, `<link rel="icon">` injection, localhost auth bypass logging
- **`tests/test_favicon_and_auth.py`** (new) — 5 integration tests for favicon serving and auth bypass
- **`docs/project-memory/backlog/README.md`** — Marked F-056, F-057, B-026 as Complete (Sprint 21)
- **`docs/project-memory/sessions/S-2026-03-21-1654-sprint21-favicon-auth-bypass.md`** (new) — Session doc

### Commands run
- `git pull origin main` — already up to date
- `pytest tests/ -v` — 636 passed
- `git commit` + `git push -u origin HEAD`

### Notes / follow-on work
- The favicon uses an indigo (#6366f1) chat bubble design — can be replaced with a custom brand icon later
- Auth bypass is automatic: when `GOOGLE_CLIENT_ID` is unset, the frontend skips the auth overlay (no code change needed in `chat_ui.html` — agentB's territory)
- The `_serve_static()` method is generic enough to serve additional static assets if needed in the future


---

## agentB-chat-ux-fixes

*Completed: 2026-03-21 16:57 UTC*

### Files changed
- `bot/chat_ui.html` — all 4 UX fixes
- `docs/project-memory/backlog/README.md` — 5 items marked Complete (Sprint 21)
- `docs/project-memory/sessions/S-2026-03-21-1657-sprint21-chat-ux-fixes.md` — new session doc

### Commands run
- `git fetch origin main && git merge origin/main` — synced with main
- `.venv/bin/python3 -m pytest tests/ -v` — 621 passed, 9 failed (pre-existing missing optional deps), 1 skipped

### What was implemented
1. **Copy button on all bot messages** (B-027, F-055): Extracted `addCopyButton()` helper, called from `addMessage()`, streaming `done` event, and stream early-exit path
2. **Escape key stops bot speaking** (F-054): Global `keydown` listener, works even when input is focused
3. **Voice waveform** (F-053): Canvas element with 5 animated frequency bars using `AnalyserNode` connected to VAD's mic stream, shown only during recording
4. **Send button on paste/autofill** (B-025): Button starts disabled, toggled by `updateSendButton()` on `input`/`keyup`/`change`/`paste` events

### Notes / follow-on work
- The 9 test failures are pre-existing — all `ModuleNotFoundError: No module named 'openai'` or `'anthropic'` (optional provider dependencies not installed)
- The waveform tries to use `vadInstance.stream` from the VAD library; falls back to a separate `getUserMedia` call if not available
- F-056 (favicon) and F-057 (auth bypass) are in agentA's scope per the brief

