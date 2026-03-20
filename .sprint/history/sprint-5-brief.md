# Sprint 5

Goal
- Fix Sprint 4 merge damage: eval framework, get_project_summary, add_to_backlog all failed to land
- Ensure all tools are importable and tested
- Add CLI evaluate command
- Bring test count above 60

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Do NOT create new files if the function already exists somewhere — check first and fix the import/export

Merge Order
1. agentA-fix-eval-tools
2. agentB-fact-extraction

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from evaluations.runner import EvaluationRunner; print('Eval: OK')"
.venv/bin/python3 -c "from bot.tools import save_discovery, get_project_summary, add_to_backlog; print('Tools: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 4 agents ran but merge conflicts dropped agent B's code: EvaluationRunner not importable, get_project_summary and add_to_backlog not in tools.py, CLI evaluate command missing
- Debug panel HTML exists in chat_ui.html (31 references) but tools it depends on aren't importable
- 56 tests pass but none cover the Sprint 4 features
- Personality, gateway, server, memory, save_discovery, Telegram polling all work

## agentA-fix-eval-tools

Objective
- Fix all Sprint 4 features that failed to merge: evaluation framework, tools, CLI evaluate

Tasks
- Fix `evaluations/runner.py`: check what class/function names exist and either rename to `EvaluationRunner` or update imports. The file exists but exports the wrong name. Make `from evaluations.runner import EvaluationRunner` work
- Add or fix `get_project_summary` in `bot/tools.py`: reads Vision, Plan, Roadmap from a project's `docs/lifecycle/` directory and returns a summary dict. Register as LLM tool in the tool definitions
- Add or fix `add_to_backlog` in `bot/tools.py`: appends a bug or feature to a project's `docs/project-memory/backlog/README.md`. Auto-assigns next ID. Register as LLM tool
- Add `evaluate` subcommand to `cli.py`: loads scenarios from `evaluations/scenarios/`, runs them through EvaluationRunner, prints pass/fail results
- Write tests in `tests/test_evaluations.py` for the evaluation runner
- Write tests in `tests/test_tools.py` for get_project_summary and add_to_backlog
- Update backlog: mark F-003, F-005, F-010, F-012 status correctly

Acceptance Criteria
- `from evaluations.runner import EvaluationRunner` works
- `from bot.tools import get_project_summary, add_to_backlog` works
- `python3 cli.py evaluate` runs and prints results
- `.venv/bin/python3 -m pytest tests/ -v` — 60+ tests, 0 failures
- Backlog reflects actual state of all features

## agentB-fact-extraction

Objective
- Add fact extraction from conversations (F-006) — the LLM summarizes key facts from chat history

Tasks
- Add `bot/facts.py` with a `FactExtractor` class:
  - Method: `extract(conversation_history) -> list[dict]` — takes message list, returns facts
  - Each fact: `{"category": "problem|user|use_case|constraint", "content": "...", "confidence": 0.0-1.0}`
  - Uses simple keyword/pattern matching for now (no LLM call needed) — look for phrases like "the problem is", "our users", "we need", "must not"
  - Method: `summarize(facts) -> str` — produces a markdown summary of extracted facts
- Integrate fact extraction into Gateway: after each assistant response, run fact extraction on the full conversation and store facts alongside conversation memory
- Add `facts` field to the /api/chat response so the debug panel can display extracted facts
- Update `bot/chat_ui.html` debug panel to show extracted facts section
- Write tests in `tests/test_facts.py`:
  - Extract facts from sample conversation
  - Categorization works (problem, user, use_case)
  - Empty conversation returns empty facts
- Update backlog: mark F-006 as Complete

Acceptance Criteria
- `from bot.facts import FactExtractor` works
- Facts are returned in /api/chat response
- `.venv/bin/python3 -m pytest tests/test_facts.py -v` passes
- Backlog updated
