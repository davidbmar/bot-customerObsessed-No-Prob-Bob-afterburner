# Implementation Phases

## Phase 1: Personality framework + web chat + text bot MVP
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

## Phase 2: Full Afterburner integration + evaluation
- More tools: generate_vision, add_to_backlog, get_sprint_status
- Post-sprint feedback loop ("here's what shipped, does it match?")
- Evaluation framework with scenario tests
- Fact extraction from conversations (LLM-generated summaries)
- Multi-project support (backend registry)
- Web chat settings panel: switch personality, switch model, view memory

## Phase 3: Voice + multi-platform
- Whisper STT for Telegram voice messages
- WhatsApp support (reuse tool-telegram-whatsapp transport layer)
- Customer profiles (cross-conversation memory)
- TTS responses (optional — using existing voice repos)
- Personality inheritance tested with a second bot type (e.g., tech-support)

## Verification (Phase 1)

1. Personality loader: `python3 -c "from bot.personality import Personality; p = Personality('customer-discovery'); print(len(p.to_system_prompt()))"`
2. Start bot: `afterburner-bot start` (starts web server on :1203 + Telegram polling)
3. **Web chat test**: Open `http://localhost:1203/chat`, type "We need a login page" → bot asks about users and use cases (not "what kind of login?")
4. **Debug panel**: Verify principles shown as "Customer Obsession, Dive Deep", tools as "none called"
5. **Multi-turn**: Have 5-7 exchange conversation in web chat → bot synthesizes into Problem/Users/Use Cases/Success Criteria
6. **Telegram test**: Send same message in Telegram → same quality response
7. **CLI test**: `afterburner-bot chat "We need a login page"` → bot responds
8. **Tool call**: Confirm summary → bot calls save_discovery → seed doc written to project
9. **Memory**: Start new conversation, verify it doesn't bleed into previous
10. Existing tool-telegram-whatsapp notifications still work independently
11. Afterburner dashboard shows the project at `http://localhost:1201/afterburner-customer-bot/`
