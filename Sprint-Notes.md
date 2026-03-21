# Sprint 27 — Agent Notes

*Started: 2026-03-21 18:43 UTC*

Phase 1 Agents: 2
- agentA-word-count
- agentB-deps-docs

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-word-count

*Completed: 2026-03-21 18:45 UTC*

## Files changed
- `bot/chat_ui.html` — Added `.word-count-indicator` CSS, HTML element, and `updateWordCount()` JS function
- `docs/project-memory/backlog/README.md` — Marked F-067 as Complete (Sprint 27)
- `docs/project-memory/sessions/S-2026-03-21-1845-word-count-indicator.md` — Session doc (new)
- `AGENT_BRIEF.md` — Already tracked as modified

## Commands run
- `git pull origin main` — up to date
- `python3 -m pytest tests/ -v` — 689 passed
- `git push -u origin HEAD` — pushed

## Notes / follow-on work
- Token estimate uses `words × 1.3` heuristic as specified. If more accurate tokenization is needed later, a proper tokenizer library (e.g. tiktoken) could be integrated server-side.
- The indicator appears below the input area, right-aligned, in 11px muted text — disappears when input is empty.


---

## agentB-deps-docs

*Completed: 2026-03-21 18:47 UTC*

**Files changed (6):**
- `pyproject.toml` — Added `providers` extra group; updated `dev` and `all` groups with anthropic, openai, google-auth[requests]
- `scripts/start.sh` — Added `pip install -q -e ".[dev]"` after venv activation
- `tests/test_sprint27_deps.py` — 4 import tests (anthropic, openai, google.oauth2.id_token, google.auth.transport.requests)
- `docs/PROJECT_STATUS_2026-03-21-sprint26.md` — Sprint 26 status doc
- `docs/project-memory/backlog/README.md` — B-035, B-036 marked Complete (Sprint 27)
- `docs/project-memory/sessions/S-2026-03-21-1846-sprint27-deps-docs.md` — Session doc

**Commands run:**
- `python3.12 -m venv .venv && pip install -e ".[dev]"` — created venv with Python 3.12
- `python3 -c "import anthropic; ..."` — verified imports work
- `pytest tests/ -v` — 693 tests passing
- `git push -u origin HEAD` — pushed to `agentB-deps-docs`

**Notes / follow-on work:**
- agentA owns F-067 (message word count) and chat_ui.html — not touched here
- The `AGENT_BRIEF.md` is still modified (expected — sprint infrastructure file)

