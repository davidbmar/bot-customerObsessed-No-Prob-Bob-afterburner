# Sprint 25

Goal
- Add Stop Generating button to cancel streaming responses mid-generation (F-064)
- Add Pause/Resume toggle for hands-free mode — Send button becomes ⏸/▶ (F-065)
- All 17 tests in tests/test_sprint25_button_states.py must pass

Constraints
- Use the project venv: .venv/bin/python3
- All tests must pass: .venv/bin/python3 -m pytest tests/ -v
- Agents run non-interactively — MUST NOT ask for confirmation
- agentA owns bot/chat_ui.html ONLY — agentB MUST NOT touch chat_ui.html
- agentB owns tests/ — agentB MUST NOT touch bot/chat_ui.html
- The test file tests/test_sprint25_button_states.py already exists and defines the spec — do NOT modify it

Merge Order
1. agentA-button-states
2. agentB-button-tests

Merge Verification
```bash
cd /Users/davidmar/src/bot-customerObsessed-No-Prob-Bob-afterburner
.venv/bin/python3 -m pytest tests/test_sprint25_button_states.py -v 2>&1 | tail -20
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -5
```

Previous Sprint
- Sprint 24: VAD/barge-in settings panel, PROJECT_STATUS docs for Sprints 20-23, tool error handling
- 659 tests pass (+ 17 new Sprint 25 spec tests, 9 currently failing)
- Users need: stop generating during streaming, pause/resume in hands-free mode
- Test spec already written: tests/test_sprint25_button_states.py (9 failing = the spec)

## agentA-button-states

Objective
- Implement F-064 (Stop Generating) and F-065 (Pause/Resume) in bot/chat_ui.html
- All 9 currently-failing tests in test_sprint25_button_states.py must pass after your changes

Tasks

### F-064: Stop Generating Button

The Send button should become a Stop button (⏹) during streaming responses.

1. **Add AbortController to streaming fetch**:
   - In the `sendMessage()` function, create an `AbortController` before the `fetch()` call
   - Store it: `var currentAbortController = null;`
   - Pass `signal: currentAbortController.signal` to the fetch options
   - On stream completion or error, set `currentAbortController = null`

2. **Transform Send button during streaming**:
   - When streaming starts: change `sendBtn.textContent = '⏹'`, add `title="Stop generating"`, enable the button, add class `stop-generating`
   - When streaming ends: restore the button to its previous state (Send, or ⏸ if hands-free)
   - Track streaming state: `var isStreaming = false;`

3. **Stop button handler**:
   - When clicked during streaming: call `currentAbortController.abort()`, set `isStreaming = false`
   - Set a flag `var streamAborted = false;` — set to true when abort is called
   - In the SSE `done` event handler: check `streamAborted` and skip TTS synthesis if true
   - Restore the button state after abort

4. **CSS**: Add `.stop-generating` class with red/orange accent color

### F-065: Hands-free Pause/Resume

The Send button should become a Pause/Play toggle when hands-free is active.

1. **Track paused state**:
   - Add variable: `var vadPaused = false;`
   - This is separate from `handsfreeActive` — you can be in hands-free but paused

2. **Transform Send button in hands-free mode**:
   - In `toggleHandsfree()`, when activating hands-free:
     - Change `sendBtn.textContent = '⏸'`
     - Set `sendBtn.title = 'Pause listening'`
     - Enable the button (remove disabled)
     - Set `sendBtn.onclick = toggleVadPause`
   - When deactivating hands-free:
     - Restore `sendBtn.textContent = 'Send'`
     - Remove title
     - Set `sendBtn.onclick = sendMessage` (or restore original handler)
     - Set `sendBtn.disabled = !input.value.trim()`
     - Reset `vadPaused = false`

3. **toggleVadPause() function**:
   ```javascript
   function toggleVadPause() {
     if (isStreaming) return; // Stop button takes priority
     vadPaused = !vadPaused;
     if (vadPaused) {
       vadInstance.pause();
       sendBtn.textContent = '▶';
       sendBtn.title = 'Resume listening';
       setVadState('paused');
     } else {
       vadInstance.start();
       sendBtn.textContent = '⏸';
       sendBtn.title = 'Pause listening';
       setVadState('listening');
     }
   }
   ```

4. **Add 'paused' to setVadState()**:
   - In the `setVadState()` function, add a case for `'paused'`:
     - Set status text to "Paused"
     - Set status dot to gray or yellow
     - Hide waveform

5. **Button priority logic** — add/update `updateSendButton()`:
   ```javascript
   function updateSendButton() {
     if (isStreaming) {
       sendBtn.textContent = '⏹';
       sendBtn.title = 'Stop generating';
       sendBtn.disabled = false;
       sendBtn.onclick = stopGenerating;
     } else if (handsfreeActive && !input.value.trim()) {
       sendBtn.textContent = vadPaused ? '▶' : '⏸';
       sendBtn.title = vadPaused ? 'Resume listening' : 'Pause listening';
       sendBtn.disabled = false;
       sendBtn.onclick = toggleVadPause;
     } else {
       sendBtn.textContent = 'Send';
       sendBtn.title = '';
       sendBtn.disabled = !input.value.trim();
       sendBtn.onclick = sendMessage;
     }
   }
   ```

6. **Call updateSendButton()** from:
   - `toggleHandsfree()` — when mode changes
   - `sendMessage()` — when streaming starts/ends
   - `stopGenerating()` — after abort
   - Input event handler — when text changes (existing `updateSendButton` or equivalent)

7. **Update backlog** — Mark F-064, F-065 as Complete (Sprint 25)

Acceptance Criteria
- `tests/test_sprint25_button_states.py` — all 17 tests pass (9 currently failing)
- During streaming: Send → ⏹ with "Stop generating" tooltip
- Click ⏹ during streaming: stream aborts, partial text kept, no TTS
- Hands-free ON: Send → ⏸ with "Pause listening" tooltip
- Click ⏸: VAD pauses, status shows "Paused", button → ▶ "Resume listening"
- Click ▶: VAD resumes, status shows "Listening...", button → ⏸
- Type text in hands-free: Send appears (overrides ⏸)
- After stream ends: button returns to ⏸ (hands-free) or Send (type mode)

## agentB-button-tests

Objective
- Add additional integration tests to verify button behavior end-to-end
- Do NOT modify tests/test_sprint25_button_states.py — that is the spec
- Do NOT modify bot/chat_ui.html — that is agentA's territory

Tasks
1. **Add server-side streaming abort test**:
   - Test that the `/api/chat/stream` SSE endpoint handles client disconnection gracefully
   - Test that aborting mid-stream doesn't crash the server or leave zombie processes

2. **Add API test for concurrent requests**:
   - Test that sending a new message while streaming aborts the previous stream
   - Or test that the server handles overlapping requests cleanly

3. **Update backlog** — Verify F-064, F-065 marked Complete

Acceptance Criteria
- All existing + new tests pass
- `.venv/bin/python3 -m pytest tests/ -v` — all pass
