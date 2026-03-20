agentA-multi-project-vision — Sprint 8

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 7: web chat polished — debug panel shows real data (principles, tokens, latency, facts), settings panel (switch personality/model), typing indicator, timestamps, markdown rendering, get_sprint_status tool. 100 tests pass.
- All Phase 1+2 features complete. Phase 3 roadmap: multi-project, voice, customer profiles.
- Backlog: F-013 (multi-project), F-014 (feedback loop), F-015 (generate_vision) are highest priority planned items.
─────────────────────────────────────────

Sprint-Level Context

Goal
- Multi-project support — bot can work with multiple Afterburner projects (F-013)
- generate_vision tool — bot synthesizes discovery conversation into Vision doc (F-015)
- Post-sprint feedback loop (F-014)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent to avoid merge conflicts


Objective
- Add multi-project support, generate_vision tool, and post-sprint feedback

Tasks
1. Multi-project support in `bot/config.py` (F-013):
   - Add `projects` dict to BotConfig: maps project slug → project root path
   - Add `active_project` field — the currently selected project
   - Method: `add_project(slug, root_path)` — registers a project
   - Method: `switch_project(slug)` — changes active project
   - Method: `list_projects() -> list[str]` — returns registered slugs
   - Default: auto-discover from `~/.config/afterburner/registry.json` if it exists, or from Afterburner dashboard projects.json
   - Save projects to config file so they persist

2. Update `bot/tools.py` — all project-aware tools (save_discovery, get_project_summary, add_to_backlog, get_sprint_status) should use `config.active_project` as the default project root instead of hardcoded paths

3. Add `generate_vision` tool to `bot/tools.py` (F-015):
   - Takes structured discovery data (problem, users, use_cases, differentiators, success_criteria)
   - Generates a Vision markdown document following Afterburner format (Product Name, Problem Statement, Target Audience, Key Differentiators, Solution Overview, Success Criteria, FAQ)
   - Writes to active project's `docs/lifecycle/VISION.md`
   - Register as LLM tool

4. Add post-sprint feedback to `bot/gateway.py` (F-014):
   - New method: `feedback_on_sprint(project_slug)` — reads latest PROJECT_STATUS doc and summarizes what was shipped
   - Returns structured summary the bot can present: "Here's what Sprint N shipped: [deliverables]. Does this match what you expected?"
   - Add as a tool the LLM can call

5. Add API endpoints to `bot/server.py`:
   - `GET /api/projects` — list registered projects
   - `POST /api/projects/switch` — switch active project
   - Update settings panel in chat_ui.html to show project selector

6. Write tests:
   - `tests/test_tools.py`: test generate_vision writes correct markdown
   - `tests/test_config.py`: test multi-project config (add, switch, list)
   - Target: 110+ tests

7. Update backlog: mark F-013, F-014, F-015 as Complete (Sprint 8)

Acceptance Criteria
- `from bot.tools import generate_vision` works
- Bot can switch between projects and tools use the active project
- generate_vision writes a valid Vision doc to the active project
- Settings panel shows project selector
- `.venv/bin/python3 -m pytest tests/ -v` — 110+ tests, 0 failures
- Backlog updated
