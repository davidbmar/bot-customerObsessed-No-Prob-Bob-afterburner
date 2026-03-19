# Vision: Afterburner Customer Bot

## Product Name

Afterburner Customer Bot

## Problem Statement

Afterburner handles engineering (sprints, agents, code), but there's no customer-facing layer that captures **what to build and why**. The gap between "customer has a problem" and "engineer writes code" is filled by meetings, Slack threads, and tribal knowledge. Discovery interviews are manual, requirements flow through Notion/Jira, and context is lost at every handoff. Most AI dev tools start with the code — they assume you already know what to build.

## Target Audience

**Product builders and solo founders** who talk to customers but struggle to translate conversations into engineering requirements. They know their customers have real problems but lack the tooling to systematically capture, structure, and act on what they learn. They use Afterburner for engineering but need a front door that starts with the customer, not the code.

## Key Differentiators

- **Customer-first, not code-first.** The bot obsessively understands the problem before a single line is written — it won't accept "add a dark mode" without asking why.
- **Personality framework is reusable.** Future bots (tech support, sales, internal PM) plug into the same system with personality inheritance.
- **Local LLM inference** via Ollama — no API costs, full data privacy, works offline.
- **Deep Afterburner integration** — bot outputs (seed docs) become engineering inputs automatically. Conversation → Vision → Plan → Sprint → Shipped code → Customer feedback loop.
- **Principles over scripts.** Personalities are markdown documents encoding the *spirit* of behavior, not rigid response templates. The LLM uses judgment.

## Solution Overview

A conversational AI bot with three interfaces — web chat (localhost:1203), Telegram, and CLI — sharing a single brain (Qwen 3:4b via Ollama). The bot is guided by a markdown personality document (customer-discovery.md) that encodes principles like Customer Obsession, Dive Deep, and Bias for Action.

When a customer says "we need better reporting," the bot doesn't ask "what kind of reports?" — it asks "tell me about the last time someone used a report to make a decision." After 5-7 exchanges of deep discovery, the bot synthesizes findings into Problem/Users/Use Cases/Success Criteria format and writes seed docs to the Afterburner project.

The personality framework supports inheritance (base.md → customer-discovery.md), scenario-based evaluation, and a separate memory system (JSONL per chat + fact extraction). A debug panel in the web chat shows which principles are active, what tools were called, memory state, and token usage.

## Success Criteria

- Bot asks about users and use cases when given a feature request (not "what kind of feature?")
- 5-7 exchange conversations produce structured synthesis (Problem/Users/Use Cases/Success Criteria)
- save_discovery tool writes seed docs that Afterburner's lifecycle pipeline can consume
- Web chat debug panel shows principles, tools, memory, and latency
- Conversations don't bleed between sessions (memory isolation)
- Existing tool-telegram-whatsapp notifications continue working independently

## FAQ

**Q: Why Qwen 3:4b instead of Claude or GPT-4?**
A: Local inference means zero API costs for potentially hundreds of customer conversations, full privacy for sensitive discovery data, and the bot works without internet. The personality framework compensates for the smaller model by providing explicit behavioral guidance.

**Q: Can this work with other LLMs?**
A: Yes — the personality framework separates principles (what) from prompts (how). Phase 2 adds multi-provider support. The gateway pattern means swapping the LLM is a config change, not an architecture change.

**Q: How is this different from just using ChatGPT to talk to customers?**
A: Three things: (1) the personality framework ensures consistent discovery behavior across conversations, (2) tool integration means discoveries automatically become Afterburner seed docs, and (3) the evaluation framework lets you test whether the bot actually follows its principles.
