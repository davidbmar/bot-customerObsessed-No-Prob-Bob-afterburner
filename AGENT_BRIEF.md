Sprint 21 — merged (agentA-server-polish + agentB-chat-ux-fixes)

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

- `.venv/bin/python3 -m pytest tests/ -v` — all tests pass
