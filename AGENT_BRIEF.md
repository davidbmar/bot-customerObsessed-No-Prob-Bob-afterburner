agentB-docs-tests — Sprint 26

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 25: Stop generating button (F-064), Pause/Resume hands-free (F-065)
- 674 tests pass
- Bot UI is feature-rich: 68 features, voice, markdown, conversations, debug panel
- Long conversations hard to navigate — need scroll-to-bottom
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add scroll-to-bottom floating button for long conversations (F-066)
- Generate PROJECT_STATUS docs for Sprints 24-25 so dashboard stays current
- Add keyboard shortcuts help tooltip (F-068)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns bot/server.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Generate PROJECT_STATUS docs for Sprints 24-25
- Add tests for new features

Tasks
1. **Generate PROJECT_STATUS docs**:
   - `docs/PROJECT_STATUS_2026-03-21-sprint24.md` — Sprint 24: VAD settings, PROJECT_STATUS docs 20-23, tool error handling
   - `docs/PROJECT_STATUS_2026-03-21-sprint25.md` — Sprint 25: Stop generating button, Pause/Resume hands-free
   - Use `git log` for actual details
   - Follow `PROJECT_STATUS_TEMPLATE.md` format with merge table

2. **Add scroll-to-bottom test** (static HTML analysis):
   - Test that chat_ui.html contains scroll-to-bottom button element
   - Test that a scroll event listener exists for the messages container

3. **Update backlog** — Verify Sprint 26 items marked Complete

Acceptance Criteria
- PROJECT_STATUS docs exist for Sprints 24-25
- Dashboard rebuild shows Sprints 24-25
- All tests pass
