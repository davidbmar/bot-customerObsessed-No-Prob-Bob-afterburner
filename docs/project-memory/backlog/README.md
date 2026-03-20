# Backlog

Track bugs and feature requests here.

## Bugs

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| B-001 | gateway.py imports OllamaLLM but llm.py exports OllamaClient — name mismatch | Critical | Fixed (Sprint 2) |
| B-002 | BotConfig has no model_name attribute — field naming inconsistency between config and gateway | Critical | Open |
| B-003 | server.py fails to import due to cascading gateway import error (B-001) | Critical | Open |
| B-004 | pytest not installed in venv — tests can't run | High | Open |
| B-005 | .venv had stale path from project rename (afterburner-customer-bot → bot-customerObsessed...) | Medium | Fixed |

## Features

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| F-001 | Telegram polling transport — run alongside web server | High | Complete (Sprint 2) |
| F-002 | save_discovery tool — write conversation synthesis as seed doc to Afterburner project | High | Complete (Sprint 2) |
| F-003 | get_project_summary tool — read project status from Afterburner | Medium | Planned |
| F-004 | End-to-end test: conversation → seed doc written to project | High | Planned |
| F-005 | Evaluation framework with YAML scenario tests | Medium | Planned |
| F-006 | Fact extraction from conversations (LLM-generated summaries) | Medium | Planned |
| F-007 | Web chat settings panel — switch personality, switch model, view memory | Low | Planned |
| F-008 | CLI `chat` command — interactive terminal chat loop | Medium | Planned |
| F-009 | CLI `status` command — show server status, personality, conversation count | Low | Planned |
