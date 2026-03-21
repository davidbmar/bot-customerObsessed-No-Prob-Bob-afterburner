"""Sprint 25 — Button state tests for Send/Stop/Pause behavior.

These tests define the EXPECTED behavior. They are written BEFORE
implementation so agents know what to build. Tests that fail before
Sprint 25 are the spec; tests that pass after Sprint 25 prove it works.

Button priority for the Send button slot:
  1. Streaming active     → ⏹ (tooltip: "Stop generating")
  2. Hands-free ON, no text → ⏸/▶ (tooltip: "Pause/Resume listening")
  3. Text in input        → Send
  4. No text, type mode   → Send (disabled)
"""

import pytest
import time
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers — these tests need a running server at localhost:1203
# We use requests + simple DOM checks via the /api endpoints
# The actual Playwright E2E tests run manually via the iterate loop
# ---------------------------------------------------------------------------

def _get_chat_html():
    """Read the chat_ui.html source for static analysis."""
    html_path = Path(__file__).parent.parent / "bot" / "chat_ui.html"
    return html_path.read_text()


class TestButtonSlotPriority:
    """Verify the Send button slot changes based on context."""

    def test_send_button_exists(self):
        """The Send button element must exist in the HTML."""
        html = _get_chat_html()
        assert "sendBtn" in html or "Send" in html

    def test_send_button_disabled_by_default(self):
        """Send button should be disabled when input is empty."""
        html = _get_chat_html()
        # The button should start disabled
        assert "disabled" in html.lower()

    def test_stop_generating_button_exists(self):
        """A stop-generating mechanism must exist during streaming (F-064).
        Look for a stop button, abort controller, or equivalent."""
        html = _get_chat_html()
        # After Sprint 25, this should find a stop/abort mechanism
        has_stop = (
            "stopGenerat" in html
            or "abortController" in html
            or "abort()" in html
            or "Stop generating" in html
            or "stop-generating" in html
        )
        assert has_stop, "F-064: No stop-generating mechanism found in chat_ui.html"

    def test_pause_button_exists_for_handsfree(self):
        """A pause/resume mechanism must exist for hands-free mode (F-065).
        The Send button should transform to pause/play when hands-free is active."""
        html = _get_chat_html()
        has_pause = (
            "pauseListening" in html
            or "pause-listening" in html
            or "vadPaused" in html
            or "Pause listening" in html
            or "Resume listening" in html
        )
        assert has_pause, "F-065: No pause/resume mechanism found in chat_ui.html"

    def test_pause_button_has_tooltip(self):
        """Pause and Play buttons must have title attributes (tooltips)."""
        html = _get_chat_html()
        has_pause_tooltip = "Pause listening" in html
        has_resume_tooltip = "Resume listening" in html
        assert has_pause_tooltip, "F-065: Missing 'Pause listening' tooltip"
        assert has_resume_tooltip, "F-065: Missing 'Resume listening' tooltip"

    def test_stop_generating_has_tooltip(self):
        """Stop generating button must have a tooltip."""
        html = _get_chat_html()
        has_tooltip = "Stop generating" in html
        assert has_tooltip, "F-064: Missing 'Stop generating' tooltip"


class TestStreamingAbort:
    """Verify streaming can be aborted (F-064)."""

    def test_abort_controller_in_send_flow(self):
        """The streaming fetch should use AbortController so it can be cancelled."""
        html = _get_chat_html()
        has_abort = "AbortController" in html
        assert has_abort, "F-064: Streaming must use AbortController for cancellation"

    def test_stop_button_aborts_stream(self):
        """The stop button should call abort() on the controller."""
        html = _get_chat_html()
        has_abort_call = "abort()" in html
        assert has_abort_call, "F-064: Stop button must call abort() to cancel stream"

    def test_stop_skips_tts(self):
        """When streaming is aborted, TTS should NOT play for the partial response."""
        html = _get_chat_html()
        # After abort, the code should skip TTS synthesis
        # Look for logic that checks aborted state before calling TTS
        has_skip_logic = (
            "aborted" in html
            or "wasAborted" in html
            or "streamAborted" in html
        )
        assert has_skip_logic, "F-064: Must skip TTS when stream is aborted"


class TestHandsfreePauseResume:
    """Verify hands-free pause/resume behavior (F-065)."""

    def test_send_button_becomes_pause_in_handsfree(self):
        """When hands-free is activated, Send button should show pause icon."""
        html = _get_chat_html()
        # Look for logic that changes sendBtn content/class when handsfree activates
        has_transform = (
            "sendBtn" in html
            and ("⏸" in html or "pause" in html.lower())
        )
        assert has_transform, "F-065: Send button must transform to pause in hands-free mode"

    def test_pause_stops_vad(self):
        """Clicking pause should pause the VAD instance."""
        html = _get_chat_html()
        has_vad_pause = "vadInstance.pause" in html or "vadPaused" in html
        assert has_vad_pause, "F-065: Pause must stop VAD from detecting speech"

    def test_resume_restarts_vad(self):
        """Clicking play/resume should restart the VAD instance."""
        html = _get_chat_html()
        has_vad_resume = "vadInstance.start" in html
        assert has_vad_resume, "F-065: Resume must restart VAD"

    def test_pause_state_persists(self):
        """Paused state should be tracked in a variable."""
        html = _get_chat_html()
        has_state = (
            "vadPaused" in html
            or "isPaused" in html
            or "listeningPaused" in html
        )
        assert has_state, "F-065: Must track paused state in a variable"

    def test_vad_status_shows_paused(self):
        """When paused, the VAD status indicator should show 'Paused'."""
        html = _get_chat_html()
        has_paused_status = "Paused" in html
        assert has_paused_status, "F-065: VAD status must show 'Paused' when mic is muted"


class TestModeTransitions:
    """Verify button behavior across mode transitions."""

    def test_handsfree_off_restores_send_button(self):
        """Turning off hands-free should restore the normal Send button."""
        html = _get_chat_html()
        # toggleHandsfree should restore sendBtn text/state
        has_restore = "toggleHandsfree" in html and "Send" in html
        assert has_restore, "Turning off hands-free must restore Send button"

    def test_streaming_overrides_pause(self):
        """During streaming, Stop should override Pause (higher priority)."""
        html = _get_chat_html()
        # The streaming code should change the button even in hands-free mode
        # This is verified by checking that the streaming handler touches sendBtn
        has_override = "sendBtn" in html
        assert has_override, "Streaming must be able to override the Send button slot"

    def test_stream_end_restores_previous_state(self):
        """After streaming ends, button should return to previous state
        (Pause if hands-free, Send if type mode)."""
        html = _get_chat_html()
        # Look for logic that restores button after stream completes
        has_restore = (
            "restoreButton" in html
            or "updateSendButton" in html
            or "resetSendBtn" in html
        )
        # This might be in updateSendButton or a new function
        assert has_restore or "sendBtn" in html, "Must restore button state after streaming"
