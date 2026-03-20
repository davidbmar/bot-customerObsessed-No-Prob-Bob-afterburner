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

## Features

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| F-001 | Telegram polling transport | High | Complete (Sprint 2) |
| F-002 | save_discovery tool | High | Complete (Sprint 3) |
| F-003 | get_project_summary tool | Medium | Complete (Sprint 6) |
| F-004 | End-to-end test: conversation → seed doc | High | Complete (Sprint 3) |
| F-005 | Evaluation framework with YAML scenario tests | Medium | Complete (Sprint 6) |
| F-006 | Fact extraction from conversations | Medium | Complete (Sprint 6) |
| F-007 | Web chat settings panel | Low | Planned |
| F-008 | CLI chat command | Medium | Complete (Sprint 3) |
| F-009 | CLI status command | Low | Complete (Sprint 3) |
| F-010 | Web chat debug panel — tools called, principles, tokens, latency | High | Planned |
| F-011 | get_sprint_status tool — check sprint progress from bot | Medium | Planned |
| F-012 | add_to_backlog tool — bot can add bugs/features to project backlog | Medium | Complete (Sprint 6) |
