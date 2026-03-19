# Sprint 1

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

Merge Order
1. agentA-personality
2. agentB-llm-webchat
3. agentC-memory-cli

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
python3 -c "from bot.personality import PersonalityLoader; p = PersonalityLoader('personalities'); pd = p.load('customer-discovery'); print('Personality:', pd.name); assert len(pd.principles) >= 3"
python3 -c "from bot.memory import ConversationMemory; m = ConversationMemory('/tmp/test-mem'); m.add('user', 'hello'); assert len(m.get_history()) == 1; print('Memory: ok')"
python3 -c "from bot.llm import OllamaClient; print('LLM client: ok')"
```

Previous Sprint
- This is Sprint 1 — no previous sprint. Project scaffolding exists with stub modules in bot/ (personality.py, llm.py, gateway.py, memory.py, server.py, tools.py, config.py, polling.py). Personality docs exist (base.md, customer-discovery.md). pyproject.toml configured.

## agentA-personality

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

## agentB-llm-webchat

Objective
- Build the LLM client (Ollama) and web chat UI with debug panel

Tasks
- Rewrite `bot/llm.py` with an `OllamaClient` class that:
  - Connects to Ollama at `http://localhost:11434`
  - Method: `chat(messages, system_prompt, tools=None) -> response` using the chat API
  - Supports tool calling (function definitions passed as tools parameter)
  - Handles streaming responses
  - Configurable model name (default: `qwen3.5:latest`)
  - Timeout handling and error recovery
- Rewrite `bot/server.py` as the HTTP server on port 1203:
  - `GET /` → serves the chat UI (bot/chat_ui.html)
  - `POST /api/chat` → accepts `{message, conversation_id}`, returns `{response, tools_called, principles_active}`
  - `GET /api/history?conversation_id=X` → returns conversation history
  - `GET /api/personality` → returns current personality info (name, principles)
  - Stale process cleanup on startup (kill existing process on port 1203)
  - Graceful shutdown on SIGINT/SIGTERM
- Rewrite `bot/chat_ui.html` as a self-contained dark-themed chat interface:
  - Message bubbles (user on right, bot on left)
  - Auto-scroll, loading spinner during responses
  - Debug panel (collapsible) showing: active principles, tools called, token count, response latency
  - Input field with Enter to send
  - Conversation ID tracking (new conversation button)
- Rewrite `bot/gateway.py` as the orchestration layer:
  - Takes a message + conversation_id
  - Loads personality, builds system prompt
  - Retrieves conversation history from memory
  - Calls LLM with system prompt + history + tools
  - Saves response to memory
  - Returns response + metadata (tools_called, principles)

Acceptance Criteria
- `python3 bot/server.py` starts on port 1203 without errors
- `curl http://localhost:1203/` returns the chat UI HTML
- `curl -X POST http://localhost:1203/api/chat -d '{"message":"hello","conversation_id":"test1"}'` returns a JSON response (even if Ollama isn't running, should return a clear error)
- Chat UI loads in browser with dark theme and debug panel
- Gateway connects personality → LLM → memory pipeline

## agentC-memory-cli

Objective
- Build the conversation memory system and CLI commands

Tasks
- Rewrite `bot/memory.py` with a `ConversationMemory` class that:
  - Stores conversations as JSONL files (one file per conversation_id)
  - Storage dir: `~/.local/share/afterburner-bot/conversations/`
  - Method: `add(role, content, metadata=None)` — appends to JSONL
  - Method: `get_history(conversation_id, limit=50) -> list[dict]` — returns messages
  - Method: `list_conversations() -> list[str]` — returns conversation IDs
  - Method: `clear(conversation_id)` — deletes a conversation
  - Each entry: `{"role": "user"|"assistant", "content": "...", "timestamp": "...", "metadata": {...}}`
  - Conversations don't bleed between IDs (isolation)
- Rewrite `cli.py` with three commands using argparse:
  - `python3 cli.py start` — starts the web server (port 1203) + prints URL
  - `python3 cli.py chat` — interactive CLI chat loop (reads from stdin, prints responses)
  - `python3 cli.py status` — shows bot status: is server running? which personality? how many conversations?
  - Uses the same gateway as the web chat (shared code path)
- Write tests in `tests/test_memory.py`:
  - Add messages and retrieve history
  - Conversation isolation (different IDs don't mix)
  - List conversations returns correct IDs
  - Clear deletes conversation data
- Rewrite `bot/config.py` for centralized configuration:
  - Config file: `~/.config/afterburner-bots/config.json`
  - Defaults: ollama_url, model_name, personality_name, data_dir
  - Method: `load() -> Config` with sensible defaults if file doesn't exist

Acceptance Criteria
- Memory stores and retrieves messages correctly with conversation isolation
- `python3 cli.py start` launches the server
- `python3 cli.py status` shows status info
- `python3 -m pytest tests/test_memory.py -v` passes
- Config loads with sensible defaults even without a config file
