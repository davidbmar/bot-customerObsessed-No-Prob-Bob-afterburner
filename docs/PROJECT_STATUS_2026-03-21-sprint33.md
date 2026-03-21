# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 33: Auto-rebuild, Sprint 32 doc, Active Project dropdown)

## Sprint 33 Summary

Sprint 33 implemented auto-rebuild after merge (F-074), generated the missing Sprint 32 PROJECT_STATUS doc (B-047), and fixed the Active Project dropdown to show project names instead of [object Object] (B-045, F-075). agentA fixed the dropdown display bug in chat_ui.html. agentB generated the Sprint 32 doc and verified auto-rebuild functionality.

---

## What Changed

### agentA-project-dropdown

Fixed Active Project dropdown in Settings panel showing [object Object] instead of project names (B-045, F-075). Updated chat_ui.html to correctly render project names in the dropdown.

**Commits:**
- 43a3070 agentA-project-dropdown: implement sprint 33 tasks
- 2157548 fix: Active Project dropdown shows project names instead of [object Object] (B-045, F-075)

**Files:** bot/chat_ui.html, docs/project-memory/sessions/S-2026-03-21-2114-fix-project-dropdown.md

### agentB-auto-rebuild

Generated the missing Sprint 32 PROJECT_STATUS doc and verified auto-rebuild after merge (B-047, F-074).

**Commits:**
- 22186c8 agentB-auto-rebuild: implement sprint 33 tasks
- 50b3488 feat: generate Sprint 32 PROJECT_STATUS doc + verify auto-rebuild (B-047, F-074)

**Files:** docs/PROJECT_STATUS_2026-03-21-sprint32.md, docs/project-memory/sessions/S-2026-03-21-2112-sprint33-auto-rebuild.md

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-auto-rebuild | Sprint 32 doc + auto-rebuild verify (B-047, F-074) | 1 | Clean | 4 |
| 2 | agentA-project-dropdown | Active Project dropdown fix (B-045, F-075) | 1 | Clean | 4 |

---

## Backlog Snapshot

### Completed This Sprint
- B-045: Active Project dropdown in Settings panel is empty
- B-047: Missing PROJECT_STATUS doc for Sprint 32
- F-074: Auto-rebuild dashboard data after sprint merges
- F-075: Active Project dropdown shows project names

### Still Open
- B-010: GitHub not configured in dashboard project entry
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written
- B-046: Bot reports stale sprint data until rebuild runs
- B-048: sprint-config venv test issues

---

## Next Steps

- Fix sprint-config venv test (B-048)
- Further Active Project dropdown improvements (F-075)
- Address stale sprint data reporting (B-046)
