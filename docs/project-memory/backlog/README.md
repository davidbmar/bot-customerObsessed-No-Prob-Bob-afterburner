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
| B-008 | sprint-run.sh crashes with `local -A` on zsh — agents run but merge/polling dies | High | Open |
| B-009 | Dashboard shows 0 for sprints/sessions/ADRs — no PROJECT_STATUS docs built | Medium | Fixed (Sprint 12) |
| B-010 | GitHub not configured in dashboard project entry | Low | Open |
| B-011 | CLI status crashes — _auto_discover_projects expects dict but gets strings from projects.json | High | Fixed (Sprint 9) |
| B-012 | Tool naming inconsistency — feedback_on_sprint vs get_sprint_feedback pattern | Medium | Fixed (Sprint 9) |
| B-013 | Debug panel visible by default on page load — F-019 (Sprint 10) may not have fully landed | Low | Complete (Sprint 16) |
| B-014 | No PROJECT_STATUS docs exist — sprint-merge.sh never ran (all 11 sprints merged manually or via sprint-run.sh that crashed) | High | Complete (Sprint 12) |
| B-015 | Dashboard backlog counts show 0 — build-sprint-data.sh doesn't parse backlog/README.md into backlog.json | Medium | Open |
| B-016 | Ollama Qwen 3.5 response latency ~22s for simple messages — acceptable but noticeable | Low | Open |
| B-017 | `python3 bot/server.py` fails with relative import error — must use `python3 -m bot.server` (F-022 regression) | Medium | Complete (Sprint 13) |
| B-018 | Token count inflated — shows 1378 out tokens for a 20-word response, likely counting thinking tokens or misreporting | Low | Complete (Sprint 14) |
| B-019 | Header shows `ollama · qwen3:4b` instead of `qwen-3.5 · qwen3.5:latest` — health endpoint returns provider_label: "ollama" not "Qwen 3.5" | Low | Complete (Sprint 17) |
| B-020 | Sprint 12 agent done markers not written — sprint-launch.sh done detection broken (related to B-008) | Medium | Open |
| B-021 | Dashboard only shows Sprints 1-11 — Sprints 12-16 need PROJECT_STATUS docs generated | Medium | Complete (Sprint 17) |
| B-022 | Debug panel still visible on fresh load despite B-013 fix — localStorage may be overriding default hidden state | Low | Complete (Sprint 18) |
| B-023 | Sidebar visible by default on desktop — should be collapsed on first visit, user opens when needed | Low | Complete (Sprint 18) |
| B-024 | Light theme is now the default after clearing localStorage — should detect system preference with prefers-color-scheme | Low | Complete (Sprint 18) |

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
