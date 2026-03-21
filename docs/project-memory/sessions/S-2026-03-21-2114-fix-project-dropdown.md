# Session

Session-ID: S-2026-03-21-2114-fix-project-dropdown
Title: Fix Active Project dropdown in Settings panel (B-045, F-075)
Date: 2026-03-21
Author: agentA (Sprint 33)

## Goal

Fix the empty/broken Active Project dropdown in the Settings panel so it correctly displays registered Afterburner projects and allows switching between them.

## Context

The Settings panel had an Active Project dropdown (`#settingsProject`) that was already wired to fetch from `/api/projects` and POST to `/api/projects/switch`. However, the backend returns project objects with `{slug, name}` fields while the frontend was treating each project as a plain string, resulting in `[object Object]` values and a broken dropdown.

## Plan

1. Read and understand current frontend dropdown code and backend API response format
2. Fix the JavaScript to destructure project objects correctly
3. Add empty-state handling when no projects are registered
4. Run tests to verify

## Changes Made

- Fixed `openSettings()` project list handler in `bot/chat_ui.html` to use `p.slug` and `p.name` from the API response objects instead of treating projects as plain strings
- Added backwards-compatible handling for both string and object formats
- Added "No projects registered" disabled option when the project list is empty

## Decisions Made

- Used defensive `typeof p === 'string'` check so the dropdown works regardless of whether the API returns strings or objects. This handles version skew gracefully.
- Show a disabled "No projects registered" placeholder when the list is empty, so the dropdown is never confusingly blank.

## Open Questions

None.

## Links

Commits:
- (pending commit)
