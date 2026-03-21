# Sprint 38

Goal
- Verify worktree .venv symlink works — agents should complete successfully (test B-051 fix)
- Add tests for the new read_project_doc and list_projects tools

Constraints
- agentA owns `tests/test_tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files

Merge Order
1. agentB-session-doc
2. agentA-tool-tests

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-tool-tests

Objective
- Add tests for list_projects and read_project_doc tools

Tasks
- In `tests/test_tools.py`, add tests:
  - `test_tool_list_projects_returns_projects` — mock httpx.get to return project list, verify formatted output
  - `test_tool_list_projects_dashboard_offline` — mock httpx.get to raise ConnectError, verify error message
  - `test_tool_read_project_doc_reads_file` — create temp project dir with README.md, mock _find_project_root, verify file content returned
  - `test_tool_read_project_doc_blocks_traversal` — verify path traversal (../../etc/passwd) is blocked
  - `test_tool_read_project_doc_missing_file` — verify "File not found" for nonexistent path
  - `test_tool_registration_includes_list_projects` — verify list_projects is in TOOL_DEFINITIONS
  - `test_tool_registration_includes_read_project_doc` — verify read_project_doc is in TOOL_DEFINITIONS
- Run `.venv/bin/python3 -m pytest tests/ -x -q` to verify all tests pass

Acceptance Criteria
- All new tests pass
- All existing 726 tests still pass
- Total test count increases by 7+

## agentB-session-doc

Objective
- Create session doc for Sprint 38

Tasks
- Create `docs/project-memory/sessions/S-2026-03-21-2230-sprint38-tool-tests.md` using session template
- Document what Sprint 38 delivered: tests for list_projects and read_project_doc tools
- Reference the commits from this sprint

Acceptance Criteria
- Session doc exists with correct session ID and content
