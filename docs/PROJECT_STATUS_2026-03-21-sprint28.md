# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 28: Voice personality awareness, dynamic Docs stats)

## Sprint 28 Summary

Sprint 28 added voice/STT/TTS awareness to all personality system prompts (B-037) so the bot no longer says "I'm text-only" when users speak via voice. Also updated the Docs panel in chat_ui.html to pull sprint/test/feature counts dynamically from /api/stats instead of hardcoded values. agentB generated the Sprint 27 PROJECT_STATUS doc and added a personality voice-awareness test.

---

## What Changed

### agentA-voice-personality

Added voice awareness instructions to base.md and customer-discovery.md personality files (B-037). Updated Docs panel stats to fetch dynamically from /api/stats.

**Commits:**
- 0bbd4ac feat: add voice awareness to personalities + dynamic Docs stats (B-037)
- 9d93e15 agentA-voice-personality: implement sprint 28 tasks

**Files:** personalities/base.md, personalities/customer-discovery.md, bot/chat_ui.html

### agentB-docs-stats

Generated Sprint 27 PROJECT_STATUS doc and added personality voice-awareness test.

**Commits:**
- ea3e53a feat: Sprint 27 PROJECT_STATUS doc, voice awareness test (B-037)
- 35e9f63 agentB-docs-stats: implement sprint 28 tasks

**Files:** docs/PROJECT_STATUS_2026-03-21-sprint27.md, tests/test_personality.py, docs/project-memory/backlog/README.md

### Post-merge fix

- ce59f52 fix: rephrase voice instruction to avoid 'text-only' literal in prompt

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-docs-stats | Sprint 27 PROJECT_STATUS, voice awareness test | 1 | Clean | 3 |
| 2 | agentA-voice-personality | Voice personality awareness (B-037), dynamic Docs stats | 1 | Clean | 3 |

---

## Backlog Snapshot

### Completed This Sprint
- B-037: Bot says "I'm text-only" when user speaks via voice

### Still Open
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-010: GitHub not configured in dashboard project entry
- B-015: Dashboard backlog counts show 0
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written
- B-029: Console shows 10 ONNX runtime warnings on every page load
- B-038: Input filter lets TV/movie audio through

---

## Test Results

690+ tests passing.

---

## Next Steps

- Improve input quality filter to catch TV/movie background audio (B-038)
- Add "discard" button for voice transcriptions before sending
