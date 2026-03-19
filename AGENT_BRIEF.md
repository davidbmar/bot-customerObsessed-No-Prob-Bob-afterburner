agentA-personality — Sprint 1

Previous Sprint Summary
─────────────────────────────────────────
- This is Sprint 1 — no previous sprint. Project scaffolding exists with stub modules in bot/ (personality.py, llm.py, gateway.py, memory.py, server.py, tools.py, config.py, polling.py). Personality docs exist (base.md, customer-discovery.md). pyproject.toml configured.
─────────────────────────────────────────

Sprint-Level Context

Goal
- Build the foundation: personality framework, LLM gateway with web chat, and memory system
- Deliver a working bot you can talk to at http://localhost:1203/chat
- Customer discovery personality guides all conversations

Constraints
- Use Qwen 3.5 via Ollama (local inference, no API costs)
- All bot code goes in `bot/` directory, CLI in `cli.py`
- Personality docs go in `personalities/` (base.md, customer-discovery.md)
- Web chat serves on port 1203
- Python 3.11+, httpx for HTTP, no heavy frameworks
- Agents run non-interactively — MUST NOT ask for confirmation


Objective
- Build the personality framework with inheritance, principle extraction, and system prompt generation

Tasks
- Rewrite `bot/personality.py` with a `PersonalityLoader` class that:
  - Reads markdown files from a `personalities/` directory
  - Supports inheritance: `customer-discovery.md` can declare `extends: base` in YAML frontmatter
  - Extracts principles from markdown (## Principles section → list of principle objects)
  - Generates a system prompt by combining base + child principles and personality content
  - Method: `load(name) -> PersonalityDoc` with fields: name, principles, system_prompt, raw_content
- Ensure `personalities/base.md` has foundational principles (polite, honest, helpful, curious)
- Ensure `personalities/customer-discovery.md` extends base and adds discovery-specific principles:
  - Customer Obsession: understand the problem before proposing solutions
  - Dive Deep: ask "why" and "tell me about the last time" not "what kind of"
  - Bias for Action: after 5-7 exchanges, synthesize findings
  - Working Backwards: start with the customer outcome, not the feature
  - Structured Output: produce Problem/Users/Use Cases/Success Criteria format
- Write tests in `tests/test_personality.py`:
  - Loader finds and loads personality by name
  - Inheritance merges base + child principles
  - System prompt includes all principles
  - Missing personality raises clear error

Acceptance Criteria
- `PersonalityLoader('personalities').load('customer-discovery')` returns a PersonalityDoc with 5+ principles
- System prompt includes both base and customer-discovery principles
- `python3 -m pytest tests/test_personality.py -v` passes
- Personality docs in `personalities/` are well-written markdown
