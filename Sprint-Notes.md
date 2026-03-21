# Sprint 20 — Agent Notes

*Started: 2026-03-21 06:13 UTC*

Phase 1 Agents: 2
- agentA-input-filter-fastpath
- agentB-hands-free-vad

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentB-hands-free-vad

*Completed: 2026-03-21 06:18 UTC*

### Files changed
- `bot/chat_ui.html` — All 7 tasks from the brief implemented (VAD, toggle, echo cancellation, silence threshold, visual feedback, filtered responses)
- `docs/project-memory/backlog/README.md` — F-049, F-050, F-051 marked Complete (Sprint 20)
- `docs/project-memory/sessions/S-2026-03-21-0617-hands-free-vad.md` — Session doc created

### Commands run
- `git pull origin main` — synced with main
- `.venv/bin/python3 -m pytest tests/ -v` — 519 passed, 10 failed (pre-existing: missing openai/anthropic packages, stale doc count assertion)
- `git commit` + `git push -u origin HEAD`

### Notes / follow-on work
- 10 test failures are all pre-existing (missing `openai`/`anthropic` pip packages and a stale `test_total_status_docs_count` expecting 18 docs but 19 exist). None related to this change.
- VAD WASM loading may need explicit path config if CDN caching misbehaves in some environments
- Mobile Safari may restrict continuous mic access in background tabs — worth testing on device


---

## agentA-input-filter-fastpath

*Completed: 2026-03-21 06:19 UTC*

### Files changed
- **`bot/input_filter.py`** (NEW) — STT quality classifier with `InputQuality` enum and `classify()` function
- **`bot/fast_path.py`** (NEW) — Instant answers for "help", "reset", "who are you" without LLM
- **`bot/server.py`** — Wired filter + fast path into `/api/voice/transcribe`; response now includes `filtered`, `quality`, `duration_s`, `fast_path_response`
- **`tests/test_input_filter.py`** (NEW) — 63 tests
- **`tests/test_fast_path.py`** (NEW) — 38 tests
- **`docs/project-memory/backlog/README.md`** — F-048, F-052 marked Complete (Sprint 20)
- **`docs/project-memory/sessions/S-2026-03-21-0617-sprint20-input-filter-fastpath.md`** (NEW)

### Commands run
- `git pull origin main`
- `python3 -m pytest tests/ -v` → **630 passed**, 1 pre-existing failure
- `git commit` + `git push -u origin HEAD`

### Notes / follow-on work
- **1 pre-existing test failure**: `test_sprint18_ui_polish.py::TestProjectStatusDocs::test_total_status_docs_count` — not related to this branch
- **Chat endpoint**: Fast path is only wired into the voice transcribe endpoint. Could also be added to `/api/chat` for text-based fast paths
- **Fixed regex bug**: The repeated-word hallucination pattern from the reference didn't actually match "the the the" — fixed with a non-capturing group for whitespace

