# Session

Session-ID: S-2026-03-20-0609-sprint13-ui-polish
Title: Sprint 13 UI polish — auto-scroll, seed doc button, mobile responsive
Date: 2026-03-20
Author: agentB

## Goal

Implement UI polish features for web chat: auto-scroll on new messages, "Save as Seed Doc" button, and mobile-responsive CSS.

## Context

Sprint 13 agentB tasks. Chat UI is self-contained in bot/chat_ui.html (vanilla JS, no build step). Auto-scroll partially existed in addMessage but was missing after localStorage restore. No seed doc export from UI. Mobile CSS was minimal.

## Plan

1. Add auto-scroll after restoreConversation and ensure existing scroll points are complete
2. Add "Save as Seed Doc" button bar that appears after 3+ user exchanges
3. Expand mobile responsive CSS: 95% message width, stacked provider cards, larger touch targets, debug panel as full-screen overlay on mobile

## Changes Made

- `bot/chat_ui.html`: Added scrollToBottom after restoreConversation in init()
- `bot/chat_ui.html`: Added seed-doc-bar with button that appears after 3+ exchanges, calls /api/tools/save_discovery
- `bot/chat_ui.html`: Added toast notification system for save feedback
- `bot/chat_ui.html`: Expanded @media (max-width: 768px) with 95% message width, stacked provider cards, larger touch targets (48px min), debug panel as full-screen overlay with close button
- `bot/chat_ui.html`: Refactored toggleDebug to support mobile-open class
- `docs/project-memory/backlog/README.md`: Marked F-027, F-031, F-033 as Complete (Sprint 13)

## Decisions Made

- Used exchange count (user messages >= 3) for seed doc button visibility, matching the brief's "3+ exchanges" requirement
- Debug panel on mobile uses full-screen overlay rather than slide-out to maximize usable space
- Toast notifications auto-dismiss after 3s
- Set 16px font on mobile inputs to prevent iOS zoom behavior

## Open Questions

- The /api/tools/save_discovery endpoint behavior depends on agentA's implementation
- F-034 (auto-synthesis after 5+ exchanges) is in the brief but assigned to server-side logic, not UI

## Links

Commits:
- (pending)
