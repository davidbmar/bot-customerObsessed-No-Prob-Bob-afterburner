# Session

Session-ID: S-2026-03-20-0631-sprint14-conversations-tokens
Title: Sprint 14 — Conversation sidebar, token fix, cost display
Date: 2026-03-20
Author: Claude (agentA)

## Goal

Implement conversation sidebar (F-032), fix token counting (B-018), fix provider display (B-019), and add cost display (F-030).

## Context

Sprint 13 shipped conversation persistence, mobile responsive, auto-synthesis. Token counts showed inflated numbers (1378 out for 20-word response), header showed wrong provider name, no way to see past conversations, no cost tracking.

## Plan

1. Fix token count: route Ollama providers through OllamaClient (native /api/chat) instead of OpenAICompatibleClient (/v1) to get eval_count
2. Fix provider display: add provider_label to health check response, use in header
3. Add conversation sidebar: collapsible left panel reading conv_* from localStorage
4. Add token cost display: TOKEN_PRICES map, per-message + session cost in debug panel
5. Write tests for all features

## Changes Made

- `bot/llm.py`: Modified `get_client()` — local Ollama providers (needs_key=False) now return OllamaClient with /v1 stripped from URL, ensuring eval_count is used for accurate token counts
- `bot/gateway.py`: Added `provider_label` to `health_check()` response using LLM_PROVIDERS lookup
- `bot/chat_ui.html`: Added conversation sidebar (CSS + HTML + JS), provider label display, TOKEN_PRICES cost calculation, per-message and session cost in debug panel
- `tests/test_llm.py`: Updated 2 tests to match new OllamaClient routing
- `tests/test_sprint14_conversations_tokens.py`: 37 new tests covering token accuracy, provider labels, cost calculation, sidebar HTML, cost display HTML
- `docs/project-memory/backlog/README.md`: Marked B-018, B-019, F-030, F-032 as Complete (Sprint 14)

## Decisions Made

- Used OllamaClient for all local (needs_key=False) providers rather than adding a separate flag. This is clean because the only non-key providers are Ollama-backed.
- Sidebar collapsed by default (including desktop) — toggled via hamburger icon in header. Mobile gets full-screen overlay with backdrop.
- Preserved existing conversations in localStorage when starting new chat (changed clearConversationStorage to saveConversation in newConversation).
- Cost prices hardcoded in JS (not fetched from server) — simplifies architecture, prices change infrequently.

## Open Questions

None.

## Links

Commits:
- (pending commit)
