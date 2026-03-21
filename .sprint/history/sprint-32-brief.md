# Sprint 32

Goal
- Generate PROJECT_STATUS docs for Sprints 30-31 so dashboard shows full history (B-043, F-073)
- Fix sprint-run.sh `local -A` crash on zsh so automated sprints complete end-to-end (B-008)
- Suppress ONNX runtime console warnings from Silero VAD initialization (B-044)

Constraints
- agentA owns `bot/chat_ui.html` exclusively
- agentB owns `.sprint/scripts/sprint-run.sh` and `docs/` files
- No two agents may modify the same files

Merge Order
1. agentB-sprint-docs
2. agentA-onnx-suppress

Merge Verification
- python3 -m pytest tests/ -x -q

## agentA-onnx-suppress

Objective
- Suppress ONNX runtime console warnings that fire on every page load (B-044)

Tasks
- In `bot/chat_ui.html`, wrap the Silero VAD ONNX model initialization to suppress console warnings
- The ONNX runtime emits ~10 `[W:onnxruntime:...]` warnings from `ort.min.js` during model load — these are harmless but noisy
- Options: (a) override `console.warn` temporarily during ONNX init, (b) use ONNX runtime's `logSeverityLevel` config to silence warnings, (c) set `ort.env.logLevel = 'error'` before model load
- Prefer option (c) — `ort.env.logLevel = 'error'` is the cleanest approach
- Verify no other warnings are suppressed (only ONNX init warnings)

Acceptance Criteria
- Page load produces 0 console warnings from ONNX runtime
- VAD still works correctly (speech detection, pause/play)
- No other console output is suppressed

## agentB-sprint-docs

Objective
- Generate PROJECT_STATUS docs for Sprints 30-31 (B-043, F-073)
- Fix sprint-run.sh `local -A` crash on zsh (B-008)

Tasks
- Create `docs/PROJECT_STATUS_2026-03-21-sprint30.md` following PROJECT_STATUS_TEMPLATE format, using Sprint 30 brief from `.sprint/history/` and git log for details
- Create `docs/PROJECT_STATUS_2026-03-21-sprint31.md` following PROJECT_STATUS_TEMPLATE format, using Sprint 31 brief from `.sprint/history/` and git log for details
- In `.sprint/scripts/sprint-run.sh`, replace `local -A` (bash 4+ only) with a zsh-compatible approach — use regular variables or arrays instead of associative arrays
- Test the fix: `zsh -c 'source .sprint/scripts/sprint-run.sh --help'` should not error
- Create a session doc for this sprint

Acceptance Criteria
- `docs/PROJECT_STATUS_2026-03-21-sprint30.md` exists with correct sprint summary
- `docs/PROJECT_STATUS_2026-03-21-sprint31.md` exists with correct sprint summary
- `sprint-run.sh` no longer crashes with `local: -A: invalid option` on zsh
- Dashboard shows Sprints 30 and 31 after rebuild
