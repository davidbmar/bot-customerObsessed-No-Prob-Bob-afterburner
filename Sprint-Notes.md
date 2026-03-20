# Sprint 17 — Agent Notes

*Started: 2026-03-20 07:04 UTC*

Phase 1 Agents: 2
- agentA-provider-and-history
- agentB-ui-fixes

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentB-ui-fixes

*Completed: 2026-03-20 07:08 UTC*

### Files changed
- **`bot/chat_ui.html`** — Added inline typing dots CSS (`@keyframes pulse`, `.typing-dots-inline`) and modified `sendMessageStream()` to show pulsing dots inside the bot message bubble before tokens arrive, removing them on first token
- **`docs/project-memory/backlog/README.md`** — Marked B-022 and F-040 as Complete (Sprint 17)

### Commands run
- `git pull origin main` — already up to date
- `.venv/bin/python3 -m pytest tests/ -v` — 389 passed, 9 failed (pre-existing, missing optional deps), 1 skipped
- `git push -u origin HEAD` — pushed to `agentB-ui-fixes`

### Notes / follow-on work
- **B-022 (debug panel)**: The code already correctly defaults to hidden on first visit (init checks `localStorage.getItem('debugPanelVisible') === 'true'`). This was fixed in a prior sprint. Verified and confirmed working.
- **F-040 (typing dots)**: Three pulsing dots appear inside the bot message bubble during streaming, removed on first token arrival. Uses CSS-only animation (no JS timers).
- The 9 test failures are pre-existing — they require `anthropic` and `openai` packages which are optional dependencies not installed in the test venv.


---

## agentA-provider-and-history

*Completed: 2026-03-20 07:09 UTC*

```
All tasks complete.

---

## Files Changed

| File | Change |
|------|--------|
| `bot/gateway.py` | Default `_provider_id` to `"qwen-3.5"`, fix `health_check()` fallback |
| `bot/server.py` | Add `active_label` field to `/api/llm/providers` response |
| `scripts/generate_sprint_history.py` | Accept CLI args, auto-discover sprint range, updated docstring |
| `tests/test_sprint17_provider_and_history.py` | **New** — 46 tests for B-019 and B-021 |
| `tests/test_sprint14_conversations_tokens.py` | Updated assertion to match fixed behavior |
| `docs/PROJECT_STATUS_2026-03-20-sprint{12..16}.md` | **New** — 5 generated status docs |
| `docs/project-memory/backlog/README.md` | B-019 and B-021 marked Complete (Sprint 17) |
| `docs/project-memory/sessions/S-2026-03-20-0708-sprint17-provider-and-history.md` | **New** session doc |

## Commands Run

- `.venv/bin/python3 -m pytest tests/ -q` — **445 passed**, 0 failures
- `.venv/bin/python3 scripts/generate_sprint_history.py 12 16` — generated 5 docs
- `ls docs/PROJECT_STATUS_*.md | wc -l` — returns **16**
- `git push -u origin HEAD`

## Notes / Follow-on Work

- **F-040 (typing indicator)** is assigned to agentB per the brief — not implemented here
- **B-022 (debug panel default visibility)** is also agentB's scope (chat_ui.html)
- After sprint merge, run `build-sprint-data.sh` to rebuild dashboard data so sprints 12-16 appear
```

