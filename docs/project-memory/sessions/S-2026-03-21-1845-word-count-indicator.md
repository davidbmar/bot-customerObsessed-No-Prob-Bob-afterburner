# Session

Session-ID: S-2026-03-21-1845-word-count-indicator
Title: Add word/token count indicator to chat input
Date: 2026-03-21
Author: agentA (Claude)

## Goal

Add a subtle word count and approximate token count indicator below the chat input (F-067).

## Context

Sprint 27 brief requests a real-time word/token count near the text input. Users want to gauge message length before sending, especially for paid LLM providers with token limits.

## Plan

1. Add CSS for `.word-count-indicator` element
2. Add HTML element after the input area
3. Hook into existing `onInputChange` to update count on every keystroke
4. Update backlog to mark F-067 complete

## Changes Made

- `bot/chat_ui.html`: Added `.word-count-indicator` CSS class (11px, muted, right-aligned)
- `bot/chat_ui.html`: Added `<div id="wordCountIndicator">` after input area
- `bot/chat_ui.html`: Added `updateWordCount()` function in the textarea auto-resize IIFE
- `docs/project-memory/backlog/README.md`: Marked F-067 as Complete (Sprint 27)

## Decisions Made

- Token estimation uses `words * 1.3` as specified in brief (rough heuristic)
- Word count hidden when input is empty (shows only when text present)
- Placed indicator outside `.input-area` flex container to avoid layout disruption
- Singular/plural "word"/"words" for polish

## Open Questions

None.

## Links

Commits:
- (pending) feat: add word/token count indicator below chat input (F-067)
