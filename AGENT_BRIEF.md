agentA-list-projects — Sprint 36

Previous Sprint Summary
─────────────────────────────────────────
# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 32: ONNX suppress, Sprint docs, zsh fix)

## Sprint 32 Summary

Sprint 32 suppressed noisy ONNX runtime console warnings during Silero VAD initialization (B-044), generated missing PROJECT_STATUS docs for Sprints 30-31 so the dashboard shows all recent sprint history (B-043, F-073), and fixed the sprint-run.sh `local -A` crash on zsh (B-008). agentA suppressed ONNX warnings in chat_ui.html. agentB generated the Sprint 30-31 docs, cleaned up Sprint-Notes.md, and patched sprint-run.sh for zsh compatibility.

---

## What Changed

### agentA-onnx-suppress

Suppressed ONNX runtime console warnings that fired on every page load when Silero VAD initializes (B-044). The WASM compilation warnings happen before JS config takes effect, so the fix intercepts console.warn during VAD init.

**Commits:**
- 0888ff3 agentA-onnx-suppress: implement sprint 32 tasks
- 090be1c feat: suppress ONNX runtime console warnings from Silero VAD init (B-044)

**Files:** bot/chat_ui.html

### agentB-sprint-docs

Generated PROJECT_STATUS docs for Sprints 30-31 so dashboard shows all recent history (B-043, F-073). Fixed sprint-run.sh `local -A` crash on zsh (B-008) by replacing associative array syntax with POSIX-compatible alternatives. Cleaned up Sprint-Notes.md.

**Commits:**
- 45cd790 agentB-sprint-docs: implement sprint 32 tasks
- f675e05 feat: generate Sprint 30-31 PROJECT_STATUS docs + fix zsh crash (B-008, B-043, F-073)

**Files:** docs/PROJECT_STATUS_2026-03-21-sprint30.md, docs/PROJECT_STATUS_2026-03-21-sprint31.md, .sprint/scripts/sprint-run.sh, Sprint-Notes.md

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-sprint-docs | Sprint 30-31 docs + zsh fix (B-008, B-043, F-073) | 1 | Clean | 8 |
| 2 | agentA-onnx-suppress | ONNX warning suppression (B-044) | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-043: Missing PROJECT_STATUS docs for Sprints 30-31
- B-044: ONNX warnings still fire despite ort.env.logLevel='error'
- F-073: Generate PROJECT_STATUS docs for Sprints 30-31

### Still Open
- B-010: GitHub not configured in dashboard project entry
- B-016: Ollama Qwen 3.5 response latency ~22s
- B-020: Sprint 12 agent done markers not written
- B-045: Active Project dropdown in Settings panel is empty
- B-046: Bot reports stale sprint data until rebuild runs
- B-047: Missing PROJECT_STATUS doc for Sprint 32

---

## Test Results

700+ tests passing.

---

## Next Steps

- Auto-rebuild dashboard data after sprint merges (F-074, B-046)
- Generate PROJECT_STATUS doc for Sprint 32 (B-047)
- Fix Active Project dropdown (B-045, F-075)
─────────────────────────────────────────

Sprint-Level Context

Goal
- Generate PROJECT_STATUS docs for Sprints 33-35 so dashboard is complete (B-049)
- Add "list all projects" capability to bot tools so users can ask "what projects are there?" (F-076)

Constraints
- agentA owns `bot/tools.py` and `bot/llm.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files


Objective
- Add a `list_projects` tool the bot can call when users ask "what projects are there?" (F-076)

Tasks
- In `bot/tools.py`, add a `tool_list_projects()` function that calls `list_project_slugs()` (already exists) and returns a formatted list with slug + name for each project
- In `bot/llm.py`, add `list_projects` to the `TOOL_DEFINITIONS` array with description "List all registered Afterburner projects"
- In `bot/tools.py`, add `list_projects` to the `execute_tool` dispatch dict
- Add tests in `tests/test_tools.py`:
  - Test that `tool_list_projects()` returns formatted project list when dashboard is available
  - Test that `tool_list_projects()` returns error message when dashboard is unavailable
  - Test that `list_projects` is in `TOOL_DEFINITIONS`

Acceptance Criteria
- User asks "what projects are there?" and bot calls list_projects tool
- Tool returns formatted list of all registered projects with slugs and names
- All existing + new tests pass
