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


# ---------------------------------------------------------------------------
# Sprint 15 — New scenario tests
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = ["name", "input", "principles_tested", "pass_criteria", "fail_criteria"]

NEW_SCENARIO_FILES = [
    "technical-customer.yaml",
    "emotional-customer.yaml",
    "multi-problem.yaml",
    "solution-fixated.yaml",
    "returning-customer.yaml",
    "enterprise-customer.yaml",
]

REAL_SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "evaluations" / "scenarios"


class TestRealScenariosCount:
    """Verify the project has 8+ scenarios after Sprint 15 expansion."""

    def test_at_least_9_scenario_files(self) -> None:
        """evaluations/scenarios/ contains at least 9 YAML files."""
        yamls = list(REAL_SCENARIOS_DIR.glob("*.yaml"))
        assert len(yamls) >= 9

    def test_runner_loads_all_scenarios(self) -> None:
        """EvaluationRunner loads all 9 scenarios."""
        runner = EvaluationRunner()
        scenarios = runner.load_scenarios()
        assert len(scenarios) >= 9


class TestNewScenarioFilesExist:
    """Each new scenario file exists in evaluations/scenarios/."""

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_file_exists(self, filename: str) -> None:
        assert (REAL_SCENARIOS_DIR / filename).exists(), f"Missing {filename}"


class TestNewScenarioStructure:
    """Each new scenario has required fields and well-formed criteria."""

    @pytest.fixture
    def all_scenarios(self) -> list[dict]:
        runner = EvaluationRunner()
        return runner.load_scenarios()

    @pytest.fixture
    def scenario_map(self, all_scenarios: list[dict]) -> dict:
        return {s["name"]: s for s in all_scenarios}

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_scenario_has_required_field(self, filename: str, field: str) -> None:
        """Every new scenario YAML contains the required field."""
        path = REAL_SCENARIOS_DIR / filename
        data = yaml.safe_load(path.read_text())
        assert field in data, f"{filename} missing '{field}'"

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_pass_criteria_non_empty(self, filename: str) -> None:
        data = yaml.safe_load((REAL_SCENARIOS_DIR / filename).read_text())
        assert len(data["pass_criteria"]) >= 2, f"{filename} needs >=2 pass criteria"

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_fail_criteria_non_empty(self, filename: str) -> None:
        data = yaml.safe_load((REAL_SCENARIOS_DIR / filename).read_text())
        assert len(data["fail_criteria"]) >= 1, f"{filename} needs >=1 fail criteria"

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_principles_tested_non_empty(self, filename: str) -> None:
        data = yaml.safe_load((REAL_SCENARIOS_DIR / filename).read_text())
        assert len(data["principles_tested"]) >= 1

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_input_is_non_empty_string(self, filename: str) -> None:
        data = yaml.safe_load((REAL_SCENARIOS_DIR / filename).read_text())
        assert isinstance(data["input"], str) and len(data["input"]) > 10

    @pytest.mark.parametrize("filename", NEW_SCENARIO_FILES)
    def test_name_is_non_empty_string(self, filename: str) -> None:
        data = yaml.safe_load((REAL_SCENARIOS_DIR / filename).read_text())
        assert isinstance(data["name"], str) and len(data["name"]) > 5


# ---------------------------------------------------------------------------
# Criterion-matching tests for new patterns added in Sprint 15
# ---------------------------------------------------------------------------

from evaluations.runner import _criterion_matches


class TestCriterionMatchesAcknowledges:
    """_criterion_matches handles 'acknowledges' criteria."""

    def test_acknowledges_frustration(self) -> None:
        assert _criterion_matches(
            "i understand how frustrating this must be. can you tell me more?",
            "response acknowledges the frustration or difficulty",
        )

    def test_acknowledges_with_sorry(self) -> None:
        assert _criterion_matches(
            "i'm sorry to hear that. what specifically is not working?",
            "response acknowledges the frustration or difficulty",
        )

    def test_no_acknowledgement(self) -> None:
        assert not _criterion_matches(
            "let me fix the api endpoint right away.",
            "response acknowledges the frustration or difficulty",
        )


class TestCriterionMatchesCaptures:
    """_criterion_matches handles 'captures' criteria."""

    def test_captures_compliance(self) -> None:
        assert _criterion_matches(
            "i note the soc2 compliance requirement. who will be using this portal?",
            "response captures non-functional requirements like compliance or security",
        )

    def test_captures_security(self) -> None:
        assert _criterion_matches(
            "security is clearly important here. what audit standards do you follow?",
            "response captures non-functional requirements like compliance or security",
        )

    def test_no_capture(self) -> None:
        assert not _criterion_matches(
            "sure, let's build the portal right away.",
            "response captures non-functional requirements like compliance or security",
        )


class TestCriterionMatchesDoesNotIgnore:
    """_criterion_matches handles 'does NOT ignore' criteria."""

    def test_does_not_ignore_compliance(self) -> None:
        assert _criterion_matches(
            "the compliance requirements are important. what does soc2 require for you?",
            "response does not ignore the compliance and security concerns",
        )

    def test_does_not_ignore_prior_context(self) -> None:
        assert _criterion_matches(
            "welcome back! can you remind me what we discussed previously?",
            "response does not ignore the prior context",
        )


