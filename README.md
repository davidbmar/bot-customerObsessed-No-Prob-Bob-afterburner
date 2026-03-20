# Afterburner Customer Discovery Bot

Conversational AI agent that guides customer discovery interviews, extracts insights, and saves structured seed documents to [Afterburner](https://github.com/davidbmar/traceable-searchable-adr-memory-index) projects.

Built across 16 sprints with 38+ features, 9 evaluation scenarios, and 363 passing tests.

## Features

- **Customer discovery conversations** with personality-driven prompts and principles
- **Multi-provider LLM** — Ollama (Qwen 3.5), Claude (Haiku/Sonnet/Opus), ChatGPT, with runtime switching
- **Streaming responses** via Server-Sent Events
- **Web chat UI** — dark/light theme, conversation sidebar, search, per-message debug panel
- **Seed document export** — save discoveries as structured docs to Afterburner projects
- **Evaluation framework** — YAML scenario tests with pass/fail criteria
- **Telegram integration** — optional polling transport
- **Personality framework** — hot-reloadable personality configs with principles
- **Conversation memory** — persistence, export, multi-conversation management
- **CLI** — start server, interactive chat, evaluate scenarios, export conversations

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/davidbmar/bot-customerObsessed-No-Prob-Bob-afterburner.git
cd bot-customerObsessed-No-Prob-Bob-afterburner

# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start the server (default port 1203)
afterburner-bot start
# Or: python3 cli.py start

# Open web chat
open http://127.0.0.1:1203/chat
```

### Prerequisites

- Python 3.11+
- An LLM provider:
  - **Ollama** (default, free) — install from [ollama.com](https://ollama.com), then `ollama pull qwen3:4b`
  - **Claude** — set `ANTHROPIC_API_KEY` in `.env`
  - **ChatGPT** — set `OPENAI_API_KEY` in `.env`

## Architecture

```
┌────────────────────────────────────────────────┐
│                  Web Chat UI                    │
│          (bot/chat_ui.html — single-file SPA)   │
└───────────────────┬────────────────────────────┘
                    │ HTTP / SSE
┌───────────────────▼────────────────────────────┐
│              HTTP Server (bot/server.py)         │
│         BaseHTTPRequestHandler, port 1203        │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│              Gateway (bot/gateway.py)            │
│  • Loads personality + principles                │
│  • Manages conversation memory                   │
│  • Orchestrates LLM calls + tool execution       │
│  • Triggers synthesis after N exchanges          │
└──────┬────────────┬───────────────┬────────────┘
       │            │               │
  ┌────▼───┐  ┌─────▼─────┐  ┌─────▼─────┐
  │  LLM   │  │  Memory   │  │  Tools    │
  │ Client │  │ (memory.py)│  │(tools.py) │
  └────────┘  └───────────┘  └───────────┘
```

**Gateway pattern**: All transports (web, CLI, Telegram) go through `Gateway.process_message()`, which handles personality injection, memory retrieval, LLM call, tool execution, and fact extraction in a single pipeline.

**Personality framework**: Personalities are Markdown files in `personalities/` with sections for role, principles, and behavioral guidelines. The gateway injects the active personality into every LLM prompt. Personalities can be hot-reloaded at runtime.

**Memory**: Conversations are stored as JSON in `~/.local/share/afterburner-bot/conversations/`. The gateway tracks message history per conversation ID and includes recent context in LLM prompts.

## API Reference

### GET endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /chat` | Serve the web chat UI |
| `GET /api/health` | Health check — returns LLM status, model, personality |
| `GET /api/personality` | Current personality info |
| `GET /api/personalities` | List available personalities |
| `GET /api/config` | Current bot configuration |
| `GET /api/history?chat_id=ID` | Conversation message history |
| `GET /api/conversations/export?id=ID` | Export conversation as markdown |
| `GET /api/projects` | List registered Afterburner projects |
| `GET /api/llm/providers` | List available LLM providers and active provider |
| `GET /api/llm/config?provider_id=ID` | Get saved config for a provider |

### POST endpoints

| Endpoint | Body | Description |
|----------|------|-------------|
| `POST /api/chat` | `{message, conversation_id}` | Send message, get full response |
| `POST /api/chat/stream` | `{message, conversation_id}` | Send message, get SSE stream |
| `POST /api/config` | `{personality}` | Update bot configuration |
| `POST /api/conversations/new` | — | Create new conversation |
| `POST /api/personality/reload` | — | Hot-reload personality from disk |
| `POST /api/projects/switch` | `{slug}` | Switch active Afterburner project |
| `POST /api/llm/switch` | `{provider_id, model}` | Switch LLM provider at runtime |
| `POST /api/llm/config` | `{provider_id, base_url, model, api_key}` | Save provider configuration |
| `POST /api/tools/save_discovery` | `{conversation_id, project_slug}` | Save conversation as seed doc |

### Streaming format (SSE)

`POST /api/chat/stream` returns Server-Sent Events:

```
data: {"type": "token", "content": "Hello"}
data: {"type": "token", "content": " there"}
data: {"type": "done", "personality": "...", "principles_active": [...], "tokens": {"input": N, "output": N}, "duration_ms": N}
data: {"type": "error", "error": "message"}
```

## Configuration

Config file: `~/.config/afterburner-bots/config.json`

```json
{
  "personality": "customer-discovery",
  "llm": {
    "provider": "ollama",
    "model": "qwen3:4b",
    "baseUrl": "http://localhost:11434"
  },
  "telegram": {
    "botToken": "",
    "enabled": false
  },
  "server": {
    "port": 1203,
    "host": "127.0.0.1"
  },
  "projects": {},
  "active_project": ""
}
```

### Environment variables

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=sk-ant-...    # For Claude providers
OPENAI_API_KEY=sk-...           # For ChatGPT provider
```

### Personalities

Personality files live in `personalities/`. The default is `customer-discovery.md`, which guides the bot to ask probing questions, avoid jumping to solutions, and synthesize discoveries.

To create a custom personality, add a new `.md` file to `personalities/` and switch via the Settings panel or `POST /api/config`.

## Evaluation

The evaluation framework tests bot behavior against YAML scenarios in `evaluations/scenarios/`.

```bash
# Run all 9 scenarios
afterburner-bot evaluate
# Or: python3 cli.py evaluate

# Run with verbose output
afterburner-bot evaluate --verbose
```

Each scenario defines:
- `input` — a customer message to send
- `pass_criteria` — conditions the response must meet
- `fail_criteria` — conditions that cause failure
- `principles_tested` — which personality principles are being verified

### Adding scenarios

Create a YAML file in `evaluations/scenarios/`:

```yaml
name: my-scenario
principles_tested:
  - ask-why
  - no-solution-jumping
input: "I need a caching layer for my API"
pass_criteria:
  - "response asks about why caching is needed"
  - "response does NOT immediately propose Redis"
fail_criteria:
  - "response proposes implementation details"
```

## CLI Commands

```bash
afterburner-bot start              # Start web server (default port 1203)
afterburner-bot start -p base      # Start with a different personality
afterburner-bot start --port 8080  # Use custom port
afterburner-bot start --telegram   # Enable Telegram polling
afterburner-bot chat               # Interactive CLI chat
afterburner-bot status             # Show server status, personality, conversations
afterburner-bot evaluate           # Run evaluation scenarios
afterburner-bot export <conv-id>   # Export conversation as markdown
```

## Tech Stack

- **Python 3.11+** with `httpx`, `pyyaml`
- **Single-file HTML/CSS/JS** web chat (no build step, no framework)
- **BaseHTTPRequestHandler** for the API server
- **Ollama / Anthropic / OpenAI** APIs for LLM inference
- **pytest** for testing (363 tests across 15 sprints)

## Contributing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python3 -m pytest tests/ -v

# Run evaluations
python3 cli.py evaluate
```

### Commit conventions

This project uses [Afterburner project memory](docs/project-memory/). Every commit includes a `Session: S-YYYY-MM-DD-HHMM-slug` reference in the body. See `CLAUDE.md` for full conventions.

## License

Private repository.
