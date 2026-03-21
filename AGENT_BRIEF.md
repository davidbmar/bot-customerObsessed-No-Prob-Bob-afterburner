agentB-deps-docs — Sprint 27

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
- Fix dependency groups so a fresh install works out of the box
- Generate PROJECT_STATUS doc for Sprint 26

Tasks
1. **Fix pyproject.toml dependency groups** (B-035):
   - Add a new `[project.optional-dependencies]` group called `providers`:
     ```
     providers = [
         "anthropic>=0.30",
         "openai>=1.30",
     ]
     ```
   - Update `dev` group to include providers and auth:
     ```
     dev = [
         "pytest>=8.0",
         "pytest-asyncio>=0.23",
         "anthropic>=0.30",
         "openai>=1.30",
         "google-auth[requests]>=2.20",
     ]
     ```
   - Update `all` group to include providers too
   - This ensures `pip install -e ".[dev]"` gives you everything needed to run AND test

2. **Update scripts/start.sh** (B-036):
   - After the venv creation/activation step, change `pip install -e .` to `pip install -e ".[dev]"`
   - This ensures start.sh installs test deps + providers + auth on first run

3. **Generate PROJECT_STATUS doc for Sprint 26**:
   - Create `docs/PROJECT_STATUS_2026-03-21-sprint26.md`
   - Sprint 26: scroll-to-bottom FAB, keyboard shortcuts help
   - Follow PROJECT_STATUS_TEMPLATE.md format

4. **Write test for dependency completeness**:
   - Test that all expected modules can be imported:
     ```python
     def test_anthropic_importable():
         import anthropic
     def test_google_auth_importable():
         from google.oauth2 import id_token
     ```

5. **Update backlog** — Mark B-035, B-036 as Complete (Sprint 27)

Acceptance Criteria
- `pip install -e ".[dev]"` installs anthropic, openai, google-auth
- `python -c "import anthropic; from google.oauth2 import id_token; print('ok')"` works
- scripts/start.sh uses `.[dev]` for install
- PROJECT_STATUS doc exists for Sprint 26
- All tests pass
