# No Prob Bob — Customer Discovery Agent

> Talk to customers first, build later. This bot obsessively understands the problem before a single line of code is written.

A conversational AI agent that guides customer discovery interviews, extracts insights, and saves structured seed documents to [Afterburner](https://github.com/davidbmar/traceable-searchable-adr-memory-index) projects. Built across 19 sprints with 52 features, 9 evaluation scenarios, and 485 passing tests.

**[Setup Guide](#setup-guide)** · **[Web Chat](#web-chat)** · **[Telegram](#telegram-setup)** · **[API Reference](#api-reference)** · **[Dashboard](https://d3gb25yycyv0d9.cloudfront.net)**

---

## Setup Guide

### What You Need

| Component | Purpose | Required? |
|-----------|---------|-----------|
| [Ollama](https://ollama.com) | Local LLM (free, private, no API key) | Yes (or use Claude/ChatGPT instead) |
| Python 3.11+ | Runs the bot server | Yes |
| Telegram bot token | Bot responds on Telegram | Optional |
| Anthropic API key | Use Claude (smarter, costs money) | Optional |
| OpenAI API key | Use ChatGPT | Optional |

### Step 1: Install Ollama

Download from [ollama.com](https://ollama.com), then:

```bash
# Pull the default model
ollama pull qwen3:4b

# Verify it's running
ollama list
```

### Step 2: Clone and Install the Bot

```bash
git clone https://github.com/davidbmar/bot-customerObsessed-No-Prob-Bob-afterburner.git
cd bot-customerObsessed-No-Prob-Bob-afterburner

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 3: Start the Bot

```bash
# Make sure you're in the project directory with venv activated
cd ~/src/bot-customerObsessed-No-Prob-Bob-afterburner
source .venv/bin/activate

# Start the server
python3 -m bot.server
```

You should see:
```
Bot web server started at http://127.0.0.1:1203/chat
```

### Step 4: Open the Web Chat

Go to **http://localhost:1203/chat** in your browser.

The bot will greet you. Try typing: **"We need a better way to onboard new employees"**

The bot will ask discovery questions about your current process — not jump to solutions.

---

## Web Chat

The web chat at `http://localhost:1203/chat` includes:

- **Streaming responses** — text appears word-by-word as the LLM generates
- **Dark/light theme** — click ☀/☾ in the header (auto-detects your system preference)
- **Conversation sidebar** — click ☰ to see past chats, search, delete, rename
- **Multi-provider LLM** — click ⚙ to switch between Ollama, Claude, or ChatGPT
- **Debug panel** — click "Debug" to see tokens, latency, cost, active principles
- **Save as Seed Doc** — after 3+ exchanges, save the conversation as a structured document
- **Auto-synthesis** — after 5+ exchanges, the bot summarizes into Problem/Users/Use Cases/Success Criteria
- **Mobile responsive** — works on phones
- **Markdown rendering** — bot messages render bold, code, lists properly
- **Conversation persistence** — refresh the page, your chat is still there

### Switching LLM Providers

Click ⚙ in the header to open Settings. You can switch between:

| Provider | Cost | Speed | Quality |
|----------|------|-------|---------|
| **Qwen 3.5 (Ollama)** | Free | ~20-40s | Good |
| **Claude Haiku** | ~$0.001/msg | ~2s | Great |
| **Claude Sonnet** | ~$0.01/msg | ~3s | Excellent |
| **Claude Opus** | ~$0.05/msg | ~5s | Best |
| **ChatGPT** | ~$0.005/msg | ~2s | Great |

For Claude, you need an API key. Set it in the Settings panel or in your config file.

**Important:** Switching providers in the web UI also changes the provider for Telegram — they share the same brain.

---

## Telegram Setup

The bot can also respond to customers on Telegram — same personality, same discovery behavior.

### Step 1: Create a Telegram Bot

1. Open Telegram on your phone
2. Search for **@BotFather**
3. Send `/newbot`
4. Pick a name and username
5. Copy the token (looks like `123456:ABC-DEF...`)

### Step 2: Add the Token to Config

```bash
nano ~/.config/afterburner-bots/config.json
```

Change the telegram section:
```json
{
  "telegram": {
    "botToken": "paste-your-token-here",
    "enabled": true
  }
}
```

### Step 3: Restart the Server

```bash
cd ~/src/bot-customerObsessed-No-Prob-Bob-afterburner
source .venv/bin/activate
lsof -ti :1203 | xargs kill -9 2>/dev/null
python3 -m bot.server
```

You should see:
```
Telegram polling started
Telegram polling enabled
Bot web server started at http://127.0.0.1:1203/chat
```

### Step 4: Message Your Bot

Find your bot on Telegram by its username and send a message. It responds with the same customer discovery behavior as the web chat.

---

## Configuration

Everything lives in one file: `~/.config/afterburner-bots/config.json`

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
  }
}
```

### API Keys

For Claude or ChatGPT, create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
OPENAI_API_KEY=sk-...           # For ChatGPT
```

Or set them in the web UI Settings panel (⚙).

---

## How It Works

```
Customer (Web/Telegram/CLI)
        │
        ▼
   Gateway (bot/gateway.py)
   ├── Loads personality (customer-discovery.md)
   ├── Retrieves conversation memory
   ├── Calls LLM (Ollama/Claude/ChatGPT)
   ├── Executes tools (save_discovery, etc.)
   ├── Extracts facts from conversation
   └── Triggers auto-synthesis after 5 exchanges
        │
        ▼
   Response sent back to customer
```

**All interfaces share the same brain.** Web chat, Telegram, and CLI all go through `Gateway.process_message()`. Switching the LLM provider in the web UI changes it for Telegram too.

### Personality Framework

The bot's behavior is defined in markdown files in `personalities/`:
- `base.md` — core values (honest, helpful, focused)
- `customer-discovery.md` — discovery principles (Customer Obsession, Dive Deep, etc.)

Personalities support inheritance (customer-discovery extends base) and can be hot-reloaded without restarting the server.

### Tools

The bot has 6 Afterburner integration tools:

| Tool | What It Does |
|------|-------------|
| `save_discovery` | Saves conversation as a seed doc to a project |
| `get_project_summary` | Shows what's been built and planned |
| `add_to_backlog` | Adds features/bugs to project backlog |
| `get_sprint_status` | Checks current sprint progress |
| `generate_vision` | Creates a Vision doc from discovery |
| `feedback_on_sprint` | "Here's what shipped — does it match?" |

---

## API Reference

### GET Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /chat` | Web chat UI |
| `GET /api/health` | Health check — LLM status, model, personality |
| `GET /api/personality` | Current personality info |
| `GET /api/personalities` | List available personalities |
| `GET /api/config` | Current bot configuration |
| `GET /api/history?chat_id=ID` | Conversation message history |
| `GET /api/conversations/export?id=ID` | Export conversation as markdown |
| `GET /api/projects` | List Afterburner projects |
| `GET /api/llm/providers` | Available LLM providers + active |
| `GET /api/llm/config?provider_id=ID` | Saved config for a provider |

### POST Endpoints

| Endpoint | Body | Description |
|----------|------|-------------|
| `POST /api/chat` | `{message, conversation_id}` | Send message, get response |
| `POST /api/chat/stream` | `{message, conversation_id}` | Send message, get SSE stream |
| `POST /api/llm/switch` | `{provider_id, model}` | Switch LLM provider |
| `POST /api/llm/config` | `{provider_id, api_key, ...}` | Save provider config |
| `POST /api/tools/save_discovery` | `{conversation_id, project_slug}` | Save as seed doc |
| `POST /api/personality/reload` | — | Hot-reload personality |
| `POST /api/config` | `{personality}` | Update config |

### Streaming (SSE)

`POST /api/chat/stream` returns Server-Sent Events:
```
data: {"type": "token", "content": "Hello"}
data: {"type": "token", "content": " there"}
data: {"type": "done", "principles_active": [...], "tokens": {...}, "duration_ms": N}
```

---

## Evaluation

Test bot behavior against 9 customer scenarios:

```bash
python3 cli.py evaluate
```

Scenarios include: surface-level requests, vague requirements, pushback, technical customers, emotional customers, multi-problem, solution-fixated, returning customers, enterprise compliance.

---

## Running Tests

```bash
# All 485 tests
python3 -m pytest tests/ -v

# Quick run
python3 -m pytest tests/ -q
```

---

## Related Projects

| Project | Description | Link |
|---------|-------------|------|
| **Afterburner** | Sprint toolkit + project memory framework | [traceable-searchable-adr-memory-index](https://github.com/davidbmar/traceable-searchable-adr-memory-index) |
| **tool-telegram-whatsapp** | Sprint notification tool (separate from bot's Telegram) | [tool-telegram-whatsapp](https://github.com/davidbmar/tool-telegram-whatsapp) |
| **tool-s3-cloudfront-push** | Publish static sites to S3 + CloudFront | [tool-s3-cloudfront-push](https://github.com/davidbmar/tool-s3-cloudfront-push) |

---

## Troubleshooting

**"Address already in use" when starting server:**
```bash
lsof -ti :1203 | xargs kill -9
python3 -m bot.server
```

**"No module named 'bot'":**
Make sure you're in the project directory with the right venv:
```bash
cd ~/src/bot-customerObsessed-No-Prob-Bob-afterburner
source .venv/bin/activate
python3 -m bot.server
```

**Telegram bot not responding:**
Check the logs: `tail -f /tmp/bot-server.log`
- If you see "Telegram polling started" — it's working, wait ~20s for Ollama response
- If you don't see it — check your token in `~/.config/afterburner-bots/config.json`

**Slow responses (20-40s):**
That's normal for local Ollama. Switch to Claude Haiku in Settings (⚙) for ~2 second responses.

---

## License

Private repository.
