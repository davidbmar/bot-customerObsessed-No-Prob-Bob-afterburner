"""Tests for bot.fast_path — instant answers without LLM."""

import pytest
from bot.fast_path import try_fast_path


# ── Help fast path ────────────────────────────────────────────

class TestHelpFastPath:
    """'help' and variants should return a help message."""

    def test_help(self):
        result = try_fast_path("help")
        assert result is not None
        assert "discovery" in result.lower() or "help" in result.lower()

    def test_help_with_question_mark(self):
        result = try_fast_path("help?")
        assert result is not None

    def test_what_can_you_do(self):
        result = try_fast_path("what can you do")
        assert result is not None

    def test_what_can_you_do_question(self):
        result = try_fast_path("what can you do?")
        assert result is not None

    def test_what_do_you_do(self):
        result = try_fast_path("what do you do")
        assert result is not None

    def test_how_does_this_work(self):
        result = try_fast_path("how does this work")
        assert result is not None

    def test_help_case_insensitive(self):
        result = try_fast_path("Help")
        assert result is not None

    def test_help_uppercase(self):
        result = try_fast_path("HELP")
        assert result is not None


# ── Reset fast path ───────────────────────────────────────────

class TestResetFastPath:
    """'reset' and variants should return a reset message."""

    def test_reset(self):
        result = try_fast_path("reset")
        assert result is not None
        assert "fresh" in result.lower() or "start" in result.lower()

    def test_start_over(self):
        result = try_fast_path("start over")
        assert result is not None

    def test_new_conversation(self):
        result = try_fast_path("new conversation")
        assert result is not None

    def test_clear(self):
        result = try_fast_path("clear")
        assert result is not None

    def test_reset_case_insensitive(self):
        result = try_fast_path("Reset")
        assert result is not None


# ── Identity fast path ────────────────────────────────────────

class TestIdentityFastPath:
    """'who are you' and variants should return an identity message."""

    def test_who_are_you(self):
        result = try_fast_path("who are you")
        assert result is not None
        assert "bob" in result.lower() or "discovery" in result.lower()

    def test_who_are_you_question(self):
        result = try_fast_path("who are you?")
        assert result is not None

    def test_what_are_you(self):
        result = try_fast_path("what are you")
        assert result is not None

    def test_who_is_this(self):
        result = try_fast_path("who is this")
        assert result is not None

    def test_identity_case_insensitive(self):
        result = try_fast_path("Who Are You?")
        assert result is not None


# ── No match → None ───────────────────────────────────────────

class TestNoMatch:
    """Real questions should return None (fall through to LLM)."""

    def test_real_question(self):
        assert try_fast_path("We need a dashboard") is None

    def test_product_idea(self):
        assert try_fast_path("I want to build an app for tracking workouts") is None

    def test_problem_statement(self):
        assert try_fast_path("Our users are complaining about slow load times") is None

    def test_greeting(self):
        assert try_fast_path("hello") is None

    def test_empty_string(self):
        assert try_fast_path("") is None

    def test_whitespace(self):
        assert try_fast_path("   ") is None

    def test_partial_match(self):
        assert try_fast_path("help me build a dashboard") is None

    def test_question_about_features(self):
        assert try_fast_path("can you help me brainstorm feature ideas") is None


# ── Acceptance criteria from brief ────────────────────────────

class TestAcceptanceCriteria:
    def test_help_returns_message(self):
        result = try_fast_path("help")
        assert result is not None
        assert len(result) > 10

    def test_dashboard_returns_none(self):
        assert try_fast_path("We need a dashboard") is None

    def test_import_works(self):
        from bot.fast_path import try_fast_path
        assert callable(try_fast_path)