class TestCriterionMatchesPriority:
    """_criterion_matches handles priority/urgency criteria."""

    def test_asks_about_priority(self) -> None:
        assert _criterion_matches(
            "which of these is the most urgent for your team?",
            "response asks about which problem is most urgent or impactful",
        )

    def test_asks_which_first(self) -> None:
        assert _criterion_matches(
            "those are three distinct issues. which one should we tackle first?",
            "response contains a question about priority or impact",
        )


class TestCriterionMatchesSolveAll:
    """_criterion_matches handles 'solve all' negation criteria."""

    def test_tries_to_solve_all_fails(self) -> None:
        assert _criterion_matches(
            "let me address all three issues right now.",
            'response says "let me address all three"',
        )

    def test_focused_response_passes(self) -> None:
        assert not _criterion_matches(
            "which of those is most impactful for your users?",
            'response says "let me address all three"',
        )


# ---------------------------------------------------------------------------
# End-to-end: new scenarios pass/fail with mock LLMs
# ---------------------------------------------------------------------------

def _empathetic_llm(input_text: str) -> str:
    """Mock LLM that acknowledges emotions and asks questions."""
    return (
        "I understand how frustrating that must be. "
        "Can you tell me more about what specifically is not working? "
        "Which part is causing the most problems for your team?"
    )


def _technical_questioner_llm(input_text: str) -> str:
    """Mock LLM that asks about users/problems behind technical requests."""
    return (
        "That's an interesting technical approach. Before we dive into the details, "
        "who will be the primary users of this? What problem are you trying to solve "
        "for them? Understanding the why will help us make better decisions."
    )


def _compliance_aware_llm(input_text: str) -> str:
    """Mock LLM that acknowledges compliance and asks about users."""
    return (
        "I note the SOC2 compliance and SSO requirements — those are important. "
        "Who will be the primary users of this portal, and what do they need to do? "
        "Understanding the user workflows will help us design with security in mind."
    )


def _context_aware_llm(input_text: str) -> str:
    """Mock LLM that acknowledges prior conversation."""
    return (
        "Welcome back! I appreciate you following up on the dashboard project. "
        "Can you remind me what we discussed previously so I can make sure we build "
        "on those decisions? What were the key outcomes from last time?"
    )


def _prioritizer_llm(input_text: str) -> str:
    """Mock LLM that helps prioritize multiple problems."""
    return (
        "Those are three distinct concerns. Which one is most urgent for your team "
        "right now? Let's focus on the highest priority first so we can make meaningful "
        "progress. What's causing the most pain?"
    )


class TestNewScenariosPassWithGoodLLM:
    """Good mock LLMs pass each new scenario."""

    def _run_scenario(self, name: str, llm_fn) -> ScenarioResult:
        runner = EvaluationRunner()
        scenarios = runner.load_scenarios()
        scenario = next(s for s in scenarios if s["name"] == name)
        return runner.evaluate_scenario(scenario, llm_fn)

    def test_technical_customer_passes(self) -> None:
        result = self._run_scenario("Technical customer with jargon", _technical_questioner_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"

    def test_emotional_customer_passes(self) -> None:
        result = self._run_scenario("Emotional frustrated customer", _empathetic_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"

    def test_multi_problem_passes(self) -> None:
        result = self._run_scenario("Customer with multiple problems", _prioritizer_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"

    def test_solution_fixated_passes(self) -> None:
        result = self._run_scenario("Solution-fixated customer", _technical_questioner_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"

    def test_returning_customer_passes(self) -> None:
        result = self._run_scenario("Returning customer referencing prior context", _context_aware_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"

    def test_enterprise_customer_passes(self) -> None:
        result = self._run_scenario("Enterprise customer with compliance needs", _compliance_aware_llm)
        assert result.passed, f"Expected pass. Hits: {result.pass_hits}, Fails: {result.fail_hits}"


class TestNewScenariosFailWithBadLLM:
    """Bad mock LLM fails each new scenario."""

    def _run_scenario(self, name: str) -> ScenarioResult:
        runner = EvaluationRunner()
        scenarios = runner.load_scenarios()
        scenario = next(s for s in scenarios if s["name"] == name)
        return runner.evaluate_scenario(scenario, _bad_llm)

    def test_technical_customer_fails(self) -> None:
        result = self._run_scenario("Technical customer with jargon")
        assert not result.passed

    def test_emotional_customer_fails(self) -> None:
        result = self._run_scenario("Emotional frustrated customer")
        assert not result.passed

    def test_multi_problem_fails(self) -> None:
        result = self._run_scenario("Customer with multiple problems")
        assert not result.passed

    def test_solution_fixated_fails(self) -> None:
        result = self._run_scenario("Solution-fixated customer")
        assert not result.passed

    def test_returning_customer_fails(self) -> None:
        result = self._run_scenario("Returning customer referencing prior context")
        assert not result.passed

    def test_enterprise_customer_fails(self) -> None:
        result = self._run_scenario("Enterprise customer with compliance needs")
        assert not result.passed
