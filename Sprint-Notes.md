# Sprint 28 — Agent Notes

*Started: 2026-03-21 19:03 UTC*

Phase 1 Agents: 2
- agentA-voice-personality
- agentB-docs-stats

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-voice-personality

*Completed: 2026-03-21 19:07 UTC*

### Files changed
- `personalities/customer-discovery.md` — added `## Capabilities` section with voice awareness
- `personalities/base.md` — added same `## Capabilities` section (all personalities inherit voice awareness)
- `bot/chat_ui.html` — added `id="docsStats"` to stats paragraph; updated `openDocs()` to fetch `/api/stats` dynamically with hardcoded fallback
- `docs/project-memory/backlog/README.md` — marked B-037 as Complete (Sprint 28)
- `docs/project-memory/sessions/S-2026-03-21-1906-voice-personality-dynamic-stats.md` — new session doc

### Commands run
- `git pull origin main` — already up to date
- `pytest tests/ -v` — 693 tests passed
- `git push -u origin HEAD` — branch pushed

### Notes / follow-on work
- The Capabilities section is in both `base.md` and `customer-discovery.md`. Since customer-discovery extends base, it's slightly redundant — but explicit is better than implicit for system prompt instructions that affect user experience.
- The `/api/stats` endpoint (F-060, Sprint 23) must be running for dynamic stats to work; the hardcoded fallback covers offline/dev scenarios.


---

## agentB-docs-stats

*Completed: 2026-03-21 19:07 UTC*

### Files changed
- `docs/PROJECT_STATUS_2026-03-21-sprint27.md` — **new** — Sprint 27 status doc covering deps fix (B-035, B-036) and word count indicator (F-067)
- `tests/test_personality.py` — **modified** — added `test_personality_knows_about_voice` asserting voice/speech/hear keywords present and text-only/can't hear absent (B-037)
- `docs/project-memory/sessions/S-2026-03-21-1906-sprint28-docs-voice-test.md` — **new** — session doc

### Commands run
- `git pull origin main` — already up to date
- `python3 -m pytest tests/ -v` — **694 passed** in 27s
- `git push -u origin HEAD` — pushed to `agentB-docs-stats`

### Notes / follow-on work
- The voice awareness test currently passes because "hearing" naturally appears in customer-discovery.md's conversation flow section. Once agentA adds explicit voice/STT/TTS capability text to the personality (B-037 fix), the test will serve as a stronger regression guard.
- Backlog was already up to date — B-035, B-036, F-067 all correctly marked Complete (Sprint 27).

