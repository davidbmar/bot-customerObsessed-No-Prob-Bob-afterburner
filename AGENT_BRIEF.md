agentA-eval-expansion — Sprint 15

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 14: conversation sidebar, token count fix, provider label fix, cost display. 271 tests pass.
- Evaluation framework exists with 3 scenarios (surface-request, vague-requirements, pushback)
- Sidebar shows past conversations with first message preview, timestamp, message count
- Published to CloudFront: https://d3gb25yycyv0d9.cloudfront.net
─────────────────────────────────────────

Sprint-Level Context

Goal
- Add more evaluation scenarios — expand from 3 to 8+ scenarios with diverse customer types (F-035)
- Delete conversation from sidebar — right-click or swipe to remove old chats (F-036)
- Search conversations — filter sidebar by keyword (F-037)
- Dark/light theme toggle (F-038)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- agentA owns evaluations/ and tests/ — agentB MUST NOT touch these
- agentB owns bot/chat_ui.html ONLY — agentA MUST NOT touch chat_ui.html


Objective
- Expand evaluation scenarios to test more customer types and edge cases

Tasks
1. **Add 5+ new evaluation scenarios** in `evaluations/scenarios/`:
   - `technical-customer.yaml` — customer who speaks in technical jargon ("we need a REST API with OAuth2")
     - Pass: bot asks about the users of the API, not just the tech specs
   - `emotional-customer.yaml` — frustrated customer ("nothing works, this is terrible")
     - Pass: bot acknowledges frustration before diving into discovery
   - `multi-problem.yaml` — customer describes 3 problems at once
     - Pass: bot helps prioritize, doesn't try to solve all at once
   - `solution-fixated.yaml` — customer insists on a specific solution ("we need React Native")
     - Pass: bot asks what problem the solution is meant to solve
   - `returning-customer.yaml` — customer references a previous conversation
     - Pass: bot acknowledges continuity and builds on prior context
   - `enterprise-customer.yaml` — customer mentions compliance, security, audit requirements
     - Pass: bot captures non-functional requirements alongside functional ones

2. **Add tests for new scenarios**:
   - Test each scenario loads correctly
   - Test pass/fail criteria are well-formed
   - Target: 285+ total tests

3. **Update backlog** — Mark F-035 as Complete (Sprint 15)

Acceptance Criteria
- `ls evaluations/scenarios/*.yaml | wc -l` returns 8+
- All scenarios have name, input, principles_tested, pass_criteria, fail_criteria
- `.venv/bin/python3 -m pytest tests/ -v` — 285+ tests, 0 failures
