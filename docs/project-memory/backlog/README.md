# Backlog

Track bugs and feature requests here.

## Bugs

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| B-001 | gateway.py imports OllamaLLM but llm.py exports OllamaClient | Critical | Fixed (Sprint 2) |
| B-002 | BotConfig missing model_name | Critical | Fixed (Sprint 2) |
| B-003 | server.py cascading import failure | Critical | Fixed (Sprint 2) |
| B-004 | pytest not installed in venv | High | Fixed (Sprint 2) |
| B-005 | .venv stale path from project rename | Medium | Fixed |
| B-006 | save_discovery not exported from bot/tools.py | High | Fixed (Sprint 3) |
| B-007 | test uses chat_id but server uses conversation_id | Medium | Fixed (Sprint 3) |
| B-008 | sprint-run.sh crashes with `local -A` on zsh — agents run but merge/polling dies | High | Complete (Sprint 32) |
| B-009 | Dashboard shows 0 for sprints/sessions/ADRs — no PROJECT_STATUS docs built | Medium | Fixed (Sprint 12) |
| B-010 | GitHub not configured in dashboard project entry | Low | Open |
| B-011 | CLI status crashes — _auto_discover_projects expects dict but gets strings from projects.json | High | Fixed (Sprint 9) |
| B-012 | Tool naming inconsistency — feedback_on_sprint vs get_sprint_feedback pattern | Medium | Fixed (Sprint 9) |
| B-013 | Debug panel visible by default on page load — F-019 (Sprint 10) may not have fully landed | Low | Complete (Sprint 16) |
| B-014 | No PROJECT_STATUS docs exist — sprint-merge.sh never ran (all 11 sprints merged manually or via sprint-run.sh that crashed) | High | Complete (Sprint 12) |
| B-015 | Dashboard backlog counts show 0 — build-sprint-data.sh doesn't parse backlog/README.md into backlog.json | Medium | Complete (Sprint 31) |
| B-016 | Ollama Qwen 3.5 response latency ~22s for simple messages — acceptable but noticeable | Low | Open |
| B-017 | `python3 bot/server.py` fails with relative import error — must use `python3 -m bot.server` (F-022 regression) | Medium | Complete (Sprint 13) |
| B-018 | Token count inflated — shows 1378 out tokens for a 20-word response, likely counting thinking tokens or misreporting | Low | Complete (Sprint 14) |
| B-019 | Header shows `ollama · qwen3:4b` instead of `qwen-3.5 · qwen3.5:latest` — health endpoint returns provider_label: "ollama" not "Qwen 3.5" | Low | Complete (Sprint 17) |
| B-020 | Sprint 12 agent done markers not written — sprint-launch.sh done detection broken (related to B-008) | Medium | Open |
| B-021 | Dashboard only shows Sprints 1-11 — Sprints 12-16 need PROJECT_STATUS docs generated | Medium | Complete (Sprint 17) |
| B-022 | Debug panel still visible on fresh load despite B-013 fix — localStorage may be overriding default hidden state | Low | Complete (Sprint 18) |
| B-023 | Sidebar visible by default on desktop — should be collapsed on first visit, user opens when needed | Low | Complete (Sprint 18) |
| B-024 | Light theme is now the default after clearing localStorage — should detect system preference with prefers-color-scheme | Low | Complete (Sprint 18) |
| B-025 | Send button stays disabled after programmatic text input — only listens for `input` event, misses `keyup`/`change` so paste/autofill doesn't enable it | Low | Complete (Sprint 21) |
| B-026 | No favicon — browser shows 404 for `/favicon.ico` on every page load | Low | Complete (Sprint 21) |
| B-027 | Copy button only appears on first bot message, not on subsequent bot messages | Medium | Complete (Sprint 21) |
| B-028 | Active Project dropdown in Settings panel is empty — should list available projects or be hidden when only one project exists | Low | Complete (Sprint 22) |
| B-029 | Console shows 10 ONNX runtime warnings on every page load when VAD initializes — noisy but harmless | Low | Complete (Sprint 30) |
| B-037 | Bot says "I'm text-only" and "I can't hear audio" when user speaks via voice — personality system prompt doesn't mention STT/TTS voice capabilities | High | Complete (Sprint 28) |
| B-038 | Input filter lets TV/movie audio through — hands-free mode transcribes background media and sends full movie scenes to LLM as user messages | Medium | Complete (Sprint 29) |
| B-035 | pyproject.toml [dev] group missing anthropic, openai, google-auth — venv rebuild breaks login and LLM providers | High | Complete (Sprint 27) |
| B-036 | scripts/start.sh doesn't install optional deps — new clone requires manual pip install of anthropic/google-auth | Medium | Complete (Sprint 27) |
| B-030 | Conversation restore fails — clicking saved conversation in sidebar shows only welcome message, not the actual history (sidebar shows "9 msgs" but chat area shows 1) | High | Complete (Sprint 22) |
| B-031 | New conversations not saved to sidebar — after +New Chat and sending messages, conversation doesn't appear as new sidebar entry | High | Complete (Sprint 22) |
| B-032 | Docs panel stats hardcoded — says "20 sprints · 631 tests · 57 features" instead of actual counts (now 21/636/59) | Low | Complete (Sprint 22, /api/stats added Sprint 23) |
| B-033 | Tool result message uses OpenAI format for Claude API — causes 400 error when bot calls Afterburner tools with Claude provider | Critical | Fixed (hotfix) |
| B-034 | Restored bot messages lose paragraph spacing — old conversations saved via textContent have "word.Next sentence" instead of paragraph breaks | Medium | Complete (Sprint 23) |
| B-039 | Pause button doesn't stop VAD listening — clicking Pause (⏸) only cancels TTS but VAD immediately resumes and captures ambient noise, sending phantom messages to LLM | High | Complete (Sprint 31) |
| B-040 | Stop speaking doesn't pause mic — "Stop speaking" banner button cancels TTS but VAD re-triggers instantly, picking up background audio as new user input | High | Complete (Sprint 31) |
| B-041 | Hands-free auto-starts on page load — VAD begins listening immediately when page loads without user opting in, causing unintended voice captures | Medium | Complete (Sprint 31) |
| B-042 | Bot tools return raw error instead of friendly message when dashboard API unreachable — get_sprint_status and get_project_summary show "Tool error: Expecting value" instead of helpful fallback | Medium | Complete (Sprint 31) |
| B-043 | Missing PROJECT_STATUS docs for Sprints 30-31 — dashboard only shows up to Sprint 29, needs generation | Medium | Complete (Sprint 32) |
| B-044 | ONNX warnings still fire despite ort.env.logLevel='error' — WASM compilation warnings happen before JS config takes effect | Low | Open |
| B-045 | Active Project dropdown shows "No projects registered" — _auto_discover_projects() can't parse projects.json dict format (expects list, gets {projects:[...]}) | Medium | Complete (hotfix post-Sprint 34) |
| B-046 | Bot reports Sprint 29 as "latest" when Sprints 30-32 exist — feedback_on_sprint reads stale sprints.json, needs rebuild after each sprint | Medium | Complete (Sprint 33, F-074 auto-rebuild) |
| B-047 | Missing PROJECT_STATUS doc for Sprint 32 — dashboard shows 31 sprints but Sprint 32 was completed | Medium | Complete (Sprint 33) |
| B-048 | sprint-config.sh DEFAULT_TEST_CMD uses system python3 instead of .venv/bin/python3 — sprint-run.sh verification fails on macOS | Medium | Open |
| B-049 | Missing PROJECT_STATUS docs for Sprints 33-34 — needs generation for dashboard to show recent sprints | Medium | Open |

