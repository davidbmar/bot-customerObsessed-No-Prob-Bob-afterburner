# Customer Discovery Bot — Architecture & Implementation

## Context

Afterburner handles engineering (sprints, agents, code). But there's no customer-facing layer that captures **what to build and why**. We need a bot that lives in Telegram/WhatsApp, talks to customers, obsessively clarifies use cases, and translates conversations into requirements Afterburner can execute.

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

## Architecture

```
┌──────────────────────────────────────────────┐
│  afterburner-customer-bot                    │
│                                              │
│  Three interfaces (same brain):              │
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Web Chat │ │ Telegram │ │    CLI      │  │
│  │ :1203    │ │ polling  │ │ bot chat    │  │
│  │ /chat    │ │          │ │ "message"   │  │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       └─────────────┼─────────────┘          │
│                     ▼                        │
│        Qwen 3.5 (Ollama) + personality       │
│                     │                        │
│                     │ tool calls             │
│                     ▼                        │
│  Tools:                                      │
│    ├── save_discovery(slug, content)          │
│    │     → writes seed docs to project       │
│    ├── generate_vision(slug)                  │
│    │     → calls Afterburner lifecycle API    │
│    ├── add_to_backlog(slug, title, context)   │
│    │     → adds feature/bug to backlog        │
│    ├── get_sprint_status(slug)                │
│    │     → checks what's been built           │
│    └── get_project_summary(slug)              │
│          → what's shipped, what's planned     │
│                                              │
│  Memory:                                     │
│    ├── conversation history (per chat)       │
│    ├── fact extraction (LLM-generated)       │
│    └── customer profiles (cross-session)     │
└──────────────────────────────────────────────┘
```

## Three Interfaces

### 1. Web Chat — `http://localhost:1203/chat` (fastest dev loop)
- Dark-themed chat UI served by the bot's own HTTP server
- Type messages, see responses in real time
- Debug panel shows: tools called, principles active, memory state, raw LLM output
- Change personality markdown → reload page → test immediately
- No Telegram needed — instant local testing

### 2. Telegram (real usage from phone)
- Same bot token as tool-telegram-whatsapp notifications
- Polls getUpdates, routes messages through LLM
- Voice messages processed via Whisper STT (Phase 3)
- Group-aware: knows which project a group belongs to

### 3. CLI (scripting and quick tests)
```bash
afterburner-bot chat                              # Interactive
afterburner-bot chat "We need a login page"       # Single message
afterburner-bot chat --personality tech-support    # Specify personality
afterburner-bot chat --project grassyknoll         # Against a specific project
```

## Project Structure

```
~/src/afterburner-customer-bot/
├── bot/
│   ├── __init__.py
│   ├── gateway.py           # Main entry — start server + polling + LLM
│   ├── polling.py           # Telegram getUpdates loop
│   ├── llm.py               # Qwen 3.5 via Ollama with tool calling
│   ├── tools.py             # Afterburner API tool definitions
│   ├── memory.py            # Conversation memory + fact extraction
│   ├── personality.py       # Load + apply personality from markdown
│   ├── server.py            # HTTP server (:1203) — web chat + API
│   └── chat_ui.html         # Web chat interface (self-contained)
├── personalities/
│   ├── base.md
│   └── customer-discovery.md
├── evaluations/
│   ├── runner.py            # Run scenario tests
│   └── scenarios/
│       ├── surface-request.yaml
│       ├── vague-requirements.yaml
│       └── pushback.yaml
├── cli.py                   # afterburner-bot start|chat|evaluate|status
├── pyproject.toml
└── README.md
```

## Configuration

```json
{
  "botToken": "...",
  "personality": "customer-discovery",
  "llm": {
    "provider": "ollama",
    "model": "qwen3.5:4b",
    "baseUrl": "http://localhost:11434"
  },
  "backends": [
    {
      "name": "local",
      "url": "http://127.0.0.1:1201"
    }
  ],
  "voice": {
    "enabled": false,
    "sttModel": "whisper-small"
  }
}
```
