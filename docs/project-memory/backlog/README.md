# Backlog

Track bugs and feature requests here.

## Bugs

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| B-001 | gateway.py imports OllamaLLM but llm.py exports OllamaClient — name mismatch | Critical | Fixed (Sprint 2) |
| B-002 | BotConfig missing model_name — field naming inconsistency | Critical | Fixed (Sprint 2) |
| B-003 | server.py cascading import failure | Critical | Fixed (Sprint 2) |
| B-004 | pytest not installed in venv | High | Fixed (Sprint 2) |
| B-005 | .venv stale path from project rename | Medium | Fixed |
| B-006 | save_discovery function not exported from bot/tools.py — merge conflict dropped it | High | Fixed (Sprint 3) |
| B-007 | test_api_chat_uses_chat_id fails — server uses conversation_id not chat_id | Medium | Fixed (Sprint 3) |
| B-008 | sprint-run.sh crashes with `local -A` error on zsh — agents run but merge/polling dies | High | Open |

## Features

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| F-001 | Telegram polling transport | High | Complete (Sprint 2) |
| F-002 | save_discovery tool — write seed docs | High | Complete (Sprint 3) |
| F-003 | get_project_summary tool | Medium | Planned |
| F-004 | End-to-end test: conversation → seed doc | High | Planned |
| F-005 | Evaluation framework with YAML scenario tests | Medium | Planned |
| F-006 | Fact extraction from conversations | Medium | Planned |
| F-007 | Web chat settings panel | Low | Planned |
| F-008 | CLI chat command — interactive terminal loop | Medium | Planned |
| F-009 | CLI status command | Low | Planned |
| F-010 | Web chat debug panel — show tools called, principles, token count, latency | High | Planned |
