# Afterburner Ecosystem — Vision & Context

## The Problem

Afterburner handles engineering (sprints, agents, code). But there's no customer-facing layer that captures **what to build and why**. The gap between "customer has a problem" and "engineer writes code" is filled by meetings, Slack threads, and tribal knowledge.

## The Solution

A conversational AI customer discovery bot that:
- Lives in Telegram, WhatsApp, and a web chat interface
- Talks to customers and obsessively clarifies use cases
- Translates conversations into requirements Afterburner can execute
- Closes the loop after engineering ships ("does this match what you described?")

```
Customer ←→ Bot (discovery + requirements) ←→ Afterburner (engineering)
             │                                    │
             │ Personality: customer-discovery.md  │
             │ Brain: Qwen 3.5 (local)            │
             │ Memory: per-customer history        │
             │ Tools: Afterburner APIs             │
             │                                    │
             └── Seed docs, Vision, Plan ────────→┘
```

## Why It's Different

Most AI dev tools start with the code. This starts with the customer. The bot obsessively understands the problem before a single line is written.

**The flow:** Customer conversation → Seed docs → Vision → Plan → Sprint → Shipped code → Customer feedback → Loop

## Three Pillars

### 1. Personality Framework (reusable)
A system for encoding bot personalities with principles, conversation patterns, memory, and evaluation. Not config files — markdown documents that LLMs read directly. Personality inheritance (base → customer-discovery). Scenario-based evaluation.

### 2. Customer Discovery Bot (first consumer)
The first bot built on the personality framework. Three interfaces (web chat, Telegram, CLI) sharing one brain (Qwen 3.5 via Ollama). Tools that write seed docs, check project status, and trigger Afterburner pipelines.

### 3. Documentation Site (published)
A polished docs site on S3/CloudFront covering the entire Afterburner ecosystem — vision, architecture, bot UX, personality framework, getting started guide.

## This Is an Afterburner Project

Built with Afterburner's own sprint tooling:
- Sprint automation (`.sprint/scripts/`)
- Project memory (`docs/project-memory/sessions/`, `adr/`, `backlog/`)
- Lifecycle docs (`docs/lifecycle/VISION.md`, `PLAN.md`, `ROADMAP.md`)
- Dashboard tracking at `http://localhost:1201/afterburner-customer-bot/`

## Tech Stack

- **Bot backend:** Python 3.11+, httpx, PyYAML
- **LLM:** Qwen 3:4b via Ollama (local inference — no API costs, privacy, works offline)
- **Web chat:** Self-contained HTML/CSS/JS served by bot's HTTP server (port 1203)
- **Telegram:** Bot API polling via httpx
- **Memory:** JSONL per-chat + JSON fact extraction
- **Evaluation:** YAML scenario files tested against LLM responses
- **Docs site:** Static HTML deployed to S3 + CloudFront
