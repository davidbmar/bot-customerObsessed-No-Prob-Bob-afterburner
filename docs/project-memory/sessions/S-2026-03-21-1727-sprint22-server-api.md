# Session

Session-ID: S-2026-03-21-1727-sprint22-server-api
Title: Sprint 22 - Fix /api/projects endpoint and add API tests
Date: 2026-03-21
Author: agentB

## Goal

Fix the Active Project dropdown (B-028) by wiring config into the Gateway and returning projects in the expected format. Write integration tests for /api/projects, /api/health, and POST /api/conversations/new.

## Context

The /api/projects endpoint existed but always returned empty because BotConfig was never passed to the Gateway in main(). The response format also needed updating from flat slug strings to {slug, name} objects.

## Plan

1. Pass config to Gateway in main()
2. Update _handle_get_projects to return [{slug, name}] format
3. Write HTTP-level integration tests for projects, health, conversations/new
4. Update backlog: B-028, F-058 marked Complete

## Changes Made

- bot/server.py: Pass `config=cfg` to Gateway in main(); update _handle_get_projects to return objects with slug and name fields
- tests/test_sprint22_api.py: New test file with 7 tests covering /api/projects, /api/health, POST /api/conversations/new
- docs/project-memory/backlog/README.md: B-028 and F-058 marked Complete (Sprint 22)

## Decisions Made

- Project name derived from slug via replace("-", " ").title() since registry doesn't store display names
- Tests use live HTTP server on port 0 (random) to test real request/response cycle

## Open Questions

- None

## Links

Commits:
- (pending) fix: wire config into Gateway and return projects as objects
