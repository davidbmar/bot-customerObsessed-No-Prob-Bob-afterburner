# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 26: Scroll-to-bottom FAB, Keyboard shortcuts help)

## Sprint 26 Summary

Sprint 26 added a scroll-to-bottom floating action button (F-066) that appears when the user scrolls up in long conversations, letting them jump back to the latest message with one click. Also added a keyboard shortcuts help tooltip (F-068) listing available shortcuts (Enter=send, Escape=stop speaking, etc.). agentB generated PROJECT_STATUS docs for Sprints 24-25 and added scroll FAB tests.

---

## What Changed

### agentA-scroll-shortcuts

Scroll-to-bottom FAB (F-066) and keyboard shortcuts help tooltip (F-068).

**Commits:**
- 84ec4d2 feat: add scroll-to-bottom FAB (F-066) and keyboard shortcuts help (F-068)
- 04ea29b agentA-scroll-shortcuts: implement sprint 26 tasks

**Files:** chat_ui.html updated with FAB button and shortcuts modal

### agentB-docs-tests

PROJECT_STATUS docs for Sprints 24-25, scroll FAB integration tests.

**Commits:**
- f184d89 feat: PROJECT_STATUS docs for Sprints 24-25, scroll FAB tests (Sprint 26)
- 1c32a79 agentB-docs-tests: implement sprint 26 tasks

**Files:** tests/test_sprint26_scroll_fab.py, docs/PROJECT_STATUS_2026-03-21-sprint24.md, docs/PROJECT_STATUS_2026-03-21-sprint25.md

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts | Files Changed |
|---|--------|-------------|-------|-----------|---------------|
| 1 | agentB-docs-tests | Sprint 24-25 PROJECT_STATUS docs, scroll FAB tests | 1 | Clean | 4 |
| 2 | agentA-scroll-shortcuts | Scroll FAB (F-066), Shortcuts help (F-068) | 1 | Clean | 1 |

---

## Backlog Snapshot

### Completed This Sprint
- F-066: Scroll-to-bottom FAB
- F-068: Keyboard shortcuts help

### Still Open
- F-067: Message character/word count
- B-008: sprint-run.sh crashes with `local -A` on zsh
- B-035: pyproject.toml [dev] group missing anthropic, openai, google-auth
- B-036: scripts/start.sh doesn't install optional deps

---

## Test Results

685 tests passing.

---

## Next Steps

- Fix pyproject.toml dependency groups so fresh installs work (B-035, B-036)
- Add message character/word count indicator (F-067)
