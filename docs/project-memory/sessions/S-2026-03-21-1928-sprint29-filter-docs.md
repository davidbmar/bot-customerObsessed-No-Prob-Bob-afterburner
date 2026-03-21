# S-2026-03-21-1928-sprint29-filter-docs

## Title
Sprint 29: Improve input quality filter for background noise detection (B-038)

## Goal
Add background media detection heuristics to the input filter so TV/movie audio is caught before reaching the LLM. Generate Sprint 28 PROJECT_STATUS doc.

## Context
Hands-free mode transcribes background TV/movie audio and sends it as user messages. The existing filter catches STT artifacts (short audio, hallucinations, garbage words) but not semantically valid text from background media.

## Plan
1. Add BACKGROUND_NOISE enum to InputQuality
2. Add three heuristics: long monologue (>200 words), repeated phrases (3+), no engagement markers
3. Update server.py to return friendly filter_message for background noise
4. Write comprehensive tests
5. Generate PROJECT_STATUS doc for Sprint 28
6. Update backlog B-038

## Changes Made
- `bot/input_filter.py`: Added BACKGROUND_NOISE enum value, BACKGROUND_NOISE_MESSAGE constant, three new detection functions (_has_repeated_phrases, _lacks_engagement_markers), and integrated them into classify()
- `bot/server.py`: Import BACKGROUND_NOISE_MESSAGE, return filter_message in response when quality is BACKGROUND_NOISE
- `tests/test_input_filter.py`: Added TestLongMonologue, TestRepeatedPhrases, TestNoEngagementMarkers, TestBackgroundNoiseMessage test classes (18 new tests)
- `docs/PROJECT_STATUS_2026-03-21-sprint28.md`: Sprint 28 status doc
- `docs/project-memory/backlog/README.md`: Marked B-038 as Complete (Sprint 29)

## Decisions Made
- Added BACKGROUND_NOISE as a new enum value rather than reusing GARBAGE — allows UI to show a distinct, friendly message instead of silently dropping
- Long monologue threshold set at >200 words — generous enough to not catch verbose users, but catches movie scenes
- Engagement markers include questions (?), greetings, and first-person pronouns — if ANY are present, the message passes through
- Repeated phrase detection uses 2-4 word ngrams with Counter — efficient and catches common media patterns
