# Sprint 24 — Agent Notes

*Started: 2026-03-21 17:44 UTC*

Phase 1 Agents: 2
- agentA-voice-settings
- agentB-server-docs

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-voice-settings

*Completed: 2026-03-21 17:48 UTC*

### Files changed
- `bot/chat_ui.html` — Added Voice Detection section (2 sliders + 1 checkbox), JS functions for persistence/restart, barge-in guards, localStorage restore
- `docs/project-memory/backlog/README.md` — F-061 marked Complete (Sprint 24)
- `docs/project-memory/sessions/S-2026-03-21-1747-voice-settings.md` — Session doc (new)

### Commands run
- `git fetch origin main && git merge origin/main` — synced with main
- `.venv/bin/python3 -m pytest tests/ -v` — 654 tests pass
- `git push -u origin HEAD` — branch pushed

### Notes / follow-on work
- Slider changes destroy and recreate the VAD instance (Silero doesn't support live option updates). A 200ms delay between stop/start prevents microphone contention.
- Barge-in toggle applies to both VAD hands-free and push-to-talk for consistent UX.
- Default values match the previously hardcoded values (sensitivity 0.80, min speech 5, barge-in ON), so existing users see no behavior change until they adjust settings.


---

## agentB-server-docs

*Completed: 2026-03-21 17:48 UTC*

```
All tasks complete. Here's the summary:

---

## Files Changed

| File | Action |
|------|--------|
| `docs/PROJECT_STATUS_2026-03-20-sprint20.md` | Created — Sprint 20 (VAD, input filter, echo cancellation, fast path) |
| `docs/PROJECT_STATUS_2026-03-21-sprint21.md` | Created — Sprint 21 (favicon, auth bypass, copy button, Escape, waveform) |
| `docs/PROJECT_STATUS_2026-03-21-sprint22.md` | Created — Sprint 22 (conversation persistence, projects API) |
| `docs/PROJECT_STATUS_2026-03-21-sprint23.md` | Created — Sprint 23 (paragraph spacing, notification sound, syntax highlighting, /api/stats) |
| `bot/gateway.py` | Modified — gateway-level error handling in `_handle_tool_calls` |
| `tests/test_sprint24_tool_errors.py` | Created — 5 tests for tool error handling |
| `docs/project-memory/backlog/README.md` | Modified — F-062, F-063 marked Complete |
| `docs/project-memory/sessions/S-2026-03-21-1747-sprint24-server-docs.md` | Created — session doc |

## Commands Run

- `git pull origin main` — already up to date
- `python3 -m pytest tests/ -v` — **659 tests passed**
- `git push -u origin HEAD` — pushed to `agentB-server-docs`

## Notes / Follow-on Work

- Dashboard data rebuild needed after merge so Sprints 20-23 appear in the dashboard UI
- F-061 (configurable VAD/barge-in settings) is assigned to agentA per the brief
```

