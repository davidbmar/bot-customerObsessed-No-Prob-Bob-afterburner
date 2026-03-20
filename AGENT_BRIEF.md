agentA-eval-framework — Sprint 4

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 3: all 56 tests pass, save_discovery works, CLI chat/status commands work, e2e test proves conversation→seed doc pipeline
- Bot runs: personality loads (9 principles), gateway pipelines messages, memory persists, server starts on 1203
- Remaining roadmap items: evaluation framework, more tools, web chat polish
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add evaluation framework to test bot behavior against scenarios (F-005)
- Add web chat debug panel showing tools, principles, tokens, latency (F-010)
- Add more Afterburner tools: get_project_summary, add_to_backlog (F-003, F-012)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step)


Objective
- Build the evaluation framework that tests bot behavior against YAML scenario files

Tasks
- Create `evaluations/runner.py` with an `EvaluationRunner` class:
  - Loads YAML scenario files from `evaluations/scenarios/`
  - Each scenario defines: name, personality, messages (user inputs), expected_behaviors (what the bot should do)
  - Runs each scenario through the Gateway with a mock LLM (so tests don't need Ollama)
  - Checks responses against expected_behaviors using simple keyword/pattern matching
  - Returns pass/fail per scenario with details
- Update existing scenario files in `evaluations/scenarios/` (pushback.yaml, surface-request.yaml, vague-requirements.yaml) to match the runner's expected format:
  ```yaml
  name: "Pushback on vague feature request"
  personality: customer-discovery
  messages:
    - role: user
      content: "We need a dark mode"
  expected_behaviors:
    - "asks why" or "asks about the problem"
    - "does not immediately agree to build"
  ```
- Add `tests/test_evaluations.py` that runs all scenarios and verifies the runner works
- Add a CLI command: `python3 cli.py evaluate` that runs all scenarios and prints results

Acceptance Criteria
- `from evaluations.runner import EvaluationRunner` imports
- `python3 cli.py evaluate` runs scenarios and prints pass/fail
- `.venv/bin/python3 -m pytest tests/test_evaluations.py -v` passes
- At least 3 scenario files exist and are parseable
