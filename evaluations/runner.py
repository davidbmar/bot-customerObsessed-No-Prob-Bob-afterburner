"""Evaluation runner — test personalities against conversation scenarios.

Usage:
    python -m evaluations.runner customer-discovery

    from evaluations.runner import EvaluationRunner
    runner = EvaluationRunner()
    results = runner.run_all(llm_fn)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


SCENARIOS_DIR = Path(__file__).parent / "scenarios"


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    input_text: str
    response: str
    pass_hits: list[str] = field(default_factory=list)
    fail_hits: list[str] = field(default_factory=list)


class EvaluationRunner:
    """Load YAML scenarios and run them against an LLM function."""

    def __init__(self, scenarios_dir: Path | None = None) -> None:
        self.scenarios_dir = scenarios_dir or SCENARIOS_DIR

    def load_scenarios(self) -> list[dict[str, Any]]:
        """Load all YAML scenario files from the scenarios directory."""
        scenarios: list[dict[str, Any]] = []
        if not self.scenarios_dir.exists():
            return scenarios
        for f in sorted(self.scenarios_dir.glob("*.yaml")):
            with open(f) as fh:
                data = yaml.safe_load(fh)
                if data:
                    scenarios.append(data)
        return scenarios

    def evaluate_scenario(
        self, scenario: dict[str, Any], llm_fn: Callable[[str], str]
    ) -> ScenarioResult:
        """Run a single scenario and check pass/fail criteria."""
        input_text = scenario["input"]
        response = llm_fn(input_text)
        response_lower = response.lower()

        pass_hits: list[str] = []
        fail_hits: list[str] = []

        for criterion in scenario.get("pass_criteria", []):
            criterion_lower = criterion.lower()
            if _criterion_matches(response_lower, criterion_lower):
                pass_hits.append(criterion)

        for criterion in scenario.get("fail_criteria", []):
            criterion_lower = criterion.lower()
            if _criterion_matches(response_lower, criterion_lower):
                fail_hits.append(criterion)

        # Pass if at least one pass criterion matched AND no fail criteria matched
        passed = len(pass_hits) > 0 and len(fail_hits) == 0

        return ScenarioResult(
            name=scenario["name"],
            passed=passed,
            input_text=input_text,
            response=response,
            pass_hits=pass_hits,
            fail_hits=fail_hits,
        )

    def run_all(
        self, llm_fn: Callable[[str], str]
    ) -> list[ScenarioResult]:
        """Run all scenarios and return results."""
        scenarios = self.load_scenarios()
        results: list[ScenarioResult] = []
        for scenario in scenarios:
            results.append(self.evaluate_scenario(scenario, llm_fn))
        return results


def _criterion_matches(response: str, criterion: str) -> bool:
    """Check if a response matches a criterion using keyword heuristics.

    Criteria like 'response asks about why or who' are checked by looking
    for question marks and relevant keywords. Criteria like 'response says
    "sure, let's build..."' are checked by looking for the quoted text.
    """
    # If criterion contains a quoted phrase, check for it
    if '"' in criterion:
        # Extract text between quotes
        parts = criterion.split('"')
        for i in range(1, len(parts), 2):
            if parts[i].lower() in response:
                return True

    # Check for question-asking criteria
    question_keywords = ["asks", "question", "asks about", "asks for"]
    if any(kw in criterion for kw in question_keywords):
        if "?" in response:
            return True

    # Check for negation criteria ("does NOT")
    if "does not" in criterion or "not " in criterion:
        # For negation, check if the negative thing is absent
        # e.g., "does NOT immediately accept" — if response doesn't contain "sure" type words
        if "accept" in criterion or "agree" in criterion:
            accept_words = ["sure", "okay", "yes", "absolutely", "i'll add", "let's build"]
            return not any(w in response for w in accept_words)
        if "jump" in criterion or "implementation" in criterion or "proposes" in criterion:
            impl_words = ["implement", "optimize", "cache", "index", "refactor"]
            return not any(w in response for w in impl_words)

    # Check for keyword presence criteria ("contains")
    if "contains" in criterion:
        keywords = ["why", "who", "what", "how", "which", "when", "problem", "workflow"]
        if any(kw in response for kw in keywords):
            return True

    # Check for "explores" criteria
    if "explores" in criterion:
        if "?" in response:
            return True

    return False


# Keep backward-compatible standalone functions
def load_scenarios(personality_name: str | None = None) -> list[dict]:
    """Load all YAML scenario files (legacy function)."""
    runner = EvaluationRunner()
    return runner.load_scenarios()


def run_evaluation(personality_name: str) -> None:
    """Run all scenarios against a personality (legacy function)."""
    scenarios = load_scenarios(personality_name)
    print(f"Loaded {len(scenarios)} scenarios for '{personality_name}':")
    for s in scenarios:
        print(f"  - {s['name']}: tests {', '.join(s['principles_tested'])}")
    print("\nUse EvaluationRunner.run_all(llm_fn) for full evaluation.")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "customer-discovery"
    run_evaluation(name)
