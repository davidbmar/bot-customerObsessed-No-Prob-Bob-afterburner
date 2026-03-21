agentB-docs-stats — Sprint 28

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 27: Fixed pyproject.toml deps, word count indicator, start.sh renamed
- 690+ tests pass
- Critical UX bug: bot tells users "I can't hear audio" while actively receiving their transcribed speech
- Voice works (STT + TTS) but personality prompt has no awareness of it
─────────────────────────────────────────

Sprint-Level Context

Goal
- Fix bot not knowing about its own voice capabilities — it says "I'm text-only" when user speaks via mic (B-037)
- Generate PROJECT_STATUS doc for Sprint 27
- Update Docs panel stats to pull from /api/stats dynamically

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html, personalities/ — agentB MUST NOT touch these
- agentB owns bot/server.py, tests/, docs/ — agentA MUST NOT touch these


Objective
- Generate PROJECT_STATUS doc for Sprint 27
- Add personality test for voice awareness

Tasks
1. **Generate PROJECT_STATUS doc**:
   - `docs/PROJECT_STATUS_2026-03-21-sprint27.md` — Sprint 27: Fixed deps, word count, start.sh rename
   - Follow PROJECT_STATUS_TEMPLATE.md format

2. **Add personality test for voice awareness**:
   - Test that `customer-discovery` personality system prompt contains voice-related keywords
   - Test it does NOT contain phrases like "text-only" or "can't hear"
   - ```python
     def test_personality_knows_about_voice():
         p = Personality('customer-discovery')
         prompt = p.system_prompt.lower()
         assert 'voice' in prompt or 'speech' in prompt or 'hear' in prompt
         assert 'text-only' not in prompt
         assert "can't hear" not in prompt
     ```

3. **Update backlog** — Verify items marked Complete

Acceptance Criteria
- PROJECT_STATUS doc exists for Sprint 27
- Voice awareness test passes
- All tests pass
