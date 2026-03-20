"""Tests for bot/facts.py — FactExtractor class."""

from __future__ import annotations

from bot.facts import FactExtractor


def test_extract_problem() -> None:
    """FactExtractor finds problem statements."""
    extractor = FactExtractor()
    facts = extractor.extract(["The problem is users can't find their orders."])
    assert len(facts) >= 1
    assert facts[0]["category"] == "problem"
    assert "orders" in facts[0]["content"].lower()
    assert facts[0]["confidence"] > 0.5


def test_extract_user() -> None:
    """FactExtractor identifies user descriptions."""
    extractor = FactExtractor()
    facts = extractor.extract(["Our users are small business owners."])
    assert len(facts) >= 1
    user_facts = [f for f in facts if f["category"] == "user"]
    assert len(user_facts) >= 1
    assert "small business" in user_facts[0]["content"].lower()


def test_extract_use_case() -> None:
    """FactExtractor finds use case / need statements."""
    extractor = FactExtractor()
    facts = extractor.extract(["We need to track inventory in real time."])
    assert len(facts) >= 1
    use_case_facts = [f for f in facts if f["category"] == "use_case"]
    assert len(use_case_facts) >= 1
    assert "inventory" in use_case_facts[0]["content"].lower()


def test_extract_constraint() -> None:
    """FactExtractor picks up constraints with 'must not'."""
    extractor = FactExtractor()
    facts = extractor.extract(["The system must not lose any data."])
    assert len(facts) >= 1
    constraint_facts = [f for f in facts if f["category"] == "constraint"]
    assert len(constraint_facts) >= 1
    assert "data" in constraint_facts[0]["content"].lower()


def test_extract_multiple_categories() -> None:
    """FactExtractor handles multiple categories in one message set."""
    extractor = FactExtractor()
    messages = [
        "The problem is slow checkout flow.",
        "Our users are online shoppers.",
        "We need to reduce checkout time.",
        "Must not require page reloads.",
    ]
    facts = extractor.extract(messages)
    categories = {f["category"] for f in facts}
    assert "problem" in categories
    assert "user" in categories
    assert "use_case" in categories
    assert "constraint" in categories


def test_extract_deduplicates() -> None:
    """FactExtractor doesn't return duplicate facts."""
    extractor = FactExtractor()
    facts = extractor.extract([
        "The problem is slow loading.",
        "The problem is slow loading.",
    ])
    problem_facts = [f for f in facts if f["category"] == "problem"]
    assert len(problem_facts) == 1


def test_extract_empty_messages() -> None:
    """FactExtractor returns empty list for empty input."""
    extractor = FactExtractor()
    assert extractor.extract([]) == []


def test_extract_no_matches() -> None:
    """FactExtractor returns empty list when no patterns match."""
    extractor = FactExtractor()
    facts = extractor.extract(["Hello, how are you today?"])
    assert facts == []


def test_summarize_grouped_by_category() -> None:
    """summarize() produces markdown grouped by category."""
    extractor = FactExtractor()
    facts = [
        {"category": "problem", "content": "Slow checkout", "confidence": 0.9},
        {"category": "user", "content": "Online shoppers", "confidence": 0.8},
        {"category": "use_case", "content": "Reduce checkout time", "confidence": 0.85},
    ]
    summary = extractor.summarize(facts)
    assert "## Problems" in summary
    assert "## Users" in summary
    assert "## Use Cases" in summary
    assert "Slow checkout" in summary


def test_summarize_empty() -> None:
    """summarize() handles empty facts list."""
    extractor = FactExtractor()
    summary = extractor.summarize([])
    assert "No facts" in summary


def test_summarize_includes_confidence() -> None:
    """summarize() includes confidence scores."""
    extractor = FactExtractor()
    facts = [{"category": "problem", "content": "Test issue", "confidence": 0.9}]
    summary = extractor.summarize(facts)
    assert "0.9" in summary


def test_extract_goal_is_pattern() -> None:
    """FactExtractor matches 'the goal is' pattern."""
    extractor = FactExtractor()
    facts = extractor.extract(["The goal is to improve user retention."])
    use_case_facts = [f for f in facts if f["category"] == "use_case"]
    assert len(use_case_facts) >= 1
    assert "retention" in use_case_facts[0]["content"].lower()
