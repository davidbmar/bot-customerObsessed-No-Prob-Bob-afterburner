"""Tests for the personality loader."""

from pathlib import Path

import pytest

from bot.personality import PersonalityLoader

PERSONALITIES_DIR = Path(__file__).resolve().parent.parent / "personalities"


@pytest.fixture
def loader() -> PersonalityLoader:
    return PersonalityLoader(PERSONALITIES_DIR)


class TestPersonalityLoader:
    """PersonalityLoader core behaviour."""

    def test_load_base(self, loader: PersonalityLoader) -> None:
        doc = loader.load("base")
        assert doc.name == "base"
        assert len(doc.principles) >= 4
        assert "Polite" in doc.principles
        assert "Honest" in doc.principles
        assert "Helpful" in doc.principles
        assert "Curious" in doc.principles

    def test_load_customer_discovery(self, loader: PersonalityLoader) -> None:
        doc = loader.load("customer-discovery")
        assert doc.name == "customer-discovery"
        # Should have 5 own principles
        own_principles = [
            "Customer Obsession",
            "Dive Deep",
            "Bias for Action",
            "Working Backwards",
            "Structured Output",
        ]
        for p in own_principles:
            assert p in doc.principles, f"Missing principle: {p}"

    def test_inheritance_merges_principles(self, loader: PersonalityLoader) -> None:
        doc = loader.load("customer-discovery")
        # Base has 4, child has 5 → at least 9
        assert len(doc.principles) >= 9
        # Base principles come first
        assert "Polite" in doc.principles
        assert "Customer Obsession" in doc.principles

    def test_system_prompt_includes_all_principles(
        self, loader: PersonalityLoader
    ) -> None:
        doc = loader.load("customer-discovery")
        prompt = doc.system_prompt
        # Both base and child content should appear
        assert "Polite" in prompt
        assert "Customer Obsession" in prompt
        assert "Working Backwards" in prompt
        # The separator between base and child
        assert "---" in prompt

    def test_system_prompt_has_base_before_child(
        self, loader: PersonalityLoader
    ) -> None:
        doc = loader.load("customer-discovery")
        prompt = doc.system_prompt
        # Base content should appear before child content
        base_pos = prompt.index("Base Personality")
        child_pos = prompt.index("Customer Discovery Agent")
        assert base_pos < child_pos

    def test_missing_personality_raises(self, loader: PersonalityLoader) -> None:
        with pytest.raises(FileNotFoundError, match="no-such-personality"):
            loader.load("no-such-personality")

    def test_missing_directory_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match="Personalities directory"):
            PersonalityLoader("/nonexistent/path")

    def test_list_personalities(self, loader: PersonalityLoader) -> None:
        names = loader.list_personalities()
        assert "base" in names
        assert "customer-discovery" in names

    def test_five_plus_principles(self, loader: PersonalityLoader) -> None:
        """Acceptance criterion: customer-discovery has 5+ principles."""
        doc = loader.load("customer-discovery")
        assert len(doc.principles) >= 5

    def test_raw_content_excludes_frontmatter(
        self, loader: PersonalityLoader
    ) -> None:
        doc = loader.load("base")
        assert "---" not in doc.raw_content.split("\n")[0]
        assert "name:" not in doc.raw_content

    def test_personality_knows_about_voice(
        self, loader: PersonalityLoader
    ) -> None:
        """B-037: customer-discovery must know about voice/STT/TTS capabilities."""
        doc = loader.load("customer-discovery")
        prompt = doc.system_prompt.lower()
        assert "voice" in prompt or "speech" in prompt or "hear" in prompt, (
            "Personality system prompt must mention voice capabilities"
        )
        assert "text-only" not in prompt, (
            "Personality must not claim to be text-only"
        )
        assert "can't hear" not in prompt, (
            "Personality must not claim it can't hear"
        )
