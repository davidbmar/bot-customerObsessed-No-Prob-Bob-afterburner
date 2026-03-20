# Sprint 6

Goal
- Add evaluation runner, get_project_summary tool, add_to_backlog tool, and fact extraction
- These were planned in Sprints 4-5 but merge issues prevented them from landing
- Keep it simple: one agent does all the work to avoid merge conflicts

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Do NOT modify files that already work (personality.py, memory.py, llm.py, etc.)
- Focus on NEW files and adding functions to existing tools.py

Merge Order
1. agentA-all-features

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from evaluations.runner import EvaluationRunner; print('Eval: OK')"
.venv/bin/python3 -c "from bot.tools import save_discovery, get_project_summary, add_to_backlog; print('All tools: OK')"
.venv/bin/python3 -c "from bot.facts import FactExtractor; print('Facts: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -3
```

Previous Sprint
- Sprints 4-5 agents failed to produce code changes (only modified AGENT_BRIEF.md)
- Core works: personality (9 principles), gateway, server (port 1203), memory (JSONL), save_discovery tool, Telegram polling, CLI chat/status
- 56 tests pass
- Missing: EvaluationRunner class, get_project_summary, add_to_backlog, FactExtractor, CLI evaluate

## agentA-all-features

Objective
- Implement all remaining Phase 2 features in one shot

Tasks
1. Fix `evaluations/runner.py` — the file exists but exports wrong names. Check what's in it:
   - Read the file, find what class/function names exist
   - Either rename the class to `EvaluationRunner` or create a new one
   - `EvaluationRunner` should: load YAML scenarios from `evaluations/scenarios/`, run them with a mock LLM, check responses against expected behaviors
   - Write `tests/test_evaluations.py` with at least 3 tests

2. Add `get_project_summary` function to `bot/tools.py`:
   - Reads Vision.md, Plan.md, Roadmap.md from a project's docs/lifecycle/
   - Returns dict with title, problem, appetite, sprint_candidates
   - Register in TOOL_DEFINITIONS list
   - Add test in tests/test_tools.py

3. Add `add_to_backlog` function to `bot/tools.py`:
   - Reads current backlog README.md, finds highest B-NNN or F-NNN, increments
   - Appends new row to the appropriate table (bugs or features)
   - Register in TOOL_DEFINITIONS list
   - Add test in tests/test_tools.py

4. Create `bot/facts.py` with `FactExtractor` class:
   - `extract(messages) -> list[dict]` — pattern-match for problems, users, use cases
   - Look for phrases: "the problem is", "our users", "we need", "must not", "the goal is"
   - Each fact: `{"category": "problem"|"user"|"use_case"|"constraint", "content": "...", "confidence": 0.8}`
   - `summarize(facts) -> str` — markdown summary
   - Write `tests/test_facts.py` with at least 4 tests

5. Add `evaluate` subcommand to `cli.py`:
   - Loads EvaluationRunner, runs all scenarios, prints pass/fail
   - Exit code 0 if all pass, 1 if any fail

6. Update `docs/project-memory/backlog/README.md`:
   - Mark F-003, F-005, F-006, F-012 as Complete (Sprint 6)

Acceptance Criteria
- `from evaluations.runner import EvaluationRunner` works
- `from bot.tools import save_discovery, get_project_summary, add_to_backlog` works
- `from bot.facts import FactExtractor` works
- `python3 cli.py evaluate` runs and exits
- `.venv/bin/python3 -m pytest tests/ -v` — 65+ tests, 0 failures
- Backlog updated
