# Sprint 14

Goal
- Add conversation sidebar — list past conversations, click to switch (F-032)
- Fix token count reporting — shows inflated numbers (B-018)
- Fix provider display in header — shows wrong provider name after Sprint 12 changes (B-019)
- Add token cost display for paid providers (F-030)

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- Web chat UI is self-contained in bot/chat_ui.html (no build step, vanilla JS)
- Single agent to avoid merge conflicts — all changes touch interconnected files

Merge Order
1. agentA-conversations-and-tokens

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 13: server direct-run fix, save-as-seed API, auto-synthesis after 5 exchanges, auto-scroll, mobile responsive CSS. 234 tests pass.
- Conversation persistence works via localStorage but no way to see past conversations
- Token count shows 1378 out for a 20-word response — likely counting thinking/reasoning tokens
- Header shows `ollama · qwen3:4b` instead of expected `qwen-3.5 · qwen3.5:latest`
- Published to CloudFront: https://d3gb25yycyv0d9.cloudfront.net

## agentA-conversations-and-tokens

Objective
- Add conversation management sidebar and fix token/provider display issues

Tasks
1. **Conversation sidebar** — Update `bot/chat_ui.html`:
   - Add a collapsible sidebar (left side, 250px wide) listing past conversations
   - Each entry shows: first user message (truncated to 40 chars), timestamp, message count
   - Read conversation list from localStorage keys matching `conv-*` pattern
   - Click a conversation → load it (swap messages, update conversation ID)
   - Current conversation highlighted
   - "+ New Chat" in sidebar header starts a fresh conversation
   - Sidebar hidden by default on mobile (< 768px), toggle via hamburger icon
   - Sidebar toggle button in header (list icon or hamburger)

2. **Fix token count** — Update `bot/gateway.py` and/or `bot/llm.py`:
   - Investigate why OllamaClient reports 1378 output tokens for a 20-word response
   - The Ollama `/api/chat` response includes `eval_count` (actual output tokens) — use this instead of counting characters or using the full response length
   - For streaming, accumulate the actual token count from the final response metadata
   - For AnthropicClient, use `response.usage.output_tokens`
   - Update `LLMResponse` to include accurate `input_tokens` and `output_tokens`

3. **Fix provider display** — Update `bot/chat_ui.html` or `bot/server.py`:
   - Header should show the active provider label from LLM_PROVIDERS (e.g., "Qwen 3.5" not "ollama")
   - Check `/api/llm/providers` response — ensure it returns the active provider's label and model
   - Update header display logic to use `provider.label · provider.model · personality`

4. **Token cost display** — Update `bot/chat_ui.html`:
   - After each message, if using a paid provider (Claude or ChatGPT), show estimated cost
   - Cost calculation: `input_tokens * input_price + output_tokens * output_price`
   - Approximate prices per 1M tokens:
     - Claude Haiku: $0.25 in / $1.25 out
     - Claude Sonnet: $3 in / $15 out
     - Claude Opus: $15 in / $75 out
     - ChatGPT gpt-4o: $2.50 in / $10 out
   - Show in debug panel as "Cost: $0.0023" or "Cost: free" for Ollama
   - Also show cumulative session cost

5. **Write tests**:
   - Test accurate token counting from Ollama response metadata
   - Test provider label resolution
   - Test cost calculation for different providers
   - Target: 245+ total tests

6. **Update backlog** — Mark F-032, F-030, B-018, B-019 as Complete (Sprint 14)

Acceptance Criteria
- Sidebar shows list of past conversations from localStorage
- Click a conversation → messages load correctly
- Token counts match actual output (not inflated)
- Header shows "Qwen 3.5 · qwen3.5:latest · customer-discovery" format
- Debug panel shows cost for paid providers, "free" for Ollama
- `.venv/bin/python3 -m pytest tests/ -v` — 245+ tests, 0 failures
