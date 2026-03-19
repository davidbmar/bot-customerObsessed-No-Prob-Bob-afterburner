# Personality Framework Design

## Design Principles (lessons from critiquing the YAML approach)

1. **Personality as a document, not config.** Markdown that the LLM reads directly — humans write and review it naturally, the LLM interprets as guidance not rules.

2. **Principles over patterns.** Encode the *spirit* ("understand the problem before proposing solutions") not the exact phrases ("say 'tell me more about...'"). The LLM has judgment — let it use it.

3. **Separate principles from prompts.** Principles are the *what* (Customer Obsession). The system prompt is the *how* for a specific LLM. Different LLMs need different prompting — Qwen 3.5 might need more explicit instructions than Claude.

4. **Memory as a separate system.** Don't embed memory rules in the personality. A reusable memory service that summarizes past conversations, extracts key facts, and feeds relevant context per conversation.

5. **Personality inheritance.** A base personality (polite, helpful, honest) that specific personalities extend with domain-specific principles.

6. **Scenario-based evaluation.** Test personalities with conversation scenarios, not unit tests. "Given this input, does the bot behave according to its principles?"

## Personality Document Format

```
~/.config/afterburner-bots/personalities/

base.md                      ← shared foundation all bots inherit
customer-discovery.md        ← customer-facing discovery agent
tech-support.md              ← (future) patient, precise, escalates well
internal-pm.md               ← (future) blunt, data-driven, deadline-aware
```

### `base.md` — Foundation personality

```markdown
# Base Personality

## Core Values
- Be honest. If you don't know, say so.
- Be helpful. Your goal is to make the person's life easier.
- Be respectful. Every person's time matters.
- Stay focused. Don't ramble or over-explain.

## Communication Style
- One idea per message. Don't overwhelm.
- Use simple language. Avoid jargon unless the person uses it first.
- Confirm understanding before taking action.
```

### `customer-discovery.md` — The first bot

A bot that talks to customers before anything gets built. Its superpower is asking the right questions to uncover the real problem. It never accepts a feature request at face value — it always digs into the use case behind it.

**Principles:** Customer Obsession, Dive Deep, Insist on High Standards, Bias for Action, Data Driven.

**Conversation flow:** Opening → Discovery (3-7 exchanges) → Synthesis (Problem/Users/Use Cases/Success Criteria) → Handoff (seed docs, vision, sprint candidates) → Follow-up.

## Personality Loader

```python
class Personality:
    def __init__(self, path: str):
        self.content = read_markdown(path)
        self.base = self._load_base()  # reads "Extends: base.md"

    def to_system_prompt(self) -> str:
        return f"{self.base}\n\n{self.content}"

    def get_principles(self) -> list[str]:
        ...
```

## Memory System (separate from personality)

```
~/.config/afterburner-bots/memory/
├── conversations/
│   ├── chat-12345/              ← per Telegram chat
│   │   ├── history.jsonl        ← raw message log
│   │   ├── summary.md           ← LLM-generated summary of key facts
│   │   └── facts.json           ← extracted: {"users": 2, "current_tool": "spreadsheets"}
│   └── chat-67890/
└── shared/
    └── customer-profiles.json   ← cross-conversation customer knowledge
```

Memory service responsibilities:
- Log every message (history.jsonl)
- After each conversation, summarize key facts (LLM call)
- Before each response, inject relevant context from past conversations
- Extract structured data (user count, pain points, tools mentioned)
- This service is reusable across ALL bots

## Evaluation Framework

```yaml
name: "Surface-level feature request"
input: "We need a dark mode"
principles_tested: [Customer Obsession, Dive Deep]
pass_criteria:
  - response contains a question about why or who
  - response does NOT immediately accept the request
  - response does NOT ask "what kind of dark mode"
fail_criteria:
  - response says "sure, I'll add that"
  - response jumps to implementation details
```

Run evaluations:
```bash
afterburner-bot evaluate customer-discovery
# Runs all scenarios, reports which principles held vs broke
```
