# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 22: Conversation persistence, /api/projects, Active Project dropdown)

## Sprint 22 Summary

Sprint 22 goal: Fix conversation persistence — save/restore preserves markdown, sidebar refreshes on changes (B-030, B-031).
Additional: Wire config into Gateway and return projects as {slug, name} objects (B-028).
Additional: Conversation auto-save to sidebar (F-058).

---

## What Changed

### agentA-conversation-fixes

Conversation save/restore preserves markdown, sidebar refreshes on changes

**Commits:**
- ee26ef1 fix: conversation save/restore preserves markdown, sidebar refreshes on changes

**Files:** See git log for details

### agentB-server-api

Wire config into Gateway and return projects as {slug, name} objects

**Commits:**
- eebae58 fix: wire config into Gateway and return projects as {slug, name} objects (B-028)

**Files:** See git log for details

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts |
|---|--------|-------------|-------|-----------|
| 1 | agentB-server-api | Wire config into Gateway, projects API fix (B-028) | 1 | Clean |
| 2 | agentA-conversation-fixes | Conversation save/restore, sidebar refresh (B-030, B-031, F-058) | 1 | Clean |

---

## Backlog Snapshot

### Completed This Sprint
- F-058: Conversation auto-save to sidebar
- B-028: Active Project dropdown empty
- B-030: Conversation restore fails
- B-031: New conversations not saved to sidebar
- B-032: Docs panel stats hardcoded

### Still Open
- See backlog for current status

---

## Next Steps

- See sprint 23 brief for next planned work
