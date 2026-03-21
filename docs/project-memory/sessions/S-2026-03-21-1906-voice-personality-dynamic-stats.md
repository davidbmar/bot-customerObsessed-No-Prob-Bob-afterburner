# Session

Session-ID: S-2026-03-21-1906-voice-personality-dynamic-stats
Title: Add voice awareness to personalities and dynamic Docs stats
Date: 2026-03-21
Author: agentA (Sprint 28)

## Goal

Fix B-037: bot tells users "I can't hear audio" / "I'm text-only" while actively receiving transcribed speech. Update Docs panel to show dynamic stats from /api/stats.

## Context

The bot has working STT (Whisper) and TTS (Piper) but the personality system prompts never mention voice capabilities. The LLM defaults to assuming it's text-only. The Docs panel also has hardcoded sprint/test/feature counts.

## Plan

1. Add Capabilities section to customer-discovery.md and base.md personalities
2. Wire Docs panel stats to /api/stats with hardcoded fallback
3. Mark B-037 as Complete in backlog

## Changes Made

- `personalities/customer-discovery.md` — added Capabilities section with voice awareness instructions
- `personalities/base.md` — added same Capabilities section so ALL personalities inherit voice awareness
- `bot/chat_ui.html` — added id to stats paragraph, updated openDocs() to fetch /api/stats dynamically
- `docs/project-memory/backlog/README.md` — marked B-037 as Complete (Sprint 28)

## Decisions Made

- Added Capabilities section to both base.md AND customer-discovery.md for redundancy (customer-discovery extends base, but having it explicit in both ensures clarity)
- Used progressive enhancement for stats: hardcoded text remains as fallback, overwritten only on successful API response

## Open Questions

None.

## Links

Commits:
- See branch agentA-voice-personality
