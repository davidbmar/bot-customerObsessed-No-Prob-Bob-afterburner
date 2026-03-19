agentB-llm-webchat — Sprint 1

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
