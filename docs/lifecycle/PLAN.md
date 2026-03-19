# Plan

## Problem

Afterburner handles engineering (sprints, agents, code), but there's no customer-facing layer that captures what to build and why. The gap between 'customer has a problem' and 'engineer writes code' is filled by meetings, Slack threads, and tribal knowledge. There is no automated bridge from customer conversations to engineering pipelines — discovery interviews are manual, requirements flow through Notion/Jira, and context is lost at every handoff.

## Appetite

3 phases over approximately 6-8 sprints to reach full production. Phase 1 (2-3 sprints): Personality framework + web chat + text bot MVP. Phase 2 (2-3 sprints): Full Afterburner integration + evaluation framework. Phase 3 (2 sprints): Voice + multi-platform + customer profiles.

## Solution Sketch

The bot uses a gateway pattern — a single LLM orchestration layer (Qwen 3:4b via Ollama) with multiple transport adapters (web chat on port 1203, Telegram polling, CLI). The personality framework reads markdown documents that encode principles, not rigid rules, allowing the LLM to use judgment. Key architectural decisions: Personality as markdown documents with inheritance (base.md → customer-discovery.md). Memory as a separate JSONL-based system, not embedded in personality. Tool calls bridge the bot to Afterburner (save_discovery, generate_vision, add_to_backlog, get_project_summary, get_sprint_status). Web chat includes a debug panel showing principles, tools, memory, and token usage. The bot translates customer conversations into seed docs, which flow into Afterburner's lifecycle pipeline (Vision → Plan → Sprint → Shipped code → Customer feedback loop).

## Market Fit Analysis

No existing tool bridges customer conversations to automated engineering pipelines. Current alternatives: manual discovery interviews → Notion/Jira → engineering tickets. This bot automates the entire chain: conversation → seed docs → vision → plan → sprint → shipped code → customer feedback loop. Most AI dev tools start with the code and assume you know what to build. This starts with the customer, obsessively understanding the problem before a single line is written.

## Differentiation Strategy

Starts with the customer, not the code — most AI dev tools assume you know what to build. Personality framework is reusable — future bots (tech support, internal PM) plug into the same system with personality inheritance. Local LLM inference (Ollama) means no API costs, full privacy, works offline. Deep integration with Afterburner's sprint pipeline — bot outputs become engineering inputs automatically. Personality is encoded as markdown documents that LLMs read directly, not config files or YAML schemas, allowing natural authoring and LLM judgment. Scenario-based evaluation framework tests whether the bot behaves according to its principles, not just unit test correctness.

## Rabbit Holes

Don't over-engineer the personality format — markdown is enough, no YAML schemas needed. Don't build a custom vector DB for memory — JSONL + JSON facts is sufficient for Phase 1. Don't try to support every LLM provider in Phase 1 — Ollama only, add Claude/OpenAI later. Voice/STT is Phase 3 — don't let it creep into earlier phases. Avoid embedding memory rules inside the personality; keep memory as a separate reusable service. Don't try to automate sprint launching from bot conversations — a human should review seed docs first.

## No-Gos

No WhatsApp in Phase 1 (requires Business API approval). No vector database or embedding-based retrieval in Phase 1. No multi-tenant or cloud-hosted deployment — local only. No payment or billing integration. No automated sprint launching from bot conversations (human reviews seed docs first).

## Sprint Candidates

Sprint 1 — Foundation: Personality loader with inheritance, base + customer-discovery personality docs, Qwen 3:4b via Ollama with tool calling, web chat UI (port 1203) with debug panel, conversation memory (JSONL per chat), CLI commands (start, chat, status). Sprint 2 — Telegram + Tools: Telegram polling transport, tools (save_discovery, get_project_summary), end-to-end test (conversation → seed doc written to project), config system (~/.config/afterburner-bots/config.json). Sprint 3 — Evaluation + Integration: Evaluation framework with YAML scenarios, more tools (generate_vision, add_to_backlog, get_sprint_status), fact extraction from conversations, post-sprint feedback loop. Sprint 4 — Polish + Docs Site: Web chat settings panel, multi-project support, documentation site built and deployed to S3/CloudFront, README and getting-started guide.

