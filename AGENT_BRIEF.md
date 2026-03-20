agentA-fixes-and-polish — Sprint 9

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 8: multi-project support, generate_vision tool, feedback_on_sprint tool — 129 tests pass
- Bugs found: B-011 (CLI status crashes on projects.json format), B-012 (tool naming inconsistency)
- generate_vision and feedback_on_sprint both exist and work, but CLI status can't load config
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix CLI status crash (B-011) and tool naming inconsistency (B-012)
- Add conversation export (F-016) and personality hot-reload (F-017)
- Harden the bot for real usage

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent to avoid merge conflicts


Objective
- Fix crashes, add conversation export, personality hot-reload

Tasks
1. Fix `bot/config.py` `_auto_discover_projects()` (B-011):
   - The function reads dashboard projects.json but expects dict entries where projects.json has a different format
   - Read the actual projects.json format: it's a list of objects with `slug`, `name`, `rootPath` fields
   - Parse correctly: `{slug: rootPath}` mapping
   - Make it graceful: if projects.json doesn't exist or is malformed, return empty dict instead of crashing
   - Test: `python3 cli.py status` must work without crashing

2. Normalize tool naming (B-012):
   - Ensure all tool functions follow `verb_noun` pattern consistently
   - Current tools: save_discovery, get_project_summary, add_to_backlog, get_sprint_status, generate_vision, feedback_on_sprint
   - These are fine — just make sure exports and TOOL_DEFINITIONS use consistent names
   - Add `feedback_on_sprint` to the `__all__` or ensure it's importable

3. Add conversation export (F-016):
   - New endpoint: `GET /api/conversations/export?conversation_id=X` — returns full conversation as markdown
   - Format: `# Conversation {id}\n\n**User:** message\n\n**Bot:** response\n\n---\n\n` for each exchange
   - Add "Export" button to chat UI that downloads the markdown file
   - Add `export` subcommand to cli.py: `python3 cli.py export <conversation_id>` — prints markdown to stdout

4. Add personality hot-reload (F-017):
   - New endpoint: `POST /api/personality/reload` — re-reads personality files without restarting server
   - Gateway stores personality loader reference, reload method re-reads from disk
   - Add "Reload Personality" button to settings panel in chat UI
   - Useful when editing personality docs while bot is running

5. Write tests for all new features — target 140+ tests total

6. Update backlog: mark B-011, B-012, F-016, F-017 as Complete (Sprint 9)

Acceptance Criteria
- `python3 cli.py status` works without crashing
- `GET /api/conversations/export?conversation_id=test` returns markdown
- `POST /api/personality/reload` re-reads personality files
- `.venv/bin/python3 -m pytest tests/ -v` — 140+ tests, 0 failures
- Backlog updated
