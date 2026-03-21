# S-2026-03-21-1846-sprint27-deps-docs

## Title
Sprint 27 — Fix dependency groups and generate Sprint 26 PROJECT_STATUS

## Goal
Fix pyproject.toml so `pip install -e ".[dev]"` installs all runtime deps (anthropic, openai, google-auth). Generate Sprint 26 PROJECT_STATUS doc. Update backlog.

## Context
- B-035: dev extras missing LLM provider packages
- B-036: start.sh not installing optional deps
- Sprint 26 had no PROJECT_STATUS doc yet

## Plan
1. Add `providers` group to pyproject.toml, update `dev` and `all` groups
2. Add `pip install -e ".[dev]"` to scripts/start.sh after venv activation
3. Write import tests for anthropic, openai, google-auth
4. Generate PROJECT_STATUS doc for Sprint 26
5. Mark B-035, B-036 as Complete in backlog

## Changes Made
- pyproject.toml: Added `providers` extra group, updated `dev` and `all` groups with anthropic, openai, google-auth
- scripts/start.sh: Added `pip install -q -e ".[dev]"` after venv activation
- tests/test_sprint27_deps.py: 4 import tests verifying provider/auth packages
- docs/PROJECT_STATUS_2026-03-21-sprint26.md: Sprint 26 status doc
- docs/project-memory/backlog/README.md: B-035, B-036 marked Complete (Sprint 27)

## Decisions Made
- Added `pip install -q -e ".[dev]"` as a quiet install step that's a fast no-op when already satisfied, avoiding startup delay on subsequent runs
- Used `google-auth[requests]>=2.20` in dev group (with requests extra) matching the `all` group pattern

## Test Results
693 tests passing (including 4 new dependency import tests)
