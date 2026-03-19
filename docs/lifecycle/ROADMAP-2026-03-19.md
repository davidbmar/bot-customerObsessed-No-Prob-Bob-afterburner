# Roadmap & Architecture

## Roadmap

### Current Focus

- Create Afterburner project: `afterburner create_project afterburner-customer-bot`
- Personality loader (reads markdown, generates system prompt)
- Base personality + customer-discovery personality docs
- Qwen 3.5 via Ollama with tool-calling (`bot/llm.py`)
- **Web chat UI at `http://localhost:1203/chat`** — dark theme, debug panel showing tools/principles/memory
- **Web chat API**: `POST /api/chat` (send message, get response), `GET /api/history` (conversation), `GET /api/personality` (current personality info)
- Telegram polling loop (runs alongside web server)
- Tools: save_discovery, get_project_summary
- Conversation memory (JSONL per chat, works for both web and Telegram)
- CLI: `afterburner-bot start` (server + polling), `afterburner-bot chat` (interactive CLI)
- Test: have a real discovery conversation via web chat AND Telegram

### Next Up

- More tools: generate_vision, add_to_backlog, get_sprint_status
- Post-sprint feedback loop ("here's what shipped, does it match?")
- Evaluation framework with scenario tests
- Fact extraction from conversations (LLM-generated summaries)
- Multi-project support (backend registry)
- Web chat settings panel: switch personality, switch model, view memory

## Architecture

### Key Decisions

1. **Personality as a document, not config.** Markdown that the LLM reads directly — humans write and review it naturally, the LLM interprets as guidance not rules.

2. **Principles over patterns.** Encode the *spirit* ("understand the problem before proposing solutions") not the exact phrases ("say 'tell me more about...'"). The LLM has judgment — let it use it.

3. **Separate principles from prompts.** Principles are the *what* (Customer Obsession). The system prompt is the *how* for a specific LLM. Different LLMs need different prompting — Qwen 3.5 might need more explicit instructions than Claude.

4. **Memory as a separate system.** Don't embed memory rules in the personality. A reusable memory service that summarizes past conversations, extracts key facts, and feeds relevant context per conversation.

5. **Personality inheritance.** A base personality (polite, helpful, honest) that specific personalities extend with domain-specific principles.

6. **Scenario-based evaluation.** Test personalities with conversation scenarios, not unit tests. "Given this input, does the bot behave according to its principles?"

### Tech Stack

- **Bot backend:** Python 3.11+, httpx, PyYAML
- **LLM:** Qwen 3:4b via Ollama (local inference — no API costs, privacy, works offline)
- **Web chat:** Self-contained HTML/CSS/JS served by bot's HTTP server (port 1203)
- **Telegram:** Bot API polling via httpx
- **Memory:** JSONL per-chat + JSON fact extraction
- **Evaluation:** YAML scenario files tested against LLM responses
- **Docs site:** Static HTML deployed to S3 + CloudFront


--- implementation-phases.md ---

