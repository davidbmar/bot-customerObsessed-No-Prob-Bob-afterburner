# Sprint 37

Goal
- Fix sprint agent worktrees to symlink .venv so agents can run tests (B-051, F-077)
- Generate PROJECT_STATUS docs for Sprints 33-36 so dashboard is complete (B-049)

Constraints
- agentA owns `.sprint/scripts/sprint-init.sh` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files

Merge Order
1. agentB-sprint-docs
2. agentA-worktree-venv

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-worktree-venv

Objective
- Fix sprint agent worktrees so agents can run tests and install packages (B-051, F-077)

Tasks
- In `.sprint/scripts/sprint-init.sh`, after creating each worktree with `git worktree add`, add a symlink to the project's .venv:
  ```bash
  ln -sf "${PROJECT_ROOT}/.venv" "${WORKTREE_DIR}/.venv"
  ```
- This allows agents in worktrees to run `.venv/bin/python3 -m pytest` without errors
- Also symlink `node_modules` if it exists (for JS projects)
- Add a comment explaining why the symlink is needed
- Test: verify that `.venv/bin/python3 -c "import pytest"` works in a worktree

Acceptance Criteria
- After `sprint-init.sh` creates worktrees, each has a `.venv` symlink pointing to the main project's venv
- Agents can run `.venv/bin/python3 -m pytest tests/ -x -q` in worktrees
- Existing sprint-init.sh functionality (branch creation, AGENT_BRIEF.md) still works

## agentB-sprint-docs

Objective
- Generate PROJECT_STATUS docs for Sprints 33-36 (B-049)

Tasks
- Create docs for each sprint using PROJECT_STATUS_TEMPLATE format:
  - `docs/PROJECT_STATUS_2026-03-21-sprint33.md` — Sprint 33: auto-rebuild (F-074), Sprint 32 doc (B-047), Active Project dropdown (F-075). Agents: agentA-project-dropdown, agentB-auto-rebuild
  - `docs/PROJECT_STATUS_2026-03-21-sprint34.md` — Sprint 34: sprint-config venv test (B-048 partial), Active Project fix attempt. Agents: agentA-project-fix, agentB-config-docs
  - `docs/PROJECT_STATUS_2026-03-21-sprint35.md` — Sprint 35: UI polish attempt (agents had minimal output). Agents: agentA-ui-polish, agentB-test-cmd-docs
  - `docs/PROJECT_STATUS_2026-03-21-sprint36.md` — Sprint 36: list_projects tool (F-076 partial). Agents: agentA-list-projects, agentB-sprint-docs
- Use git log for commit details between sprint boundaries
- Create a session doc for this sprint

Acceptance Criteria
- All four PROJECT_STATUS docs exist with correct summaries and merge tables
- Dashboard shows 36 sprints after rebuild
