# Session

Session-ID: S-2026-03-21-2050-sprint31-backlog-tools
Title: Fix dashboard backlog parsing and bot tool error handling
Date: 2026-03-21
Author: agentB

## Goal

Fix B-015 (dashboard backlog shows 0 items) and B-042 (bot tools show raw errors when dashboard API unreachable).

## Context

build-sprint-data.sh looks for `backlog.md` but actual file is `backlog/README.md`. Also uses `#### BL-NNN` heading format but actual backlog uses `| B-NNN |` table rows. Bot tools silently swallow httpx connection errors and fall through to filesystem with no user-facing message.

## Plan

1. Update BACKLOG_FILE path in build-sprint-data.sh to check both locations
2. Add table-format parser alongside legacy heading parser
3. Add friendly error messages to tool_get_sprint_status and tool_feedback_on_sprint
4. Run build script to verify backlog.json population
5. Run tests to ensure nothing breaks

## Changes Made

- `scripts/build-sprint-data.sh` (afterburner repo): Updated BACKLOG_FILE to check `backlog/README.md` first, then `backlog.md`. Added table-format parser for `| B-NNN |` and `| F-NNN |` rows alongside legacy `#### BL-NNN` format.
- `bot/tools.py` (this repo): Added logging and friendly error messages to `tool_get_sprint_status` and `tool_feedback_on_sprint` when dashboard API is unreachable. Connection errors now produce "Dashboard unavailable, using local data" messages instead of silent pass-through or raw exceptions.

## Decisions Made

- Kept backward compatibility with legacy `#### BL-NNN` format in build script — auto-detects format based on content.
- Added `_note` field to filesystem-fallback JSON responses so callers know data came from local files.

## Open Questions

- None

## Links

Commits:
- (pending)
