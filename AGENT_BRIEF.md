agentB-fact-extraction — Sprint 5

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 4 agents ran but merge conflicts dropped agent B's code: EvaluationRunner not importable, get_project_summary and add_to_backlog not in tools.py, CLI evaluate command missing
- Debug panel HTML exists in chat_ui.html (31 references) but tools it depends on aren't importable
- 56 tests pass but none cover the Sprint 4 features
- Personality, gateway, server, memory, save_discovery, Telegram polling all work
─────────────────────────────────────────

Sprint-Level Context

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
