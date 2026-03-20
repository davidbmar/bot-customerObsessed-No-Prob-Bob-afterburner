# Sprint 13 — Synthesis and Fixes

- **Session ID:** S-2026-03-20-0614-sprint13-synthesis-and-fixes
- **Date:** 2026-03-20
- **Goal:** Fix server direct-run, add save_discovery API endpoint, add auto-synthesis

## Context
Sprint 13 agentA tasks: fix B-017 (server direct-run regression), implement F-033 (save_discovery API), implement F-034 (auto-synthesis after 5+ exchanges).

## Changes Made
1. **Fixed `python3 bot/server.py` direct run (B-017):** Added bootstrap guard at top of server.py that sets `__package__ = "bot"` and adds parent dir to `sys.path` when run directly. Removed try/except import fallback in favor of clean relative imports.
2. **Added `POST /api/tools/save_discovery` endpoint (F-033):** New endpoint accepts `{project_slug, conversation_id}`, reads conversation history, formats as discovery doc, calls existing `tool_save_discovery()`.
3. **Added auto-synthesis after 5+ exchanges (F-034):** Gateway tracks exchange counts per conversation. After 5th user message, appends synthesis instruction to system prompt. `synthesis_triggered` flag prevents re-triggering.
4. **25 new tests:** Covering all three features. Total test count: 234 (was 209).
5. **Updated backlog:** B-017, F-033, F-034 marked Complete (Sprint 13).

## Decisions Made
- Used `__package__` bootstrap approach for server direct-run rather than modifying all imports across the chain — minimal change, maximum compatibility.
- Auto-synthesis modifies system prompt rather than injecting a user message — preserves conversation flow and works with all LLM providers.
- Synthesis triggers once per conversation to avoid repeated summaries.
