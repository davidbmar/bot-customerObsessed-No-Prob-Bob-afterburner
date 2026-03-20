# Sprint 19 — Agent Notes

*Started: 2026-03-20 08:02 UTC*

Phase 1 Agents: 2
- agentA-export-and-history
- agentB-markdown-and-dates

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-export-and-history

*Completed: 2026-03-20 08:07 UTC*

```
All tasks complete. Here's the summary:

---

## Files Changed
| File | Change |
|------|--------|
| `bot/tools.py` | Added `structured`, `messages`, `provider` params to `tool_save_discovery`; added `_format_structured_discovery()` and `_extract_section()` helpers |
| `bot/server.py` | Updated `_handle_save_discovery` to pass `structured=True` with parsed messages and provider |
| `tests/test_tools.py` | Added 15 new tests for structured export (extract_section, format_structured_discovery, save_discovery with structured=True) |
| `tests/test_sprint18_ui_polish.py` | Updated PROJECT_STATUS count assertion from 17 → 18 |
| `docs/PROJECT_STATUS_2026-03-20-sprint18.md` | Generated Sprint 18 status doc |
| `docs/project-memory/backlog/README.md` | Marked F-047 as Complete (Sprint 19) |

## Commands Run
- `git pull origin main` — sync with main
- `python3 scripts/generate_sprint_history.py 18 18` — generate Sprint 18 PROJECT_STATUS
- `pytest tests/ -v` — **485 passed, 0 failures**
- `git push -u origin HEAD` — pushed to remote

## Notes / Follow-on Work
- The structured export extracts sections from bot synthesis messages via regex. If the bot hasn't triggered synthesis yet (< 5 exchanges), placeholder text `[Not yet extracted from conversation]` is used — the raw conversation is always included.
- agentB owns `chat_ui.html` for F-044 (markdown rendering) and F-045 (date grouping) — those were not touched here.
```


---

## agentB-markdown-and-dates

*Completed: 2026-03-20 08:08 UTC*

**Files changed:**
- `bot/chat_ui.html` — markdown rendering fixes + date grouping
- `docs/project-memory/backlog/README.md` — F-044, F-045 marked Complete
- `docs/project-memory/sessions/S-2026-03-20-0807-markdown-and-dates.md` — session doc (new)

**Commands run:**
- `python3 -m pytest tests/ -v` — 470 passed
- `git commit` + `git push -u origin HEAD`

**Notes / follow-on work:**
- The markdown renderer covers the required subset (**bold**, *italic*, `code`, ```code blocks```, lists, headers). More complex markdown (tables, blockquotes, nested lists) is not supported — could be added in a future sprint if needed.
- Date separators work for both new messages and restored conversations. Existing saved conversations without `dateISO` will group all messages under the current date on first restore, then persist correct dates going forward.

