agentA-multi-provider — Sprint 11

Previous Sprint Summary
─────────────────────────────────────────
- Sprint 10: UX polish — welcome message, debug panel, new chat button. 144 tests pass.
- Current LLM: OllamaClient only (qwen3.5 via localhost:11434)
- Need: Claude (3 tiers), ChatGPT, and any Ollama model — switchable from UI
─────────────────────────────────────────

Sprint-Level Context

Goal
- Multi-provider LLM: Ollama, Claude (Haiku/Sonnet/Opus), and ChatGPT
- Gear icon settings panel matching Afterburner dashboard's LLM provider pattern
- Runtime switching — change provider/model mid-conversation

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Single agent to avoid merge conflicts
- Reuse Afterburner's LLM_PROVIDERS pattern (see below) for speed
- API keys stored in config file or env vars, NEVER in code
- Install deps: .venv/bin/pip install anthropic openai

Reference — Afterburner dashboard's LLM_PROVIDERS dict (copy this pattern):
```python
LLM_PROVIDERS = {
    "qwen-3.5": {"label": "Qwen 3.5", "default_base_url": "http://localhost:11434/v1", "default_model": "qwen3.5:latest", "api_format": "openai", "needs_key": False, "model_choices": ["qwen3.5:latest", "qwen3.5:4b", "qwen3.5:9b", "qwen3.5:27b"]},
    "ollama-other": {"label": "Ollama (other)", "default_base_url": "http://localhost:11434/v1", "default_model": "mistral-nemo:latest", "api_format": "openai", "needs_key": False, "model_choices": ["mistral-nemo:latest", "deepseek-r1:14b", "llama3.1:8b", "gemma2:9b"]},
    "claude-haiku": {"label": "Claude Haiku", "default_base_url": "https://api.anthropic.com", "default_model": "claude-haiku-4-5-20251001", "api_format": "anthropic", "needs_key": True, "model_choices": ["claude-haiku-4-5-20251001"]},
    "claude-sonnet": {"label": "Claude Sonnet", "default_base_url": "https://api.anthropic.com", "default_model": "claude-sonnet-4-6", "api_format": "anthropic", "needs_key": True, "model_choices": ["claude-sonnet-4-6"]},
    "claude-opus": {"label": "Claude Opus", "default_base_url": "https://api.anthropic.com", "default_model": "claude-opus-4-6", "api_format": "anthropic", "needs_key": True, "model_choices": ["claude-opus-4-6"]},
    "chatgpt": {"label": "ChatGPT", "default_base_url": "https://api.openai.com/v1", "default_model": "gpt-5.4", "api_format": "openai", "needs_key": True, "model_choices": ["gpt-5.4", "gpt-5.4-pro", "gpt-5-mini", "gpt-4o"]},
}
```


Objective
- Add multi-provider LLM support with gear icon config panel

Tasks
1. Add `LLM_PROVIDERS` dict to `bot/llm.py` (copy from reference above):
   - Each provider has: label, default_base_url, default_model, api_format ("openai" or "anthropic"), needs_key, model_choices
   - Two api_format types:
     - `"openai"` — works for Ollama AND ChatGPT (both use OpenAI-compatible API)
     - `"anthropic"` — uses the anthropic SDK

2. Refactor `bot/llm.py`:
   - Keep `OllamaClient` but rename to `OpenAICompatibleClient` — it works for any OpenAI-format API (Ollama, ChatGPT)
   - Add `AnthropicClient` using the `anthropic` SDK:
     - `pip install anthropic` in venv
     - Method: `chat(messages, system_prompt, tools=None) -> LLMResponse`
     - Pass system prompt as `system` parameter (not in messages)
     - Map tool definitions to Claude's tool format
   - Add factory: `get_client(provider_id) -> LLMClient` that reads LLM_PROVIDERS and returns the right client
   - Both clients return the same `LLMResponse` dataclass

3. Add `bot/llm_config.py` for per-provider config persistence:
   - Store in `~/.config/afterburner-bots/llm-providers.json` (same pattern as Afterburner)
   - Each provider entry: base_url, model, api_key (encrypted or at least not plaintext — or just read from env)
   - `load_provider_config(provider_id) -> dict`
   - `save_provider_config(provider_id, config) -> None`
   - `get_active_provider() -> str`
   - `set_active_provider(provider_id) -> None`

4. Update `bot/gateway.py`:
   - On init, use `get_client(active_provider)` instead of hardcoded OllamaClient
   - Add `switch_provider(provider_id, model=None)` method that swaps the LLM client at runtime

5. Update `bot/server.py` — add API endpoints:
   - `GET /api/llm/providers` — returns LLM_PROVIDERS dict with current active provider marked
   - `POST /api/llm/switch` — switch active provider + model, takes effect immediately
   - `GET /api/llm/config` — returns current provider config (base_url, model, has_key)
   - `POST /api/llm/config` — save provider-specific config (api_key, base_url override)

6. Update `bot/chat_ui.html` — gear icon opens config panel:
   - Gear icon (⚙) in header opens a slide-out or modal panel
   - Panel sections:
     - **Provider selector** — radio buttons or cards for each provider (with label and icon)
     - **Model selector** — dropdown populated from the selected provider's model_choices
     - **API Key** — masked input, only shown when provider needs_key=True
     - **Base URL** — text input, pre-filled with default, editable for custom endpoints
     - **Save** button — saves config and switches provider
     - **Test Connection** button — pings the provider and shows OK/error
   - Current provider + model shown in header bar dynamically
   - When provider switches, header updates immediately

7. Install dependencies:
   ```bash
   .venv/bin/pip install anthropic openai
   ```

8. Write tests in `tests/test_llm.py`:
   - `get_client("qwen-3.5")` returns OpenAICompatibleClient
   - `get_client("claude-sonnet")` returns AnthropicClient
   - `get_client("chatgpt")` returns OpenAICompatibleClient
   - Provider config saves and loads correctly
   - Unknown provider raises clear error
   - Target: 155+ total tests

9. Update backlog with completion status

Acceptance Criteria
- `from bot.llm import get_client, LLM_PROVIDERS` works
- Settings panel shows all 6 providers with model dropdowns
- Switching to Claude → next message uses Claude API
- Switching to ChatGPT → next message uses OpenAI API
- Switching back to Ollama → next message uses local Ollama
- API keys saved to config file, loaded from env as fallback
- Header shows current provider + model
- `.venv/bin/python3 -m pytest tests/ -v` — 155+ tests, 0 failures
