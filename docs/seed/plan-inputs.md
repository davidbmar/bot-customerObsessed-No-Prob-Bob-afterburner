# Plan Inputs

## Appetite

3 phases over approximately 6-8 sprints to reach full production.

Phase 1 (2-3 sprints): Personality framework + web chat + text bot MVP
Phase 2 (2-3 sprints): Full Afterburner integration + evaluation framework
Phase 3 (2 sprints): Voice + multi-platform + customer profiles

## Solution Sketch

The bot uses a **gateway pattern** — a single LLM orchestration layer (Qwen 3:4b via Ollama) with multiple transport adapters (web chat on port 1203, Telegram polling, CLI). The personality framework reads markdown documents that encode principles, not rigid rules, allowing the LLM to use judgment.

Key architectural decisions:
- Personality as markdown documents with inheritance (base.md → customer-discovery.md)
- Memory as a separate JSONL-based system, not embedded in personality
- Tool calls bridge the bot to Afterburner (save_discovery, get_project_summary)
- Web chat includes a debug panel showing principles, tools, memory, and token usage

## Market Fit

No existing tool bridges customer conversations to automated engineering pipelines. Current alternatives: manual discovery interviews → Notion/Jira → engineering tickets. This bot automates the entire chain: conversation → seed docs → vision → plan → sprint → shipped code → customer feedback loop.

## Differentiation

- Starts with the customer, not the code. Most AI dev tools assume you know what to build.
- Personality framework is reusable — future bots (tech support, internal PM) plug into the same system.
- Local LLM inference (Ollama) means no API costs, full privacy, works offline.
- Deep integration with Afterburner's sprint pipeline — bot outputs become engineering inputs automatically.

## Rabbit Holes

- Don't over-engineer the personality format — markdown is enough, no YAML schemas needed.
- Don't build a custom vector DB for memory — JSONL + JSON facts is sufficient for Phase 1.
- Don't try to support every LLM provider in Phase 1 — Ollama only, add Claude/OpenAI later.
- Voice/STT is Phase 3 — don't let it creep into earlier phases.

## No Gos

- No WhatsApp in Phase 1 (requires Business API approval).
- No vector database or embedding-based retrieval in Phase 1.
- No multi-tenant or cloud-hosted deployment — local only.
- No payment or billing integration.
- No automated sprint launching from bot conversations (human reviews seed docs first).

## Sprint Candidates

### Sprint 1: Foundation
- Personality loader with inheritance
- Base + customer-discovery personality docs
- Qwen 3:4b via Ollama with tool calling
- Web chat UI (port 1203) with debug panel
- Conversation memory (JSONL per chat)
- CLI: start, chat, status commands

### Sprint 2: Telegram + Tools
- Telegram polling transport
- Tools: save_discovery, get_project_summary
- End-to-end test: conversation → seed doc written to project
- Config system (~/.config/afterburner-bots/config.json)

### Sprint 3: Evaluation + Integration
- Evaluation framework with YAML scenarios
- More tools: generate_vision, add_to_backlog, get_sprint_status
- Fact extraction from conversations
- Post-sprint feedback loop

### Sprint 4: Polish + Docs Site
- Web chat settings panel
- Multi-project support
- Documentation site built and deployed to S3/CloudFront
- README and getting-started guide
