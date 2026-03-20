# Plan: No Prob Bob — Customer-Obsessed Agent Platform

## Problem

AI developer tools start with the code and assume you know what to build. The gap between "customer has a problem" and "engineer writes code" is filled by manual discovery interviews, Notion/Jira tickets, and lost context at every handoff. No existing tool bridges customer conversations to automated engineering pipelines.

## Appetite

4 phases over 19+ sprints. Phases 1-2 are complete (19 sprints shipped). Phase 3 is next. Phase 4 is future exploration.

## Phase 1: Foundation (DONE — Sprints 1-4)

**Goal:** Working bot you can talk to, guided by a personality framework.

**Delivered:**
- Personality framework with markdown documents and inheritance (base.md → customer-discovery.md)
- 9 discovery principles (Customer Obsession, Dive Deep, etc.)
- Qwen 3:4b via Ollama with tool calling
- Web chat UI at localhost:1203 — dark theme, chat bubbles
- Conversation memory (JSONL per chat, per-session isolation)
- CLI: start, chat, status commands
- Telegram polling transport
- save_discovery tool — conversation → seed doc pipeline
- End-to-end test proving the full flow

**Test count at Phase 1 end:** 56 tests

## Phase 2: Integration + Polish + Multi-Provider (DONE — Sprints 5-19)

**Goal:** Full Afterburner integration, evaluation framework, polished UX, multi-provider LLM, production-ready web chat.

**Delivered (Sprints 5-11, original Phase 2):**
- Evaluation framework with YAML scenario tests and CLI runner
- 6 Afterburner tools: save_discovery, get_project_summary, add_to_backlog, get_sprint_status, generate_vision, feedback_on_sprint
- Fact extraction from conversations (LLM-generated structured summaries)
- Multi-provider LLM — Ollama + Claude (Haiku/Sonnet/Opus) + ChatGPT, runtime switching from UI
- Web chat debug panel, settings panel, welcome message, progress indicator
- Multi-project support, conversation export, personality hot-reload

**Delivered (Sprints 12-19, extended Phase 2):**
- SSE streaming responses (word-by-word instead of waiting 20-40s)
- Conversation persistence across page reloads (localStorage)
- Error handling with retry (red error bubbles when LLM unreachable)
- 19 PROJECT_STATUS docs for full dashboard sprint history
- Save-as-seed-doc button in web chat UI
- Auto-synthesis after 5+ exchanges (Problem/Users/Use Cases/Success Criteria)
- Auto-scroll on new messages
- Mobile-responsive CSS with viewport meta
- Conversation sidebar with search, delete, title editing
- Token cost display for paid providers
- Dark/light theme toggle with system preference detection
- 9 evaluation scenarios (technical, emotional, multi-problem, solution-fixated, returning, enterprise)
- E2E integration tests proving discovery→seed doc pipeline
- Comprehensive README with quick start, API reference, architecture
- CLI evaluate with colored pass/fail output
- Markdown rendering in bot messages (bold, code, lists)
- Date grouping in chat history (Today, Yesterday, Mar 19)
- Structured seed doc export with Problem/Users/Use Cases sections
- Debug panel hidden by default (CSS-level fix)
- Sidebar collapsed on first visit
- Typing indicator animation (pulsing dots)

**Test count at Phase 2 end:** 485 tests, 52 features shipped

**Notable sprint lessons:**
- Sprints 4-5 had merge failures with multiple agents. Sprint 6 switched to single-agent sprints. Sprints 12-19 used safe file-ownership splitting for 2-agent parallelism.
- The build→test→backlog→sprint loop (Sprints 12-19) shipped 30 features and +302 tests in ~3 hours of wall clock time.

## Phase 3: Agent SDK + Voice + Profiles (NEXT)

**Goal:** Migrate to the Agent SDK architecture, add voice support, customer profiles, and a second personality type.

The seed docs include a TypeScript Agent SDK reference implementation (vibecode-agent) that demonstrates the target architecture: query loop, WebSocket streaming, typed permission gating, in-process MCP server.

### Sprint Candidates
- Agent SDK Migration: Port Python LLM gateway to TypeScript Agent SDK `query()` loop
- WebSocket streaming: Replace SSE with WebSocket for bidirectional communication
- Permission gating: Auto-allow read ops, require approval for destructive tools
- Customer profiles: Cross-conversation knowledge store
- Voice: Whisper STT for Telegram voice messages, WhatsApp transport
- Second personality: Tech-support personality to validate framework reusability

## Phase 4: Multi-Bot Platform (FUTURE)

**Goal:** From a single bot to a platform for building and deploying personality-driven agents.

**Exploration areas:**
- Active learning from conversation outcomes
- Personality marketplace
- Multi-bot orchestration with shared customer context
- Cloud deployment
- Sub-agents for long-running tasks

## Rabbit Holes (Updated)

- Don't over-engineer the personality format — markdown is enough. ✅ Validated across 19 sprints.
- Don't build a custom vector DB for memory — JSONL + JSON facts is sufficient. ✅ Still holds.
- Multi-provider shipped in Sprint 11. Gateway pattern validated. ✅
- Voice/STT remains Phase 3.
- Don't port everything to TypeScript at once — migrate the LLM gateway first.
- Don't add cloud deployment before the Agent SDK migration is solid.

## No-Gos (Updated)

- No multi-tenant or cloud-hosted deployment until Phase 4.
- No payment or billing integration.
- No automated sprint launching from bot conversations (human reviews seed docs first).
- No embedding-based retrieval — fact extraction + JSONL is the memory model.
