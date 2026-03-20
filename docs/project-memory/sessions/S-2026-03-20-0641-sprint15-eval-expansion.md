# Session

Session-ID: S-2026-03-20-0641-sprint15-eval-expansion
Title: Sprint 15 — Expand evaluation scenarios from 3 to 9
Date: 2026-03-20
Author: agentA

## Goal

Add 6 new evaluation scenarios to test diverse customer types (F-035), bringing total from 3 to 9.

## Context

Sprint 14 left the evaluation framework with 3 scenarios (surface-request, vague-requirements, pushback). Sprint 15 brief calls for 8+ scenarios covering technical customers, emotional customers, multi-problem, solution-fixated, returning customers, and enterprise customers.

## Plan

1. Create 6 new YAML scenario files
2. Extend _criterion_matches in runner.py for new patterns (acknowledges, captures, priority, does-not-ignore)
3. Add comprehensive tests: file existence, structure validation, pass/fail with mock LLMs
4. Mark F-035 complete in backlog

## Changes Made

- Created 6 new scenario files in evaluations/scenarios/
  - technical-customer.yaml, emotional-customer.yaml, multi-problem.yaml
  - solution-fixated.yaml, returning-customer.yaml, enterprise-customer.yaml
- Extended _criterion_matches() with patterns: acknowledges, captures, does-not-ignore, priority, solve-all
- Added 92 new tests in test_evaluations.py (353 total passing, up from 261)
- Updated backlog: F-035 marked Complete (Sprint 15)

## Decisions Made

- Criteria phrasing follows the heuristic matcher's keyword patterns — used "asks about", "does NOT", "acknowledges", "captures" which map to specific keyword lists
- Added empathy-detection keywords (understand, frustrating, sorry, etc.) for the emotional-customer scenario
- Each scenario has 2-3 pass criteria and 1-2 fail criteria for balanced evaluation

## Open Questions

None.

## Links

Commits:
- (pending commit)
