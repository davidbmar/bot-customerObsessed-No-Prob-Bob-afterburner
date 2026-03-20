"""Tests for evaluations/runner.py — EvaluationRunner class."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from evaluations.runner import EvaluationRunner, ScenarioResult


@pytest.fixture
def scenarios_dir(tmp_path: Path) -> Path:
    """Create a temporary scenarios directory with test YAML files."""
    sdir = tmp_path / "scenarios"
    sdir.mkdir()

    # Scenario that should pass with a good response
    (sdir / "clarify.yaml").write_text(yaml.dump({
        "name": "Clarify vague request",
        "input": "We need a dashboard",
        "principles_tested": ["Dive Deep"],
        "pass_criteria": [
            "response asks about why or who",
            "response does NOT immediately accept the request",
        ],
        "fail_criteria": [
            'response says "sure, I\'ll build that"',
            "response jumps to implementation details",
        ],
    }))

    # Scenario with no pass criteria (edge case)
    (sdir / "empty.yaml").write_text(yaml.dump({
        "name": "No criteria scenario",
        "input": "Hello",
        "principles_tested": [],
        "pass_criteria": [],
        "fail_criteria": [],
    }))

    return sdir


def _good_llm(input_text: str) -> str:
    """Mock LLM that asks clarifying questions."""
    return "Can you tell me more about why you need that? Who are the users?"


def _bad_llm(input_text: str) -> str:
    """Mock LLM that immediately agrees."""
    return "Sure, I'll build that right away. Let me implement it."


def test_evaluation_runner_import() -> None:
    """EvaluationRunner can be imported from evaluations.runner."""
    from evaluations.runner import EvaluationRunner
    assert EvaluationRunner is not None


def test_load_scenarios_from_project(scenarios_dir: Path) -> None:
    """EvaluationRunner loads YAML scenarios from directory."""
    runner = EvaluationRunner(scenarios_dir=scenarios_dir)
    scenarios = runner.load_scenarios()
    assert len(scenarios) == 2
    assert scenarios[0]["name"] == "Clarify vague request"


def test_load_scenarios_from_real_dir() -> None:
    """EvaluationRunner loads the real project scenarios."""
    runner = EvaluationRunner()
    scenarios = runner.load_scenarios()
    assert len(scenarios) >= 3
    names = [s["name"] for s in scenarios]
    assert "Pushback on copy-cat request" in names


def test_evaluate_good_response_passes(scenarios_dir: Path) -> None:
    """A good LLM response (asks questions) passes the clarify scenario."""
    runner = EvaluationRunner(scenarios_dir=scenarios_dir)
    scenarios = runner.load_scenarios()
    clarify = scenarios[0]

    result = runner.evaluate_scenario(clarify, _good_llm)
    assert result.passed is True
    assert result.name == "Clarify vague request"
    assert len(result.pass_hits) > 0
    assert len(result.fail_hits) == 0


def test_evaluate_bad_response_fails(scenarios_dir: Path) -> None:
    """A bad LLM response (agrees immediately) fails the clarify scenario."""
    runner = EvaluationRunner(scenarios_dir=scenarios_dir)
    scenarios = runner.load_scenarios()
    clarify = scenarios[0]

    result = runner.evaluate_scenario(clarify, _bad_llm)
    assert result.passed is False


def test_run_all_returns_results(scenarios_dir: Path) -> None:
    """run_all returns a list of ScenarioResult for all scenarios."""
    runner = EvaluationRunner(scenarios_dir=scenarios_dir)
    results = runner.run_all(_good_llm)
    assert len(results) == 2
    assert all(isinstance(r, ScenarioResult) for r in results)


def test_scenario_result_contains_response(scenarios_dir: Path) -> None:
    """ScenarioResult includes the LLM's response text."""
    runner = EvaluationRunner(scenarios_dir=scenarios_dir)
    results = runner.run_all(_good_llm)
    for r in results:
        assert r.response != ""
        assert r.input_text != ""


def test_empty_scenarios_dir(tmp_path: Path) -> None:
    """EvaluationRunner handles empty scenarios directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    runner = EvaluationRunner(scenarios_dir=empty_dir)
    assert runner.load_scenarios() == []
    assert runner.run_all(_good_llm) == []


def test_nonexistent_scenarios_dir(tmp_path: Path) -> None:
    """EvaluationRunner handles nonexistent directory gracefully."""
    runner = EvaluationRunner(scenarios_dir=tmp_path / "nonexistent")
    assert runner.load_scenarios() == []
