# Sprint 39

Goal
- Add tests for list_projects, read_project_doc, and the enriched get_project_summary tools
- Generate PROJECT_STATUS doc for Sprint 38

Constraints
- agentA owns `tests/test_tools.py` exclusively
- agentB owns `docs/` files exclusively
- No two agents may modify the same files

Merge Order
1. agentB-sprint38-doc
2. agentA-new-tool-tests

Merge Verification
- .venv/bin/python3 -m pytest tests/ -x -q

## agentA-new-tool-tests

Objective
- Add comprehensive tests for list_projects, read_project_doc, and the enriched get_project_summary

Tasks
- In `tests/test_tools.py`, import `tool_list_projects` and `tool_read_project_doc` from `bot.tools`
- Add these tests:
  1. `test_tool_list_projects_returns_formatted_list` — mock httpx.get to return project data, verify "Registered projects:" header and project entries in output
  2. `test_tool_list_projects_dashboard_offline` — mock httpx.get to raise ConnectError, verify "Dashboard unavailable" message
  3. `test_tool_read_project_doc_reads_readme` — create tmp dir with README.md, mock `_find_project_root` to return it, call `tool_read_project_doc(slug="test", path="README.md")`, verify content
  4. `test_tool_read_project_doc_blocks_path_traversal` — call with `path="../../etc/passwd"`, verify "Cannot read files outside" message
  5. `test_tool_read_project_doc_missing_file` — call with `path="nonexistent.md"`, verify "File not found" message
  6. `test_tool_read_project_doc_missing_project` — call with unknown slug, verify "not found" message
  7. `test_tool_registration_includes_list_projects` — verify "list_projects" in TOOL_DEFINITIONS names
  8. `test_tool_registration_includes_read_project_doc` — verify "read_project_doc" in TOOL_DEFINITIONS names
  9. `test_execute_tool_dispatches_list_projects` — verify execute_tool routes correctly
  10. `test_get_project_summary_includes_sprint_data` — mock httpx.get for status API, verify sprint data included in output
- Run `.venv/bin/python3 -m pytest tests/test_tools.py -v` to verify

Acceptance Criteria
- All 10 new tests pass
- All existing tests still pass
- Test count increases from 726 to 736+

## agentB-sprint38-doc

Objective
- Generate PROJECT_STATUS doc for Sprint 38

Tasks
- Create `docs/PROJECT_STATUS_2026-03-21-sprint38.md` following PROJECT_STATUS_TEMPLATE format
  - Sprint 38 goal: verify worktree .venv symlink, add tool tests
  - Agents: agentA-tool-tests, agentB-session-doc
  - The sprint proved the .venv symlink works — agents ran and tests passed in worktrees
  - Use git log between `61cb4aa` and `d06f85a` for details
- Create a session doc for this sprint

Acceptance Criteria
- PROJECT_STATUS doc exists with correct merge table
- Dashboard shows Sprint 38 after rebuild
