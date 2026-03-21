# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 27: Fix deps, word count indicator)

## Sprint 27 Summary

Sprint 27 fixed pyproject.toml dependency groups (B-035, B-036) so fresh installs include anthropic, openai, and google-auth providers, and renamed `start.sh` to `start_local.sh` with optional-dep installation. Also added a word/character count indicator below the chat input (F-067) showing approximate token usage before sending long messages. agentB generated the Sprint 26 PROJECT_STATUS doc and added dependency tests.

---

## What Changed

### agentA-word-count

Word/token count indicator below chat input (F-067) and start.sh rename.

**Commits:**
- 075dde9 feat: add word/token count indicator below chat input (F-067)
- 993b283 rename: start.sh → start_local.sh
- 4d8d0ff agentA-word-count: implement sprint 27 tasks

**Files:** bot/chat_ui.html, scripts/start_local.sh (renamed from start.sh)

### agentB-deps-docs

Fixed pyproject.toml dev deps (B-035, B-036), Sprint 26 PROJECT_STATUS doc, dependency tests.

**Commits:**
- 3aeab85 fix: add providers to dev deps, generate Sprint 26 PROJECT_STATUS (B-035, B-036)
- fe1bf5a agentB-deps-docs: implement sprint 27 tasks

**Files:** pyproject.toml, docs/PROJECT_STATUS_2026-03-21-sprint26.md, tests/test_sprint27_deps.py

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-deps-docs | Fix dev deps (B-035, B-036), Sprint 26 PROJECT_STATUS | 1 | Clean | 4 |
| 2 | agentA-word-count | Word count indicator (F-067), start.sh rename | 1 | Clean | 3 |

---

## Backlog Snapshot

### Completed This Sprint
- F-067: Message character/word count indicator
- B-035: pyproject.toml [dev] group missing anthropic, openai, google-auth
- B-036: scripts/start.sh doesn't install optional deps

### Still Open
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-010: GitHub not configured in dashboard project entry
- B-015: Dashboard backlog counts show 0
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written
- B-029: Console shows 10 ONNX runtime warnings on every page load
- B-037: Bot says "I'm text-only" when user speaks via voice

---

## Test Results

690+ tests passing.

---

## Next Steps

- Fix bot personality not knowing about voice/STT/TTS capabilities (B-037)
- Update Docs panel stats to pull dynamically from /api/stats
