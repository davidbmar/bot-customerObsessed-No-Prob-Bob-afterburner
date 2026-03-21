# Session

Session-ID: S-2026-03-21-0617-sprint20-input-filter-fastpath
Title: Sprint 20 — Input quality filter and fast path
Date: 2026-03-21
Author: agentA

## Goal

Port input quality filter and fast path from voice-calendar-scheduler into the discovery bot. Wire into server so garbage STT is rejected before hitting the LLM, and simple queries get instant answers.

## Context

Sprint 20 focus: continuous speech, input filter, echo cancellation. This agent handles F-048 (input filter) and F-052 (fast path). Voice push-to-talk works but every mic press hits the LLM even for garbage/silence.

## Plan

1. Port input_filter.py from reference implementation (keep garbage words, hallucination patterns, thresholds)
2. Create simplified fast_path.py for discovery bot context (help, reset, identity — not time/date)
3. Wire both into server.py transcribe endpoint
4. Write comprehensive tests
5. Update backlog

## Changes Made

- Created `bot/input_filter.py` — ported from voice-calendar-scheduler with InputQuality enum and classify() function
- Created `bot/fast_path.py` — simplified for discovery bot: help, reset, identity fast paths
- Updated `bot/server.py` — transcribe endpoint now runs input filter and fast path, returns filtered/quality/duration_s fields
- Created `tests/test_input_filter.py` — 63 tests covering garbage words, greetings, short audio, no_speech_prob, hallucinations, low confidence
- Created `tests/test_fast_path.py` — 38 tests covering help, reset, identity, no-match cases
- Updated `docs/project-memory/backlog/README.md` — F-048 and F-052 marked Complete (Sprint 20)
- Fixed repeated-word hallucination regex to properly match "the the the" pattern

## Decisions Made

- Kept greetings (hi, hello, hey) as VALID — they're real conversational signals for a discovery bot
- Did NOT port time/date fast paths — irrelevant for discovery bot context
- Fast path returns None for greetings — those should go to the LLM for a personalized response
- Used 200 status for filtered responses (not an error) with filtered=true flag
- Added fast_path_response field to transcribe response when fast path matches

## Open Questions

- Should the chat endpoint also run fast path? Currently only wired into voice transcribe.

## Links

Commits:
- (see git log for this session)
