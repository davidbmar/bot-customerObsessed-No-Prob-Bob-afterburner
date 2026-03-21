agentA-word-count — Sprint 27

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 26: scroll-to-bottom FAB, keyboard shortcuts help
- 685 tests pass
- User hit login failure after venv rebuild — google-auth not in [dev] deps
- anthropic, openai also missing from [dev] — breaks LLM providers on fresh install
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix pyproject.toml dependencies so pip install -e ".[dev]" installs everything needed to run the bot (B-035, B-036)
- Add message character/word count indicator near input (F-067)
- Generate PROJECT_STATUS doc for Sprint 26

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns pyproject.toml, bot/server.py, scripts/, tests/, docs/ — agentA MUST NOT touch these


Objective
- Add a subtle word/character count indicator near the text input

Tasks
1. **Message word count indicator** (F-067):
   - Add a small, muted text element below or beside the input field
   - Show word count and approximate token count as the user types
   - Format: "42 words · ~56 tokens" (estimate tokens as words × 1.3)
   - Only show when input has text (hide when empty)
   - Style: font-size 11px, color var(--text-muted), right-aligned below input
   - Update on every `input` event

2. **Update backlog** — Mark F-067 as Complete (Sprint 27)

Acceptance Criteria
- Type text → word count appears below input
- Clear text → count disappears
- Count updates in real-time as you type
