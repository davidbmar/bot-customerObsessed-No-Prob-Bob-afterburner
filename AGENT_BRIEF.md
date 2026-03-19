agentC-memory-cli — Sprint 1

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
