# Sprint 31

Goal
- Fix the broken pause/play hands-free behavior so Pause stops BOTH speaking AND listening (B-039, B-040, F-071)
- Fix dashboard backlog showing 0 items by correcting the backlog file path in build-sprint-data.sh (B-015)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `scripts/build-sprint-data.sh` in the afterburner repo AND `bot/tools.py` in this repo
- No two agents may modify the same files

Merge Order
1. agentB-backlog-tools (independent changes — framework script + bot tools)
2. agentA-pause-play (UI changes to chat_ui.html)

Merge Verification
- python3 -m pytest tests/ -x -q

## agentA-pause-play

Objective
- Fix Pause/Play toggle so it stops BOTH TTS and VAD listening (B-039, B-040, F-071)
- Prevent hands-free from auto-starting on page load (B-041)

Tasks
- In `bot/chat_ui.html`, make the Pause button (⏸) call BOTH `stopAgentSpeaking()` AND set `vadPaused = true` so VAD stops capturing audio
- Make the Play button (▶) set `vadPaused = false` to resume VAD listening
- In the TTS `ended` event handler, do NOT reset `vadPaused` — respect user's explicit pause state
- On page load, set `vadPaused = true` by default — user must click Play or the Hands-free toggle to start listening
- The "Stop speaking" banner button (`#stopSpeakingBtn`) should also pause VAD (set `vadPaused = true`)
- Add visual indicator: when paused, show "Paused" text next to the button instead of "Listening..."

Acceptance Criteria
- Clicking Pause stops TTS playback AND stops mic listening — no phantom messages
- Clicking Play resumes listening — VAD starts detecting speech again
- "Stop speaking" also pauses the mic
- Fresh page load does NOT auto-listen — user must explicitly activate hands-free
- Existing keyboard shortcut (Escape to stop speaking) also pauses VAD

## agentB-backlog-tools

Objective
- Fix B-015: dashboard backlog shows 0 because build-sprint-data.sh looks for wrong file path
- Fix B-042: bot tools show raw errors when dashboard API is unreachable

Tasks
- In `scripts/build-sprint-data.sh` (AFTERBURNER REPO at ~/src/traceable-searchable-adr-memory-index), change `BACKLOG_FILE` from `${PROJECT_ROOT}/docs/project-memory/backlog.md` to also check `${PROJECT_ROOT}/docs/project-memory/backlog/README.md` (the actual location)
- In `bot/tools.py` (THIS REPO), wrap the `httpx.get` calls in `tool_get_sprint_status` and `tool_feedback_on_sprint` with proper error handling so connection errors return a friendly message like "Dashboard unavailable, using local data" instead of raising exceptions
- Run `bash ~/src/traceable-searchable-adr-memory-index/scripts/build-sprint-data.sh` against this project after fixing the path to verify backlog.json gets populated

Acceptance Criteria
- `dist/projects/bot-customerobsessed/data/backlog.json` contains actual bugs and features after rebuild
- Dashboard Backlog page shows correct counts (not 0)
- `tool_get_sprint_status("nonexistent")` returns a friendly error, not a stack trace
- All existing tests pass: `python3 -m pytest tests/ -x -q`
