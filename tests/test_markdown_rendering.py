"""Tests for enhanced markdown rendering ported from claude-chat-workspace.

Structural tests verify chat_ui.html contains the expected rendering functions
and CSS rules for: tables, blockquotes, horizontal rules, nested lists,
bold+italic combo, language badges, and copy button.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
HTML_PATH = REPO_ROOT / "bot" / "chat_ui.html"


@pytest.fixture
def html_content() -> str:
    """Read the chat_ui.html file."""
    return HTML_PATH.read_text()


# ---------------------------------------------------------------------------
# Core renderer function structure
# ---------------------------------------------------------------------------

class TestRendererFunctions:
    """Verify the renderer functions exist and have correct structure."""

    def test_render_markdown_to_dom_exists(self, html_content):
        assert "function renderMarkdownToDOM(text, container)" in html_content

    def test_process_text_lines_exists(self, html_content):
        assert "function _processTextLines(parent, text)" in html_content

    def test_parse_table_cells_exists(self, html_content):
        assert "function _parseTableCells(row)" in html_content

    def test_append_inline_segments_single_line_exists(self, html_content):
        assert "function _appendInlineSegmentsSingleLine(parent, text)" in html_content

    def test_append_formatted_line_exists(self, html_content):
        assert "function _appendFormattedLine(parent, text)" in html_content

    def test_renderer_clears_children_first(self, html_content):
        """The renderer should clear existing children for safe streaming re-renders."""
        assert "while (container.firstChild) container.removeChild(container.firstChild)" in html_content


# ---------------------------------------------------------------------------
# GFM Table support
# ---------------------------------------------------------------------------

class TestTableRendering:
    """Verify GFM pipe table rendering is implemented."""

    def test_table_detection_regex(self, html_content):
        """Table detection should look for pipe-delimited rows."""
        assert r"/^\|.+\|$/.test(line)" in html_content

    def test_table_separator_detection(self, html_content):
        """Table separator row detection (|---|---|)."""
        assert r"/^\|[-| :]+\|$/.test(lines[i + 1])" in html_content

    def test_table_creates_thead(self, html_content):
        assert "createElement('thead')" in html_content

    def test_table_creates_tbody(self, html_content):
        assert "createElement('tbody')" in html_content

    def test_table_creates_th(self, html_content):
        assert "createElement('th')" in html_content

    def test_table_creates_td(self, html_content):
        assert "createElement('td')" in html_content

    def test_table_css_border_collapse(self, html_content):
        match = re.search(r'\.message\s+\.body\s+table\s*\{([^}]+)\}', html_content)
        assert match, "Expected .message .body table CSS rule"
        assert "border-collapse: collapse" in match.group(1)

    def test_table_header_css(self, html_content):
        assert re.search(r'\.message\s+\.body\s+th', html_content), \
            "Expected CSS rule for table headers"


# ---------------------------------------------------------------------------
# Blockquote support
# ---------------------------------------------------------------------------

class TestBlockquoteRendering:
    """Verify blockquote rendering is implemented."""

    def test_blockquote_detection(self, html_content):
        assert "line.startsWith('> ')" in html_content

    def test_blockquote_element_creation(self, html_content):
        assert "createElement('blockquote')" in html_content

    def test_blockquote_css(self, html_content):
        match = re.search(r'\.message\s+\.body\s+blockquote\s*\{([^}]+)\}', html_content)
        assert match, "Expected blockquote CSS rule"
        assert "border-left" in match.group(1)
        assert "font-style: italic" in match.group(1)


# ---------------------------------------------------------------------------
# Horizontal rule support
# ---------------------------------------------------------------------------

class TestHorizontalRuleRendering:
    """Verify horizontal rule rendering is implemented."""

    def test_hr_detection_triple_dash(self, html_content):
        assert "trimmed === '---'" in html_content

    def test_hr_detection_triple_star(self, html_content):
        assert "trimmed === '***'" in html_content

    def test_hr_element_creation(self, html_content):
        assert "createElement('hr')" in html_content

    def test_hr_css(self, html_content):
        match = re.search(r'\.message\s+\.body\s+hr\s*\{([^}]+)\}', html_content)
        assert match, "Expected hr CSS rule"
        assert "border-top" in match.group(1)


# ---------------------------------------------------------------------------
# Nested list support
# ---------------------------------------------------------------------------

class TestNestedListRendering:
    """Verify nested list support (indented items)."""

    def test_indented_list_detection(self, html_content):
        """Detect 2-space indented list items."""
        assert r"/^  - /.test(line)" in html_content

    def test_nested_ul_creation(self, html_content):
        """Nested list creates a new UL inside parent LI."""
        assert "currentNestedList = document.createElement('ul')" in html_content

    def test_nested_list_attached_to_last_li(self, html_content):
        assert "lastLi.appendChild(currentNestedList)" in html_content


# ---------------------------------------------------------------------------
# Bold + Italic combo
# ---------------------------------------------------------------------------

class TestBoldItalicCombo:
    """Verify ***bold+italic*** rendering."""

    def test_bold_italic_regex(self, html_content):
        """The regex should match ***text*** before ** and *."""
        assert r"\*{3}[^*]+\*{3}" in html_content

    def test_bold_italic_creates_strong_em(self, html_content):
        """***text*** should create <strong><em>text</em></strong>."""
        # Check that strong wraps em for the triple-star case
        match = re.search(
            r"startsWith\('\*\*\*'\).*createElement\('strong'\).*createElement\('em'\)",
            html_content,
            re.DOTALL,
        )
        assert match, "Expected ***text*** to create nested strong>em elements"


# ---------------------------------------------------------------------------
# Language badge on code blocks
# ---------------------------------------------------------------------------

class TestLanguageBadge:
    """Verify code block language badge rendering."""

    def test_language_extraction_regex(self, html_content):
        assert r"/^```(\w+)/" in html_content

    def test_badge_element_creation(self, html_content):
        assert "code-lang-badge" in html_content

    def test_badge_css(self, html_content):
        match = re.search(r'\.code-lang-badge\s*\{([^}]+)\}', html_content)
        assert match, "Expected .code-lang-badge CSS rule"
        assert "position: absolute" in match.group(1)

    def test_pre_is_relative(self, html_content):
        """Pre must be position:relative for the badge to anchor correctly."""
        match = re.search(r'\.message\s+\.body\s+pre\s*\{([^}]+)\}', html_content)
        assert match, "Expected .message .body pre CSS rule"
        assert "position: relative" in match.group(1)

    def test_language_class_on_code_element(self, html_content):
        assert "codeEl.className = 'language-'" in html_content

    def test_data_language_on_pre(self, html_content):
        assert "pre.dataset.language = lang" in html_content


# ---------------------------------------------------------------------------
# Copy button
# ---------------------------------------------------------------------------

class TestCopyButton:
    """Verify copy button for assistant messages."""

    def test_copy_button_created(self, html_content):
        assert "copyBtn.className = 'copy-btn'" in html_content

    def test_markdown_stored_in_dataset(self, html_content):
        assert "body.dataset.markdown = text" in html_content

    def test_clipboard_api_used(self, html_content):
        assert "navigator.clipboard.writeText" in html_content

    def test_exec_command_fallback(self, html_content):
        assert "document.execCommand('copy')" in html_content

    def test_copied_feedback(self, html_content):
        assert "Copied!" in html_content

    def test_copy_button_css(self, html_content):
        match = re.search(r'\.copy-btn\s*\{([^}]+)\}', html_content)
        assert match, "Expected .copy-btn CSS rule"

    def test_copy_button_only_for_assistant(self, html_content):
        """Copy button should only be added for assistant role messages."""
        # Find the copy button creation and verify it's inside an assistant check
        match = re.search(
            r"if \(role === 'assistant'\) \{\s*var copyBtn",
            html_content,
        )
        assert match, "Copy button must be inside assistant role check"


# ---------------------------------------------------------------------------
# Bullet normalization
# ---------------------------------------------------------------------------

class TestBulletNormalization:
    """Verify bullet character variants are normalized."""

    def test_unicode_bullet_normalized(self, html_content):
        """Unicode bullet (U+2022) should be normalized to -."""
        assert r"\u2022" in html_content

    def test_asterisk_bullet_normalized(self, html_content):
        """Lone * (not **) should be normalized to - for list items."""
        assert r"/^(\s*)\*(?!\*) /" in html_content


# ---------------------------------------------------------------------------
# Blank line handling in lists
# ---------------------------------------------------------------------------

class TestBlankLineListHandling:
    """Verify blank lines don't prematurely close lists."""

    def test_pending_list_close_mechanism(self, html_content):
        assert "pendingListClose" in html_content

    def test_two_consecutive_blanks_close_list(self, html_content):
        assert "consecutiveBlanks >= 2" in html_content


# ---------------------------------------------------------------------------
# Streaming markdown source preservation
# ---------------------------------------------------------------------------

class TestStreamingMarkdownSource:
    """Verify markdown source is stored during streaming for copy button."""

    def test_done_event_stores_markdown(self, html_content):
        """On 'done' event, the markdown source should be stored."""
        # There should be dataset.markdown = fullText near the done handler
        assert "body.dataset.markdown = fullText" in html_content


# ---------------------------------------------------------------------------
# XSS safety
# ---------------------------------------------------------------------------

class TestXSSSafety:
    """Verify the renderer never uses innerHTML."""

    def test_no_innerhtml_in_renderer(self, html_content):
        """The markdown renderer must never use innerHTML."""
        # Extract the renderer section
        start = html_content.find("function renderMarkdownToDOM")
        end = html_content.find("function addMessage")
        renderer_code = html_content[start:end]
        assert "innerHTML" not in renderer_code, \
            "Markdown renderer must not use innerHTML (XSS risk)"
