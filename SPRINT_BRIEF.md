# Sprint 11

Goal
- Multi-provider LLM support: Claude (Haiku, Sonnet, Opus) + Ollama models
- Model selector in web chat UI — switch providers and models without restarting
- Provider config in settings panel (API keys, base URLs)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent to avoid merge conflicts
- Claude API uses the anthropic SDK — install it in venv
- API keys stored in config file (~/.config/afterburner-bots/config.json), NEVER in code

Merge Order
1. agentA-multi-provider

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -c "from bot.llm import get_client; print('Multi-provider: OK')"
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -3
```

Previous Sprint
- Sprint 10: UX polish — welcome message, debug panel toggle, new chat button, typing indicator. 144 tests pass.
- Bot works end-to-end with Ollama (qwen3.5). Web chat, Telegram, CLI, 6 tools, evaluation framework.
- Current LLM client only supports Ollama. Need to add Claude and make it switchable at runtime.

## agentA-multi-provider

Objective
- Add multi-provider LLM support with runtime switching via the web chat UI

Tasks
1. Refactor `bot/llm.py` to support multiple providers:
   - Create a base `LLMClient` protocol/ABC with method: `chat(messages, system_prompt, tools=None) -> LLMResponse`
   - Keep existing `OllamaClient` as one implementation
   - Add `AnthropicClient` that uses the `anthropic` SDK:
     - Supports claude-haiku-4-5-20251001, claude-sonnet-4-6, claude-opus-4-6
     - Reads API key from config or ANTHROPIC_API_KEY env var
     - Maps tool definitions to Claude's tool format
     - Returns same LLMResponse structure
   - Add factory function: `get_client(provider, model, config) -> LLMClient`
   - Provider names: "ollama", "anthropic"

2. Install anthropic SDK: `.venv/bin/pip install anthropic`

3. Update `bot/config.py`:
   - Add `provider` field (default: "ollama")
   - Add `anthropic_api_key` field (default: from env ANTHROPIC_API_KEY)
   - Add `available_models` dict mapping provider → list of models:
     ```python
     {
       "ollama": ["qwen3.5:latest", "llama3.1:8b", "mistral:latest"],
       "anthropic": ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-6"]
     }
     ```

4. Update `bot/gateway.py`:
   - Use `get_client(config.provider, config.model_name, config)` instead of hardcoded OllamaClient
   - Support switching provider/model at runtime via config update

5. Update `bot/server.py`:
   - `GET /api/models` — returns available providers and their models
   - `POST /api/config` — allow switching provider + model (updates gateway's client)
   - Return current provider in /api/config response

6. Update `bot/chat_ui.html` settings panel:
   - Add provider selector dropdown: "Ollama" / "Claude"
   - When provider changes, model dropdown updates to show that provider's models
   - Show API key input for Claude (masked, with save button)
   - Show current provider + model in the header bar (replace "qwen3:4b" with dynamic text)
   - Provider switch takes effect immediately (next message uses new provider)

7. Update model indicator in chat header:
   - Show provider icon/label + model name: "🦙 qwen3.5" or "🤖 claude-sonnet"
   - Green dot when provider is reachable, red when not

8. Write tests:
   - `tests/test_llm.py`: test OllamaClient and AnthropicClient can be instantiated
   - Test `get_client` factory returns correct type
   - Test config saves/loads provider setting
   - Mock-based tests (don't actually call APIs)
   - Target: 155+ tests

9. Update backlog with new feature entries

Acceptance Criteria
- `from bot.llm import get_client, OllamaClient, AnthropicClient` works
- Settings panel shows provider dropdown (Ollama/Claude) and model dropdown
- Switching to Claude in settings + sending message uses Claude API
- Switching back to Ollama uses Ollama
- Header shows current provider + model dynamically
- `.venv/bin/python3 -m pytest tests/ -v` — 155+ tests, 0 failures
- API key stored in config file, not hardcoded
