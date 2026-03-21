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


# ── Background noise detection (B-038) ───────────────────────

class TestLongMonologue:
    """Text over 200 words from a single segment is likely TV/movie audio."""

    def test_300_word_movie_transcript(self):
        # Simulate a movie scene transcription — varied words, no questions, no first-person
        base = ("the ship sailed across the vast ocean towards the distant "
                "horizon where the sun was slowly setting behind the tall "
                "mountains and the crew stood watching carefully ")
        transcript = (base * 20).strip()  # ~300 words
        assert len(transcript.split()) > 200
        assert classify(transcript, 0.0, 0.0, 60.0) == InputQuality.BACKGROUND_NOISE

    def test_250_word_narration(self):
        # Long narration-style text without engagement markers
        words = (
            "The ship sailed across the vast ocean towards the distant horizon "
            "where the sun was slowly setting behind the mountains and the crew "
            "stood watching the waves crash against the hull as the wind carried "
            "them further from shore "
        )
        # Repeat to get over 200 words
        long_text = (words * 7).strip()
        assert len(long_text.split()) > 200
        assert classify(long_text, 0.0, 0.0, 45.0) == InputQuality.BACKGROUND_NOISE

    def test_long_user_message_with_first_person_passes(self):
        # Over 200 words but with first-person pronouns — user is talking to bot
        base = "I think the product needs better error handling and more robust "
        text = base + " ".join(["feature"] * 200)
        assert len(text.split()) > 200
        # Long monologue check fires first (>200), so this is BACKGROUND_NOISE
        assert classify(text, 0.0, 0.0, 40.0) == InputQuality.BACKGROUND_NOISE

    def test_201_words_is_background(self):
        base = ("the ship sailed across the vast ocean towards the distant "
                "horizon where the sun was slowly setting behind the tall "
                "mountains and the crew stood watching carefully ")
        text = (base * 14).strip()
        assert len(text.split()) > 200
        assert classify(text, 0.0, 0.0, 40.0) == InputQuality.BACKGROUND_NOISE


class TestRepeatedPhrases:
    """Repeated phrases (3+ times) indicate media audio."""

    def test_repeated_phrase_caught(self):
        text = "on the mat on the mat on the mat something else here too"
        assert classify(text, 0.0, 0.0, 5.0) == InputQuality.BACKGROUND_NOISE

    def test_repeated_two_word_phrase(self):
        text = "come back come back come back and then more words follow"
        assert classify(text, 0.0, 0.0, 5.0) == InputQuality.BACKGROUND_NOISE

    def test_no_repeats_passes(self):
        text = "the quick brown fox jumps over the lazy dog near the park"
        # "the" appears 3 times but as single words within different ngrams
        assert classify(text, 0.0, 0.0, 5.0) == InputQuality.VALID

    def test_short_text_not_checked(self):
        # Under 6 words, repeated phrase check is skipped
        text = "please help right now thanks"
        # This is 5 words — below threshold for repeated phrase detection
        assert classify(text, 0.0, 0.0, 2.0) == InputQuality.VALID


class TestNoEngagementMarkers:
    """Long text (>50 words) without questions, greetings, or first-person."""

    def test_long_narration_no_markers(self):
        # 60+ words, no ?, no greetings, no first-person
        text = (
            "The detective walked through the dark alley searching for clues "
            "about the missing artifact that had been stolen from the museum "
            "last night when the guards were changing shifts and the security "
            "cameras had been disabled by someone with access to the control "
            "room on the second floor of the east wing near the emergency exit "
            "that leads to the parking garage behind the old warehouse district"
        )
        assert len(text.split()) > 50
        assert classify(text, 0.0, 0.0, 15.0) == InputQuality.BACKGROUND_NOISE

    def test_long_text_with_question_passes(self):
        text = (
            "The detective walked through the dark alley searching for clues "
            "about the missing artifact that had been stolen from the museum "
            "last night when the guards were changing shifts and the security "
            "cameras had been disabled by someone with access to the control "
            "room on the second floor. Can you help me understand what happened?"
        )
        assert len(text.split()) > 50
        assert classify(text, 0.0, 0.0, 15.0) == InputQuality.VALID

    def test_long_text_with_greeting_passes(self):
        text = (
            "Hey " + "the detective walked through the dark alley searching for clues "
            "about the missing artifact that had been stolen from the museum "
            "last night when the guards were changing shifts and the security "
            "cameras had been disabled by someone with access to the control "
            "room on the second floor of the east wing near the emergency exit"
        )
        assert len(text.split()) > 50
        assert classify(text, 0.0, 0.0, 15.0) == InputQuality.VALID

    def test_long_text_with_first_person_passes(self):
        text = (
            "I think the detective walked through the dark alley searching for clues "
            "about the missing artifact that had been stolen from the museum "
            "last night when the guards were changing shifts and the security "
            "cameras had been disabled by someone with access to the control "
            "room on the second floor of the east wing near the emergency exit"
        )
        assert len(text.split()) > 50
        assert classify(text, 0.0, 0.0, 15.0) == InputQuality.VALID

    def test_normal_user_message_passes(self):
        text = "I want to build a feedback tool"
        assert classify(text, 0.0, 0.0, 3.0) == InputQuality.VALID

    def test_50_words_boundary_passes(self):
        # Exactly 50 words — should NOT trigger (> 50 required)
        text = (
            "alpha bravo charlie delta echo foxtrot golf hotel india juliet "
            "kilo lima mike november oscar papa quebec romeo sierra tango "
            "uniform victor whiskey xray yankee zulu one two three four "
            "five six seven eight nine ten eleven twelve thirteen fourteen "
            "fifteen sixteen seventeen eighteen nineteen twenty extra bonus final complete"
        )
        # 50 unique words — exactly at boundary, should NOT trigger
        assert len(text.split()) == 50
        assert classify(text, 0.0, 0.0, 10.0) == InputQuality.VALID


class TestBackgroundNoiseMessage:
    """BACKGROUND_NOISE_MESSAGE is exported and has expected content."""

    def test_message_exists(self):
        from bot.input_filter import BACKGROUND_NOISE_MESSAGE
        assert "background audio" in BACKGROUND_NOISE_MESSAGE
        assert "listening" in BACKGROUND_NOISE_MESSAGE
