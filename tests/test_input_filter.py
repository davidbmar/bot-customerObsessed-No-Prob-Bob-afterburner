"""Tests for bot.input_filter — STT quality classification."""

import pytest
from bot.input_filter import InputQuality, classify


# ── Garbage words ─────────────────────────────────────────────

class TestGarbageWords:
    """Single garbage words should be classified as GARBAGE."""

    @pytest.mark.parametrize("word", ["um", "uh", "the", "a", "i", "hmm", "oh", "ah",
                                       "beep", "boop", "okay", "ok", "yeah", "yes", "no",
                                       "so", "well", "right", "like", "just", "but", "and",
                                       "or", "if", "it", "something", "nothing", "huh"])
    def test_single_garbage_word(self, word):
        assert classify(word, 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    @pytest.mark.parametrize("word", ["Um", "UH", "The", "OK", "Yeah"])
    def test_garbage_case_insensitive(self, word):
        assert classify(word, 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_garbage_with_trailing_punctuation(self):
        assert classify("um.", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("uh?", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_two_garbage_words(self):
        assert classify("um uh", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("oh well", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_two_words_one_not_garbage(self):
        assert classify("hello there", 0.0, 0.0, 1.0) == InputQuality.VALID


# ── Greetings NOT filtered ────────────────────────────────────

class TestGreetingsNotFiltered:
    """Greetings are real conversational signals and must NOT be filtered."""

    @pytest.mark.parametrize("greeting", ["hello", "hi", "hey", "Hello", "Hi", "Hey"])
    def test_greeting_is_valid(self, greeting):
        assert classify(greeting, 0.0, 0.0, 1.0) == InputQuality.VALID

    def test_greeting_with_name(self):
        assert classify("hello there", 0.0, 0.0, 1.0) == InputQuality.VALID

    def test_goodbye_not_filtered(self):
        assert classify("bye", 0.0, 0.0, 1.0) == InputQuality.VALID
        assert classify("thanks", 0.0, 0.0, 1.0) == InputQuality.VALID


# ── Short audio ───────────────────────────────────────────────

class TestShortAudio:
    """Audio shorter than 0.6s should be classified as GARBAGE."""

    def test_very_short_audio(self):
        assert classify("hello", 0.0, 0.0, 0.3) == InputQuality.GARBAGE

    def test_short_audio_boundary(self):
        assert classify("hello", 0.0, 0.0, 0.5) == InputQuality.GARBAGE

    def test_audio_at_threshold(self):
        # 0.6 is NOT less than 0.6, so should pass
        assert classify("hello", 0.0, 0.0, 0.6) == InputQuality.VALID

    def test_normal_duration(self):
        assert classify("hello", 0.0, 0.0, 2.0) == InputQuality.VALID

    def test_zero_duration_skips_check(self):
        # duration=0 means unknown, should not trigger short-audio filter
        assert classify("hello", 0.0, 0.0, 0.0) == InputQuality.VALID


# ── No-speech probability ────────────────────────────────────

class TestNoSpeechProb:
    """High no_speech_prob should be classified as GARBAGE."""

    def test_high_no_speech(self):
        assert classify("hello", 0.7, 0.0, 1.0) == InputQuality.GARBAGE

    def test_very_high_no_speech(self):
        assert classify("hello", 0.95, 0.0, 1.0) == InputQuality.GARBAGE

    def test_borderline_no_speech(self):
        # 0.6 is not > 0.6
        assert classify("hello", 0.6, 0.0, 1.0) == InputQuality.VALID

    def test_low_no_speech(self):
        assert classify("hello", 0.1, 0.0, 1.0) == InputQuality.VALID


# ── Hallucination patterns ────────────────────────────────────

class TestHallucinationPatterns:
    """Whisper hallucination patterns should be classified as GARBAGE."""

    def test_punctuation_only(self):
        assert classify(". . . .", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("...", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("!?!?", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_repeated_word(self):
        assert classify("the the the", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("um um um", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_parenthetical(self):
        assert classify("(upbeat music)", 0.0, 0.0, 1.0) == InputQuality.GARBAGE
        assert classify("(applause)", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_music_notes(self):
        assert classify("♪ la la la", 0.0, 0.0, 1.0) == InputQuality.GARBAGE


# ── Low confidence ────────────────────────────────────────────

class TestLowConfidence:
    """Low confidence + short text should be LOW_QUALITY."""

    def test_low_logprob_short_text(self):
        assert classify("um okay", 0.0, -1.5, 1.0) == InputQuality.LOW_QUALITY

    def test_low_logprob_single_word(self):
        # Single garbage word is caught by garbage check first
        assert classify("um", 0.0, -1.5, 1.0) == InputQuality.GARBAGE

    def test_low_logprob_three_words(self):
        assert classify("sort of thing", 0.0, -1.2, 1.0) == InputQuality.LOW_QUALITY

    def test_low_logprob_long_text_passes(self):
        assert classify("we need better reporting tools", 0.0, -1.5, 3.0) == InputQuality.VALID

    def test_normal_logprob_short_text(self):
        assert classify("hello world friend", 0.0, -0.5, 1.0) == InputQuality.VALID


# ── Empty input ───────────────────────────────────────────────

class TestEmptyInput:
    def test_empty_string(self):
        assert classify("", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_whitespace_only(self):
        assert classify("   ", 0.0, 0.0, 1.0) == InputQuality.GARBAGE


# ── Valid input ───────────────────────────────────────────────

class TestValidInput:
    """Real questions/statements should be VALID."""

    def test_real_question(self):
        assert classify("We need better reporting", 0.0, -0.5, 3.0) == InputQuality.VALID

    def test_product_idea(self):
        assert classify("I want to build a dashboard for tracking metrics", 0.0, -0.3, 5.0) == InputQuality.VALID

    def test_problem_statement(self):
        assert classify("Our customers are churning because onboarding is too slow", 0.0, -0.4, 4.0) == InputQuality.VALID

    def test_short_but_meaningful(self):
        assert classify("Tell me more", 0.0, -0.5, 1.5) == InputQuality.VALID

    def test_greeting_is_valid(self):
        assert classify("hello", 0.0, 0.0, 1.0) == InputQuality.VALID


# ── Acceptance criteria from brief ────────────────────────────

class TestAcceptanceCriteria:
    def test_um_is_garbage(self):
        assert classify("um", 0.0, 0.0, 1.0) == InputQuality.GARBAGE

    def test_real_sentence_is_valid(self):
        assert classify("We need better reporting", 0.0, -0.5, 3.0) == InputQuality.VALID

    def test_import_works(self):
        from bot.input_filter import classify, InputQuality
        assert InputQuality.VALID.value == "valid"
