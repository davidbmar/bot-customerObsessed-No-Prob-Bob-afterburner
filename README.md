# No Prob Bob — Customer Discovery Agent

> Talk to customers first, build later. This bot obsessively understands the problem before a single line of code is written.

A conversational AI agent that guides customer discovery interviews, extracts insights, and saves structured seed documents to [Afterburner](https://github.com/davidbmar/traceable-searchable-adr-memory-index) projects. Supports **text chat**, **push-to-talk voice** (speech-to-text + text-to-speech), and **Google Sign-In** authentication.

**[Setup Guide](#setup-guide)** · **[Voice Features](#voice-features)** · **[Google Sign-In](#google-sign-in-setup)** · **[Telegram](#telegram-setup)** · **[API Reference](#api-reference)** · **[Dashboard](https://d3gb25yycyv0d9.cloudfront.net)**

---

## Setup Guide

### What You Need

| Component | Purpose | Required? |
|-----------|---------|-----------|
| [Ollama](https://ollama.com) | Local LLM (free, private, no API key) | Yes (or use Claude/ChatGPT instead) |
| Python 3.11+ | Runs the bot server | Yes |
| Voice deps (piper-tts, faster-whisper) | Push-to-talk, TTS audio responses | Optional |
| Google OAuth Client ID | Per-user sign-in with Google accounts | Optional |
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

# Install core dependencies
pip install -e ".[dev]"

# Install voice + auth dependencies (optional but recommended)
pip install "piper-tts>=1.4" "faster-whisper>=1.0" "numpy>=1.24" "scipy>=1.11" "google-auth[requests]>=2.20"
```

### Step 3: Create a `.env` File (Optional)

Copy the example and fill in what you need:

```bash
cp .env.example .env
```

The `.env` file supports these settings:

```bash
# Server port (default 1203)
PORT=1203

# LLM provider — auto-detects priority: Claude > OpenAI > Ollama
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
OPENAI_API_KEY=sk-...           # For ChatGPT
OLLAMA_MODEL=qwen3:4b           # For Ollama (default)

# Google Sign-In (see "Google Sign-In Setup" section below)
GOOGLE_CLIENT_ID=
ALLOWED_EMAILS=

# Telegram bot
TELEGRAM_BOT_TOKEN=
```

### Step 4: Start the Bot

**Option A — Simple start:**

```bash
source .venv/bin/activate
python3 -m bot.server
```

**Option B — Production launcher with watchdog** (recommended):

```bash
bash scripts/run.sh
```

The production launcher (`scripts/run.sh`) provides:
- **Auto-starts Ollama** if not running, pulls the model if missing, warms it into GPU memory
- **Health checks** on startup — verifies the server is responding before declaring ready
- **Watchdog** — checks `/api/health` every 60 seconds, auto-restarts on failure
- **caffeinate** — prevents Mac from sleeping while running
- **Log tailing** — streams server logs to terminal in real-time
- **Clean shutdown** — Ctrl+C tears down everything gracefully

You should see:

```
=== Customer Discovery Agent ===

  Ollama running
  Model qwen3:4b: available
  Warming model into memory...

  Starting server on port 1203...
  Health check PASSED

=======================================
  URL: http://localhost:1203/chat
=======================================

=== Watchdog active — health check every 60s (Ctrl+C to stop) ===
```

### Step 5: Open the Web Chat

Go to **http://localhost:1203/chat** in your browser.

The bot will greet you. Try typing: **"We need a better way to onboard new employees"**

The bot will ask discovery questions about your current process — not jump to solutions.

---

## Voice Features

The bot supports **push-to-talk voice input** and **text-to-speech audio responses**. Speak your question, hear the answer.

### How It Works

```
You hold the mic button and speak
        │
        ▼
Browser records audio via MediaRecorder (WebM/Opus)
        │
        ▼
Browser converts to 16kHz PCM via OfflineAudioContext
        │
        ▼
POST /api/voice/transcribe (base64 PCM)
        │
        ▼
Server: Faster-Whisper STT (base model, ~75MB)
  └── Resamples to 16kHz, runs beam search
  └── Returns text + confidence + word-level timestamps
        │
        ▼
Transcribed text sent as chat message (same as typing it)
        │
        ▼
Bot response generated (streaming SSE)
        │
        ▼
POST /api/voice/synthesize {text, voice_id}
        │
        ▼
Server: Piper TTS (ONNX neural voice)
  └── Synthesizes at 22050Hz, resamples to 48kHz
  └── Returns WAV audio blob
        │
        ▼
Browser plays audio through speakers
```

### Push-to-Talk Controls

The microphone button (right side of the input area) supports:

| Platform | Action | What happens |
|----------|--------|-------------|
| **Mobile (iPhone/Android)** | Touch and hold | Records while held, transcribes on release |
| **Desktop** | Click and hold | Same — records while mouse is down |
| **Both** | Release / finger slides off | Recording stops, audio is sent for transcription |

Safety features:
- If your finger slides off the button on mobile, recording still stops (document-level `touchend` listener)
- If the browser `mouseleave`s the button on desktop, recording stops
- Recording indicator (red pulsing border) shows when active
- Green border shows when the bot is speaking back

### Speech-to-Text (STT) Details

Uses [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) — a CTranslate2 port of OpenAI's Whisper model.

| Setting | Value |
|---------|-------|
| Model | `base` (~75MB, auto-downloaded on first use) |
| Device | CPU with int8 quantization |
| Input | Any sample rate (resampled to 16kHz internally) |
| Language | English (hardcoded, changeable in `bot/stt.py`) |
| Output | Text + `no_speech_prob` + `avg_logprob` + per-word timestamps |

The `no_speech_prob` score (0.0-1.0) indicates how likely the audio contains no speech. High values mean the user was silent or there was only background noise.

### Text-to-Speech (TTS) Details

Uses [Piper](https://github.com/rhasspy/piper) — a fast neural TTS engine running ONNX models locally.

| Setting | Value |
|---------|-------|
| Default voice | `en_US-lessac-medium` |
| Output | 48kHz mono int16 PCM (wrapped in WAV for browser) |
| Model source | HuggingFace (auto-downloaded to `models/` on first use) |
| Model size | ~20-60MB per voice |

**Available voices (9 total):**

| Voice ID | Name | Language |
|----------|------|----------|
| `en_US-lessac-medium` | Lessac (US) | English |
| `en_US-hfc_female-medium` | HFC Female (US) | English |
| `en_US-hfc_male-medium` | HFC Male (US) | English |
| `en_US-libritts_r-medium` | LibriTTS (US) | English |
| `en_GB-alba-medium` | Alba (UK) | English |
| `en_GB-aru-medium` | Aru (UK) | English |
| `de_DE-thorsten-medium` | Thorsten | German |
| `fr_FR-siwis-medium` | Siwis | French |
| `es_ES-davefx-medium` | DaveFX | Spanish |

Voice models are downloaded from HuggingFace on first use and cached in the `models/` directory.

### Voice Without Dependencies

If `piper-tts` or `faster-whisper` are not installed, the server returns a clear error message (`501 Not Implemented`) and the rest of the app works normally. The mic button just won't function. Text chat is completely unaffected.

---

## Google Sign-In Setup

Google Sign-In gives each user their own identity — their avatar shows in the header, and sessions persist for 7 days. **This is completely optional.** Without it, the bot works with no authentication.

### How Auth Works

```
User clicks "Sign in with Google" button
        │
        ▼
Google Identity Services returns a JWT (signed token)
        │
        ▼
Browser sends JWT to POST /api/auth/google
        │
        ▼
Server verifies JWT signature with Google's public keys
  └── Checks issuer is accounts.google.com
  └── Checks email is verified
  └── Checks email is in ALLOWED_EMAILS (if set)
        │
        ▼
Server upserts user in SQLite (google_id, email, name, avatar)
        │
        ▼
Server creates a session token (secrets.token_urlsafe, 7-day expiry)
        │
        ▼
Browser stores session_token in localStorage
  └── On reconnect, sends token to GET /api/auth/session
  └── No re-login needed for 7 days
```

### Step 1: Create a Google OAuth Client ID

1. Go to [Google Cloud Console — Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: anything (e.g., "No Prob Bob")
5. Under **Authorized JavaScript origins**, add:
   - `http://localhost:1203` (for local development)
   - Your production URL if deploying
6. Click **Create**
7. Copy the **Client ID** (looks like `123456789-abc...apps.googleusercontent.com`)

### Step 2: Configure the Bot

Add to your `.env` file:

```bash
# Required: your OAuth Client ID from Step 1
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com

# Optional: restrict to specific email addresses (comma-separated)
# Leave empty to allow any verified Google account
ALLOWED_EMAILS=you@gmail.com,teammate@company.com
```

Or add it to `~/.config/afterburner-bots/config.json`:

```json
{
  "auth": {
    "google_client_id": "123456789-abcdefg.apps.googleusercontent.com",
    "allowed_emails": "you@gmail.com"
  }
}
```

### Step 3: Restart the Server

```bash
bash scripts/run.sh
```

When you open `http://localhost:1203/chat`, you'll see a Google Sign-In button. After signing in, your name and avatar appear in the header bar.

### Auth Database

User data is stored in `data/bot.db` (SQLite). Tables:

| Table | Purpose |
|-------|---------|
| `users` | Google ID, email, name, avatar URL, role, timestamps |
| `auth_sessions` | Session tokens with 7-day expiry, last-used tracking |
| `user_preferences` | Per-user voice, LLM provider, model, custom instructions |

Session tokens are generated with `secrets.token_urlsafe(32)` and auto-cleaned on expiry.

### Auth Without Google

If `GOOGLE_CLIENT_ID` is not set:
- No sign-in overlay appears
- The bot works exactly as before — no authentication required
- All voice and chat features work normally

---

## Web Chat

The web chat at `http://localhost:1203/chat` includes:

- **Push-to-talk voice** — hold the mic button to speak, hear responses read aloud
- **Streaming responses** — text appears word-by-word as the LLM generates
- **Google Sign-In** — optional per-user identity with avatar in header
- **Dark/light theme** — click the theme toggle (auto-detects your system preference)
- **Conversation sidebar** — click the menu icon to see past chats, search, delete, rename
- **Multi-provider LLM** — click Settings to switch between Ollama, Claude, or ChatGPT
- **Debug panel** — click "Debug" to see tokens, latency, cost, active principles
- **Save as Seed Doc** — after 3+ exchanges, save the conversation as a structured document
- **Auto-synthesis** — after 5+ exchanges, the bot summarizes into Problem/Users/Use Cases/Success Criteria
- **Mobile responsive** — works on phones with touch-friendly push-to-talk
- **Markdown rendering** — bot messages render bold, code, lists properly
- **Conversation persistence** — refresh the page, your chat is still there

### Switching LLM Providers

Click Settings in the header. You can switch between:

| Provider | Cost | Speed | Quality |
|----------|------|-------|---------|
| **Qwen 3.5 (Ollama)** | Free | ~20-40s | Good |
| **Claude Haiku** | ~$0.001/msg | ~2s | Great |
| **Claude Sonnet** | ~$0.01/msg | ~3s | Excellent |
| **Claude Opus** | ~$0.05/msg | ~5s | Best |
| **ChatGPT** | ~$0.005/msg | ~2s | Great |

For Claude, you need an API key. Set it in the Settings panel or in your `.env` file.

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

### Step 2: Add the Token

Either add to `.env`:

```bash
TELEGRAM_BOT_TOKEN=paste-your-token-here
```

Or add to `~/.config/afterburner-bots/config.json`:

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
bash scripts/run.sh
```

You should see:

```
Telegram polling started
Telegram polling enabled
```

### Step 4: Message Your Bot

Find your bot on Telegram by its username and send a message. It responds with the same customer discovery behavior as the web chat.

---

## Configuration

Config can come from two places (both are optional, values merge):

### `.env` file (project root)

Best for secrets and environment-specific settings:

```bash
PORT=1203
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OLLAMA_MODEL=qwen3:4b
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
ALLOWED_EMAILS=you@gmail.com
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
```

### `~/.config/afterburner-bots/config.json`

Best for persistent preferences:

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
  "auth": {
    "google_client_id": "",
    "allowed_emails": ""
  }
}
```

---

## How It Works

### Architecture

```
Customer (Web Chat / Voice / Telegram / CLI)
        │
        ▼
   ┌──────────────────────────────────┐
   │  HTTP Server (bot/server.py)     │
   │  ├── /chat          → Web UI     │
   │  ├── /api/chat      → Text chat  │
   │  ├── /api/auth/*    → Google SSO │
   │  ├── /api/voice/*   → STT + TTS │
   │  └── /api/llm/*     → Provider  │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │  Gateway (bot/gateway.py)        │
   │  ├── Loads personality           │
   │  ├── Retrieves conversation mem  │
   │  ├── Calls LLM                   │
   │  ├── Executes tools              │
   │  └── Auto-synthesizes at 5 turns │
   └──────────┬───────────────────────┘
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
  Ollama   Claude   ChatGPT

   ┌──────────────────────────────────┐
   │  Voice Pipeline                  │
   │  ├── STT: Faster-Whisper (base)  │
   │  └── TTS: Piper ONNX (9 voices) │
   └──────────────────────────────────┘

   ┌──────────────────────────────────┐
   │  Auth + Storage                  │
   │  ├── Google JWT verification     │
   │  ├── Session tokens (7-day)      │
   │  └── SQLite (data/bot.db)        │
   └──────────────────────────────────┘
```

**All interfaces share the same brain.** Web chat, voice, Telegram, and CLI all go through `Gateway.process_message()`. Switching the LLM provider in the web UI changes it for Telegram too.

### Module Map

| Module | Purpose |
|--------|---------|
| `bot/server.py` | HTTP server — routes, static files, SSE streaming |
| `bot/gateway.py` | Central brain — connects transports to LLM |
| `bot/llm.py` | LLM client abstraction (Ollama, Claude, OpenAI) |
| `bot/auth.py` | Google Sign-In JWT verification + session management |
| `bot/db.py` | SQLite database — users, auth sessions, preferences |
| `bot/tts.py` | Piper TTS — text to 48kHz PCM audio |
| `bot/stt.py` | Faster-Whisper STT — audio to text with timestamps |
| `bot/personality.py` | Personality framework with inheritance |
| `bot/memory.py` | Conversation memory with per-chat history |
| `bot/tools.py` | Afterburner integration tools |
| `bot/config.py` | Config loading from JSON + env vars |
| `bot/polling.py` | Telegram long-polling transport |
| `bot/chat_ui.html` | Self-contained web UI (HTML + CSS + JS) |
| `scripts/run.sh` | Production launcher with watchdog |

### Personality Framework

The bot's behavior is defined in markdown files in `personalities/`:
- `base.md` — core values (honest, helpful, focused)
- `customer-discovery.md` — discovery principles (Customer Obsession, Dive Deep, etc.)

Personalities support inheritance (customer-discovery extends base) and can be hot-reloaded without restarting the server.

### Tools

The bot has 6 Afterburner integration tools:

| Tool | What It Does | Access |
|------|-------------|--------|
| `list_projects` | Lists all registered Afterburner projects | Read |
| `get_project_summary` | Shows sprint status, bugs, sessions + lifecycle docs | Read |
| `get_sprint_status` | Checks current sprint progress via dashboard API | Read |
| `feedback_on_sprint` | "Here's what shipped — does it match?" | Read |
| `read_project_doc` | Reads README.md or any file from a project | Read |
| `save_discovery` | Saves conversation as a seed doc to a project | Write |
| `add_to_backlog` | Adds features/bugs to project backlog | Write |
| `generate_vision` | Creates a Vision doc from discovery | Write |

> **Security:** Telegram users get read-only tools only. Web chat users on localhost get full access. Write tools (save_discovery, add_to_backlog, generate_vision) are blocked for unauthenticated Telegram users to prevent data pollution.

---

## API Reference

### Chat Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/chat` | GET | — | Web chat UI |
| `/api/chat` | POST | `{message, conversation_id}` | Send message, get response |
| `/api/chat/stream` | POST | `{message, conversation_id}` | Send message, get SSE stream |
| `/api/health` | GET | — | Health check — LLM status, model, personality |
| `/api/history?chat_id=ID` | GET | — | Conversation message history |
| `/api/conversations/export?id=ID` | GET | — | Export conversation as markdown |

### Auth Endpoints

| Endpoint | Method | Body / Headers | Description |
|----------|--------|----------------|-------------|
| `/api/auth/google` | POST | `{credential: "JWT"}` | Authenticate with Google Sign-In JWT. Returns `{session_token, user}` |
| `/api/auth/session` | GET | `Authorization: Bearer TOKEN` | Validate a stored session token. Returns `{valid, user}` |
| `/api/auth/logout` | POST | `{session_token: "TOKEN"}` | Invalidate a session token |

### Voice Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/api/voice/transcribe` | POST | `{audio: "base64", sample_rate: 16000, format: "pcm"}` | Transcribe audio to text. Returns `{text, no_speech_prob, avg_logprob, timing}` |
| `/api/voice/synthesize` | POST | `{text: "Hello", voice_id: "en_US-lessac-medium"}` | Synthesize text to speech. Returns `audio/wav` binary |
| `/api/voice/voices` | GET | — | List available TTS voices with download status |

### LLM & Config Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/api/llm/providers` | GET | — | Available LLM providers + which is active |
| `/api/llm/switch` | POST | `{provider_id, model}` | Switch LLM provider at runtime |
| `/api/llm/config` | GET/POST | `{provider_id, api_key, ...}` | Read or save provider config |
| `/api/personality` | GET | — | Current personality info |
| `/api/personalities` | GET | — | List available personalities |
| `/api/personality/reload` | POST | — | Hot-reload personality from disk |
| `/api/config` | GET/POST | `{personality}` | Read or update bot config |
| `/api/projects` | GET | — | List Afterburner projects |
| `/api/tools/save_discovery` | POST | `{conversation_id, project_slug}` | Save conversation as seed doc |

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
# All tests
python3 -m pytest tests/ -v

# Quick run
python3 -m pytest tests/ -q
```

---

## Related Projects

| Project | Description | Link |
|---------|-------------|------|
| **Afterburner** | Sprint toolkit + project memory framework | [traceable-searchable-adr-memory-index](https://github.com/davidbmar/traceable-searchable-adr-memory-index) |
| **Voice Agent** | iPhone voice assistant (source of voice/auth code) | [iphone-and-companion-transcribe-mode](https://github.com/davidbmar/iphone-and-companion-transcribe-mode) |
| **tool-telegram-whatsapp** | Sprint notification tool (separate from bot's Telegram) | [tool-telegram-whatsapp](https://github.com/davidbmar/tool-telegram-whatsapp) |
| **tool-s3-cloudfront-push** | Publish static sites to S3 + CloudFront | [tool-s3-cloudfront-push](https://github.com/davidbmar/tool-s3-cloudfront-push) |

---

## Troubleshooting

**"Address already in use" when starting server:**
```bash
lsof -ti :1203 | xargs kill -9 2>/dev/null
python3 -m bot.server
```
Or use `bash scripts/run.sh` which handles stale processes automatically.

**"No module named 'bot'":**
Make sure you're in the project directory with the right venv:
```bash
cd ~/src/bot-customerObsessed-No-Prob-Bob-afterburner
source .venv/bin/activate
python3 -m bot.server
```

**Mic button not working (501 error):**
Voice dependencies aren't installed. Run:
```bash
pip install "piper-tts>=1.4" "faster-whisper>=1.0" "numpy>=1.24" "scipy>=1.11"
```

**First voice request is slow:**
The Whisper model (~75MB) and Piper voice model (~20-60MB) are downloaded on first use. Subsequent requests use the cached models.

**Google Sign-In button not appearing:**
- Check that `GOOGLE_CLIENT_ID` is set in `.env` or config.json
- Check the browser console for errors — the Google Identity Services library may be blocked by an ad blocker
- Make sure `http://localhost:1203` is listed in your OAuth client's **Authorized JavaScript origins**

**Telegram bot not responding:**
- If you see "Telegram polling started" in logs — it's working, wait ~20s for Ollama response
- If you don't see it — check your token in `.env` or config.json

**Slow responses (20-40s):**
That's normal for local Ollama. Switch to Claude Haiku in Settings for ~2 second responses.

**Watchdog keeps restarting:**
Check `logs/server.log` for the root cause. Common issues:
- Ollama crashed — restart it with `open -a Ollama`
- Port conflict — another process grabbed port 1203
- Python crash — check the traceback in the log

---

## License

Private repository.
