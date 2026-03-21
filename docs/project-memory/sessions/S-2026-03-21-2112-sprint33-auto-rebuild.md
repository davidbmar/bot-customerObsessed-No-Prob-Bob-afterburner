# Session

Session-ID: S-2026-03-21-2112-sprint33-auto-rebuild
Title: Sprint 33 — Auto-rebuild dashboard data + Sprint 32 PROJECT_STATUS
Date: 2026-03-21
Author: agentB

## Goal

Add auto-rebuild of dashboard data after sprint merges in sprint-run.sh (F-074) and generate the missing PROJECT_STATUS doc for Sprint 32 (B-047).

## Context

After sprint merges, dashboard data must be manually rebuilt for the bot to return current sprint info. Sprint 32 completed but has no PROJECT_STATUS doc, so the dashboard only shows through Sprint 31.

## Plan

1. Verify sprint-run.sh has auto-rebuild curl call after merge+push
2. Create PROJECT_STATUS_2026-03-21-sprint32.md with Sprint 32 summary
3. Create session doc

## Changes Made

- Verified sprint-run.sh already has auto-rebuild at lines 1005-1020 (curl POST to /api/rebuild-data after push, with graceful failure handling)
- Created `docs/PROJECT_STATUS_2026-03-21-sprint32.md` documenting ONNX warning suppression (B-044), Sprint 30-31 docs generation (B-043, F-073), and zsh crash fix (B-008)

## Decisions Made

- The auto-rebuild curl call was already present in sprint-run.sh from a prior sprint. No modification needed — the acceptance criteria are already met by existing code.
- The "manual merge fallback" path exits with `exit 1` and tells user to re-run with `--continue`, which means the rebuild code runs on the successful re-run. No separate rebuild call needed.

## Open Questions

- B-047 will be resolved by this sprint's PROJECT_STATUS doc being added
- B-046 will be resolved once dashboard data is rebuilt with the new Sprint 32 doc

## Links

Commits:
- (pending)

PRs:
- (pending)
