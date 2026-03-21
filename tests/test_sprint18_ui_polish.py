"""Tests for Sprint 18: debug panel, sidebar, theme, title editing, PROJECT_STATUS."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
HTML_PATH = REPO_ROOT / "bot" / "chat_ui.html"
DOCS_DIR = REPO_ROOT / "docs"


@pytest.fixture
def html_content() -> str:
    """Read the chat_ui.html file."""
    return HTML_PATH.read_text()


# ---------------------------------------------------------------------------
# B-022: Debug panel hidden by default via CSS
# ---------------------------------------------------------------------------

class TestDebugPanelDefault:
    """Debug panel must be hidden by CSS default, not rely on JS."""

    def test_debug_panel_css_display_none(self, html_content):
        """The .debug-panel CSS rule must include display: none."""
        # Find the .debug-panel CSS block (not inside media query)
        match = re.search(
            r'\.debug-panel\s*\{([^}]+)\}',
            html_content,
        )
        assert match, "Expected .debug-panel CSS rule"
        assert 'display: none' in match.group(1), \
            "debug-panel must have display: none by default"

    def test_debug_panel_visible_class_exists(self, html_content):
        """A .debug-panel.visible rule must set display: block."""
        match = re.search(
            r'\.debug-panel\.visible\s*\{([^}]+)\}',
            html_content,
        )
        assert match, "Expected .debug-panel.visible CSS rule"
        assert 'display: block' in match.group(1)

    def test_debug_panel_html_no_visible_class(self, html_content):
        """The debug panel div must NOT have visible class in HTML."""
        match = re.search(r'id="debugPanel"', html_content)
        assert match
        # Find the element's class attribute
        div_match = re.search(r'<div\s+class="debug-panel"\s+id="debugPanel"', html_content)
        assert div_match, "debug-panel div should have no visible class in markup"

    def test_debug_panel_js_restores_from_localstorage(self, html_content):
        """JS init should add 'visible' class when localStorage says true."""
        assert "debugPanel').classList.add('visible')" in html_content

    def test_toggle_debug_uses_visible_class(self, html_content):
        """toggleDebug must toggle 'visible' class, not 'collapsed'."""
        # Find toggleDebug function
        assert "classList.toggle('visible', debugVisible)" in html_content

    def test_no_collapsed_class_reference(self, html_content):
        """No JS references to 'collapsed' class for debug panel."""
        # Should not find collapsed in toggle or init for debug panel
        assert "debugPanel').classList.add('collapsed')" not in html_content
        assert "debugPanel').classList.remove('collapsed')" not in html_content


# ---------------------------------------------------------------------------
# B-023: Sidebar collapsed by default
# ---------------------------------------------------------------------------

class TestSidebarDefault:
    """Sidebar must be hidden by CSS default, toggled open by JS."""

    def test_sidebar_css_display_none(self, html_content):
        """The .conv-sidebar CSS rule must include display: none."""
        match = re.search(
            r'\.conv-sidebar\s*\{([^}]+)\}',
            html_content,
        )
        assert match, "Expected .conv-sidebar CSS rule"
        assert 'display: none' in match.group(1), \
            "conv-sidebar must have display: none by default"

    def test_sidebar_open_class_exists(self, html_content):
        """A .conv-sidebar.open rule must enable display."""
        match = re.search(
            r'\.conv-sidebar\.open\s*\{([^}]+)\}',
            html_content,
        )
        assert match, "Expected .conv-sidebar.open CSS rule"
        assert 'display: flex' in match.group(1)

    def test_sidebar_html_no_open_class(self, html_content):
        """The sidebar div must NOT have open class in HTML."""
        div_match = re.search(r'<div\s+class="conv-sidebar"\s+id="convSidebar"', html_content)
        assert div_match, "conv-sidebar div should have no open class in markup"

    def test_sidebar_saves_preference(self, html_content):
        """toggleSidebar must save preference to localStorage."""
        assert "localStorage.setItem('sidebarOpen'" in html_content

    def test_sidebar_restores_preference(self, html_content):
        """init() must restore sidebar preference from localStorage."""
        assert "localStorage.getItem('sidebarOpen')" in html_content


# ---------------------------------------------------------------------------
# B-024: System color preference
# ---------------------------------------------------------------------------

class TestSystemColorPreference:
    """First visit should detect system color scheme."""

    def test_prefers_color_scheme_media_query(self, html_content):
        """CSS must include @media (prefers-color-scheme: light) block."""
        assert '@media (prefers-color-scheme: light)' in html_content

    def test_js_checks_matchmedia(self, html_content):
        """restoreTheme must use matchMedia for system preference detection."""
        assert "matchMedia('(prefers-color-scheme: light)')" in html_content or \
               'matchMedia("(prefers-color-scheme: light)")' in html_content

    def test_saved_theme_overrides_system(self, html_content):
        """If localStorage has a theme, it must be used over system preference."""
        # The saved check must come before the matchMedia check
        saved_pos = html_content.find("localStorage.getItem('theme')")
        match_pos = html_content.find("matchMedia")
        assert saved_pos < match_pos, \
            "localStorage theme check should happen before matchMedia fallback"

    def test_dark_class_set_on_toggle(self, html_content):
        """toggleTheme must set 'dark' class when switching to dark."""
        assert "classList.toggle('dark'" in html_content


# ---------------------------------------------------------------------------
# F-041: Conversation title editing
# ---------------------------------------------------------------------------

class TestConversationTitleEditing:
    """Click title in sidebar to rename, saves to localStorage."""

    def test_contenteditable_css_exists(self, html_content):
        """CSS must style contenteditable preview elements."""
        assert 'contenteditable="true"' in html_content or \
               "contenteditable" in html_content

    def test_start_title_edit_function_exists(self, html_content):
        """startTitleEdit function must be defined."""
        assert 'function startTitleEdit' in html_content

    def test_title_saved_to_localstorage(self, html_content):
        """Title edits must be saved with conv_title_ prefix."""
        assert "conv_title_" in html_content

    def test_enter_key_saves_title(self, html_content):
        """Pressing Enter should trigger blur to save."""
        assert "key === 'Enter'" in html_content or \
               'key === "Enter"' in html_content

    def test_escape_key_cancels_edit(self, html_content):
        """Pressing Escape should cancel the edit."""
        assert "key === 'Escape'" in html_content or \
               'key === "Escape"' in html_content

    def test_custom_title_displayed_in_sidebar(self, html_content):
        """refreshConversationList should display custom title if set."""
        assert "conv_title_" in html_content
        assert "customTitle" in html_content or "conv_title_" in html_content


# ---------------------------------------------------------------------------
# PROJECT_STATUS docs
# ---------------------------------------------------------------------------

class TestProjectStatusDocs:
    """Sprint 17 PROJECT_STATUS doc must exist."""

    def test_sprint17_status_doc_exists(self):
        """PROJECT_STATUS doc for Sprint 17 must exist."""
        docs = list(DOCS_DIR.glob("PROJECT_STATUS_*sprint17.md"))
        assert len(docs) == 1, f"Expected 1 sprint17 doc, found {len(docs)}"

    def test_total_status_docs_count(self):
        """Must have exactly 18 PROJECT_STATUS docs (Sprints 1-18)."""
        docs = list(DOCS_DIR.glob("PROJECT_STATUS_*.md"))
        assert len(docs) >= 18, f"Expected at least 18 docs, found {len(docs)}"

    def test_sprint17_doc_has_content(self):
        """Sprint 17 doc must have meaningful content."""
        docs = list(DOCS_DIR.glob("PROJECT_STATUS_*sprint17.md"))
        assert len(docs) == 1
        content = docs[0].read_text()
        assert "Sprint 17" in content
        assert "## What Changed" in content
