"""Sprint 26 — Scroll-to-bottom FAB tests (static HTML analysis).

These tests verify that chat_ui.html contains the scroll-to-bottom
floating action button (F-066) and associated scroll event handling.

agentA owns chat_ui.html and implements the FAB; these tests define
the expected DOM structure so agentA knows what to build.
"""

import re
from pathlib import Path

import pytest


def _get_chat_html():
    """Read the chat_ui.html source for static analysis."""
    html_path = Path(__file__).parent.parent / "bot" / "chat_ui.html"
    return html_path.read_text()


class TestScrollToBottomFAB:
    """Verify scroll-to-bottom button exists in chat_ui.html."""

    def test_scroll_fab_element_exists(self):
        """chat_ui.html must contain a scroll-to-bottom button element."""
        html = _get_chat_html()
        # Look for a button/div with scroll-related id or class
        has_scroll_btn = bool(
            re.search(r'id=["\']scroll-?(to-?)?bottom', html, re.IGNORECASE)
            or re.search(r'class=["\'][^"\']*scroll-?(to-?)?bottom', html, re.IGNORECASE)
            or re.search(r'id=["\']scrollFab', html, re.IGNORECASE)
            or re.search(r'class=["\'][^"\']*scroll-?fab', html, re.IGNORECASE)
        )
        assert has_scroll_btn, (
            "chat_ui.html should contain a scroll-to-bottom button element "
            "(id or class containing 'scroll-bottom', 'scroll-to-bottom', or 'scrollFab')"
        )

    def test_scroll_fab_has_arrow_or_icon(self):
        """The scroll FAB should contain a down-arrow icon or similar indicator."""
        html = _get_chat_html()
        # Common patterns: down arrow unicode, SVG arrow, or arrow-down class
        has_indicator = bool(
            re.search(r'[↓⬇▼⏬🔽]', html)
            or re.search(r'&#x2193;', html)
            or re.search(r'arrow.?down', html, re.IGNORECASE)
            or re.search(r'chevron.?down', html, re.IGNORECASE)
        )
        assert has_indicator, (
            "scroll-to-bottom FAB should contain a down arrow icon "
            "(↓, ▼, SVG arrow-down, or similar)"
        )


class TestScrollEventListener:
    """Verify scroll event handling for the messages container."""

    def test_messages_scroll_listener_exists(self):
        """A scroll event listener must exist for the messages container."""
        html = _get_chat_html()
        # Look for scroll event listener patterns on messages container
        has_scroll_listener = bool(
            re.search(r'addEventListener\s*\(\s*["\']scroll["\']', html)
            or re.search(r'onscroll', html, re.IGNORECASE)
        )
        assert has_scroll_listener, (
            "chat_ui.html should have a scroll event listener "
            "(addEventListener('scroll',...) or onscroll) for showing/hiding the FAB"
        )

    def test_scroll_position_check_logic(self):
        """Scroll handler should check scroll position to toggle FAB visibility."""
        html = _get_chat_html()
        # The scroll handler needs to compare scrollTop + clientHeight vs scrollHeight
        has_scroll_math = bool(
            re.search(r'scrollTop', html)
            and re.search(r'scrollHeight', html)
        )
        assert has_scroll_math, (
            "scroll handler should use scrollTop and scrollHeight "
            "to determine whether user is scrolled away from bottom"
        )

    def test_scrollToBottom_function_exists(self):
        """A scrollToBottom function must exist for the FAB click handler."""
        html = _get_chat_html()
        assert 'function scrollToBottom' in html or 'scrollToBottom' in html, (
            "chat_ui.html should have a scrollToBottom function"
        )