## Features

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| F-001 | Telegram polling transport | High | Complete (Sprint 2) |
| F-002 | save_discovery tool | High | Complete (Sprint 3) |
| F-003 | get_project_summary tool | Medium | Complete (Sprint 6) |
| F-004 | End-to-end test: conversation → seed doc | High | Complete (Sprint 3) |
| F-005 | Evaluation framework with YAML scenario tests | Medium | Complete (Sprint 6) |
| F-006 | Fact extraction from conversations | Medium | Complete (Sprint 6) |
| F-007 | Web chat settings panel | Low | Complete (Sprint 7) |
| F-008 | CLI chat command | Medium | Complete (Sprint 3) |
| F-009 | CLI status command | Low | Complete (Sprint 3) |
| F-010 | Web chat debug panel — tools called, principles, tokens, latency | High | Complete (Sprint 7) |
| F-011 | get_sprint_status tool | Medium | Complete (Sprint 7) |
| F-012 | add_to_backlog tool | Medium | Complete (Sprint 6) |
| F-013 | Multi-project support — bot can switch between Afterburner projects | High | Complete (Sprint 8) |
| F-014 | Post-sprint feedback loop — "here's what shipped, does it match?" | Medium | Complete (Sprint 8) |
| F-015 | generate_vision tool — bot generates Vision doc from discovery conversation | High | Complete (Sprint 8) |
| F-016 | Conversation export — download chat as markdown | Low | Complete (Sprint 9) |
| F-017 | Bot personality hot-reload — change personality without restarting server | Medium | Complete (Sprint 9) |
| F-018 | Welcome message — bot greets user on first load instead of empty chat | High | Complete (Sprint 10) |
| F-019 | Debug panel default hidden — toggle on, not always visible | Medium | Complete (Sprint 10) |
| F-020 | New Conversation button in main chat header (not just settings) | Medium | Complete (Sprint 10) |
| F-021 | Progress indicator — animated dots + elapsed time counter | Medium | Complete (Sprint 10) |
| F-022 | `python3 bot/server.py` should work without -m flag (add __main__.py entry point) | Medium | Complete (Sprint 10) |
| F-023 | Multi-provider LLM — Ollama + Claude (Haiku/Sonnet/Opus) + ChatGPT, runtime switching | High | Complete (Sprint 11) |
| F-024 | Generate PROJECT_STATUS docs retroactively for Sprints 1-11 so dashboard shows sprint history | High | Complete (Sprint 12) |
| F-025 | Streaming responses — show bot text as it generates instead of waiting for full response | High | Complete (Sprint 12) |
| F-026 | Keyboard shortcut: Enter to send message (currently requires clicking Send button) | Medium | Already exists (line 586) |
| F-027 | Mobile-responsive web chat — UI is desktop-only, needs viewport meta + responsive CSS | Medium | Complete (Sprint 13) |
| F-028 | Conversation persistence across page reloads — currently loses chat on refresh | Medium | Complete (Sprint 12) |
| F-029 | Error handling in web chat — show user-friendly message when LLM is unreachable | Medium | Complete (Sprint 12) |
| F-030 | Token cost display — show estimated cost per message when using paid providers (Claude/ChatGPT) | Low | Complete (Sprint 14) |
| F-031 | Auto-scroll to bottom when new messages arrive or text streams in | Medium | Complete (Sprint 13) |
| F-032 | Conversation list sidebar — see past conversations and switch between them | Medium | Complete (Sprint 14) |
| F-033 | Export conversation as seed doc — "Save as seed" button that calls save_discovery from the UI | High | Complete (Sprint 13) |
| F-034 | Bot synthesis step — after 5-7 exchanges, bot auto-generates Problem/Users/Use Cases/Success Criteria summary | High | Complete (Sprint 13) |
| F-035 | Expand evaluation scenarios from 3 to 8+ with diverse customer types | Medium | Complete (Sprint 15) |
| F-036 | Delete conversation from sidebar | Medium | Complete (Sprint 15) |
| F-037 | Search conversations by keyword in sidebar | Medium | Complete (Sprint 15) |
| F-038 | Dark/light theme toggle with CSS custom properties | Low | Complete (Sprint 15) |
| F-039 | End-to-end integration test: discovery conversation → save seed → verify in Afterburner project | High | Complete (Sprint 16) |
| F-040 | Typing indicator shows bot avatar animation while streaming (pulse or dots) | Low | Complete (Sprint 17) |
| F-041 | Conversation title editing — click title in sidebar to rename | Low | Complete (Sprint 18) |
| F-042 | README with getting-started guide, screenshots, and API reference | High | Complete (Sprint 16) |
| F-043 | CLI evaluate command improvements — show pass/fail per scenario with colors | Medium | Complete (Sprint 16) |
| F-044 | Markdown rendering in bot messages — support **bold**, *italic*, `code`, lists, headers | High | Complete (Sprint 19) |
| F-045 | Message timestamp grouping — group messages by date ("Today", "Yesterday", "Mar 19") | Medium | Complete (Sprint 19) |
| F-046 | Notification sound on bot response (optional, toggleable) | Low | Complete (Sprint 23) |
| F-048 | Input quality filter — drop garbage STT before hitting LLM (port from voice-calendar-scheduler) | High | Complete (Sprint 20) |
| F-049 | Hands-free continuous speech mode with browser-side VAD (Silero VAD WASM) | High | Complete (Sprint 20) |
| F-050 | Echo cancellation — mute mic while TTS is playing to prevent feedback loop | High | Complete (Sprint 20) |
| F-051 | Configurable silence threshold for hands-free mode (1-3 seconds) | Medium | Complete (Sprint 20) |
| F-052 | Fast path — instant answers for simple queries without LLM ("help", "what can you do") | Medium | Complete (Sprint 20) |
| F-047 | Export full conversation as structured seed doc with Problem/Users/Use Cases sections | High | Complete (Sprint 19) |
| F-053 | Voice activity waveform — show amplitude visualization during recording so user knows mic is hearing them | Medium | Complete (Sprint 21) |
| F-054 | Keyboard shortcut Escape to stop bot speaking — faster than clicking the Stop button | Medium | Complete (Sprint 21) |
| F-055 | Copy button on all bot messages — currently only the first message has a Copy button | Medium | Complete (Sprint 21) |
| F-056 | Favicon — add a simple favicon so browser tab has an icon and no 404 | Low | Complete (Sprint 21) |
| F-057 | Google SSO localhost dev bypass — skip auth overlay when running on localhost without valid Google client ID | Medium | Complete (Sprint 21) |
| F-058 | Conversation auto-save to sidebar — new conversations should persist to sidebar list after first user message without requiring page reload | High | Complete (Sprint 22) |
| F-059 | Code block syntax highlighting — bot markdown code blocks render but without language-specific syntax colors | Low | Complete (Sprint 23) |
| F-060 | /api/stats endpoint — returns sprint/test/feature counts for Docs panel auto-update | Low | Complete (Sprint 23) |
| F-061 | Configurable VAD/barge-in settings — expose Silero VAD thresholds (sensitivity, min speech, barge-in toggle) as sliders in Settings panel | Medium | Complete (Sprint 24) |
| F-062 | Generate PROJECT_STATUS docs for Sprints 20-23 so dashboard shows recent sprint history | Medium | Complete (Sprint 24) |
| F-063 | Better tool error messages — show tool name and reason instead of raw exception when bot tool calls fail | Medium | Complete (Sprint 24) |
| F-064 | Stop generating button — cancel streaming response mid-generation before TTS starts, replaces Send button during streaming | High | Complete (Sprint 25) |
| F-065 | Hands-free pause/resume — transform Send button into Pause/Play toggle when hands-free is active; Pause mutes mic without disabling hands-free, Play resumes listening; includes tooltips | High | Complete (Sprint 25) |
| F-066 | Scroll-to-bottom FAB — floating button appears when scrolled up in long conversations, click to jump to latest message | Medium | Complete (Sprint 26) |
| F-067 | Message character/word count — show approximate token usage before sending long messages | Low | Complete (Sprint 27) |
| F-068 | Keyboard shortcuts help — show available shortcuts (Enter=send, Escape=stop speaking, etc.) in a tooltip or modal | Low | Complete (Sprint 26) |
| F-069 | Voice transcription discard button — show transcription preview with discard/confirm before auto-sending | High | Complete (Sprint 29) |
| F-070 | Conversation summary banner — collapsible summary at top of long conversations showing key topics | Medium | Complete (Sprint 30) |
| F-071 | Unified play/pause toggle for hands-free — single button that stops TTS AND pauses VAD on pause, resumes VAD on play; clear visual state (mic icon vs pause icon) | High | Complete (Sprint 31) |
| F-072 | Hands-free opt-in — require explicit user tap to activate hands-free mode instead of auto-starting on page load | Medium | Complete (Sprint 31) |
| F-073 | Generate PROJECT_STATUS docs for Sprints 30-31 so dashboard shows all recent sprint history | Medium | Complete (Sprint 32) |
| F-074 | Auto-rebuild dashboard data after sprint merge — sprint-run.sh should call /api/rebuild-data so dashboard is always current | High | Complete (Sprint 33) |
| F-075 | Active Project selector in Settings should list all registered Afterburner projects from /api/projects | Medium | Complete (Sprint 34 + hotfix) |
