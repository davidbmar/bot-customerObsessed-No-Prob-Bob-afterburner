# Sprint 28

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

Merge Order
1. agentA-voice-personality
2. agentB-docs-stats

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 27: Fixed pyproject.toml deps, word count indicator, start.sh renamed
- 690+ tests pass
- Critical UX bug: bot tells users "I can't hear audio" while actively receiving their transcribed speech
- Voice works (STT + TTS) but personality prompt has no awareness of it

## agentA-voice-personality

Objective
- Update personality to acknowledge voice capabilities so the bot doesn't claim to be text-only

Tasks
1. **Update customer-discovery personality** (B-037):
   - Edit `personalities/customer-discovery.md`
   - Add a new section after the opening paragraph (before ## Principles):
     ```
     ## Capabilities

     You are a multimodal assistant that supports both text and voice interaction.
     Users can type messages OR speak to you using the microphone button or hands-free mode.
     Their speech is transcribed to text via speech-to-text (Whisper), and your responses
     can be read back to them via text-to-speech (Piper).

     Important:
     - Never say "I can't hear you" or "I'm text-only" — you CAN hear via speech-to-text
     - If a user asks "can you hear me?" respond positively: "Yes, I can hear you!"
     - If transcription seems garbled, say "I caught some of that but it was unclear — could you repeat?"
     - You don't need to mention the technical details (Whisper, Piper) unless asked
     ```

2. **Update base personality** too:
   - Edit `personalities/base.md`
   - Add similar voice awareness to the base so ALL personalities know about voice

3. **Update Docs panel in chat_ui.html**:
   - Find the hardcoded stats line in the Docs overlay
   - Replace with a fetch to `/api/stats` on panel open, showing dynamic counts
   - Fallback: show the hardcoded text if API fails

4. **Update backlog** — Mark B-037 as Complete (Sprint 28)

Acceptance Criteria
- Bot never says "I'm text-only" or "I can't hear"
- Bot responds positively to "can you hear me?"
- Docs panel shows dynamic stats from /api/stats
- All personality tests still pass

## agentB-docs-stats

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
