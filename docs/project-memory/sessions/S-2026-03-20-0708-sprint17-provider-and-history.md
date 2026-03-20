# Session

Session-ID: S-2026-03-20-0708-sprint17-provider-and-history
Title: Sprint 17 - Provider label fix and PROJECT_STATUS history
Date: 2026-03-20
Author: agentA

## Goal

Generate PROJECT_STATUS docs for Sprints 12-16 (B-021) and fix provider label in health endpoint (B-019).

## Context

Dashboard only shows Sprints 1-11. Health endpoint returns "ollama" instead of "Qwen 3.5" as provider label.

## Plan

1. Extend generate_sprint_history.py to handle sprints 12-16
2. Fix default _provider_id in Gateway to "qwen-3.5"
3. Add active_label to /api/llm/providers response
4. Write tests, update backlog

## Changes Made

- Extended `scripts/generate_sprint_history.py` to accept CLI args and auto-discover sprint range
- Generated 5 new PROJECT_STATUS docs (sprints 12-16), total now 16
- Fixed `Gateway.__init__` to default `_provider_id` to `"qwen-3.5"` instead of `None`
- Fixed `health_check()` fallback from `"ollama"` to `"qwen-3.5"`
- Added `active_label` field to `/api/llm/providers` response
- Updated existing test that asserted buggy behavior
- Added 46 new tests (445 total, up from 399)
- Updated backlog: B-019 and B-021 marked Complete (Sprint 17)

## Decisions Made

- Defaulting `_provider_id` to `"qwen-3.5"` rather than trying to infer from model name — simpler and correct for the default Ollama+Qwen setup.
- Made generate_sprint_history.py accept optional start/end CLI args for flexibility.

## Open Questions

- None

## Links

Commits:
- See git log for this session
