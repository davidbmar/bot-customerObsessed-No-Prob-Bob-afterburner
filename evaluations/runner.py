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


# ANSI color helpers — only emit codes when writing to a terminal
def _use_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _green(text: str) -> str:
    return f"\033[32m{text}\033[0m" if _use_color() else text


def _red(text: str) -> str:
    return f"\033[31m{text}\033[0m" if _use_color() else text


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m" if _use_color() else text


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if _use_color() else text


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m" if _use_color() else text


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

    # Check for "acknowledges" criteria (empathy/recognition)
    if "acknowledges" in criterion:
        empathy_words = [
            "understand", "hear you", "sounds", "frustrat", "difficult",
            "sorry", "appreciate", "recognize", "makes sense", "i see",
            "that must", "challenging",
        ]
        if any(w in response for w in empathy_words):
            return True

    # Check for "captures" criteria (records/notes requirements)
    if "captures" in criterion:
        capture_words = [
            "compliance", "security", "audit", "soc2", "sso",
            "requirement", "note", "important", "non-functional",
        ]
        if any(w in response for w in capture_words):
            return True

    # Check for "ignores" / "ignore" negation (does NOT ignore)
    if "does not ignore" in criterion or "not ignore" in criterion:
        # If the criterion says "does NOT ignore X", check that response mentions related terms
        if "compliance" in criterion or "security" in criterion:
            security_words = ["compliance", "security", "audit", "soc2", "sso", "requirement"]
            if any(w in response for w in security_words):
                return True
        if "prior" in criterion or "context" in criterion:
            context_words = ["previous", "last time", "before", "prior", "earlier", "discussed"]
            if any(w in response for w in context_words):
                return True
        # Generic: if response has a question, it's not ignoring
        if "?" in response:
            return True

    # Check for "priority" or "urgent" criteria
    if "priority" in criterion or "urgent" in criterion or "impactful" in criterion:
        priority_words = ["priority", "prioritize", "urgent", "important", "which", "most", "first"]
        if any(w in response for w in priority_words):
            return True
        if "?" in response:
            return True

    # Check for "solve all" or "address all" negation
    if ("solve all" in criterion or "address all" in criterion
            or "multiple problems" in criterion or "all three" in criterion):
        all_words = ["all three", "address all", "solve all", "let me handle all", "tackle all"]
        return any(w in response for w in all_words)

    return False


def print_results(
    results: list[ScenarioResult],
    verbose: bool = False,
    scenarios: list[dict[str, Any]] | None = None,
) -> None:
    """Print evaluation results with colored pass/fail output."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    # Build a map of scenario name → principles_tested
    principles_map: dict[str, list[str]] = {}
    if scenarios:
        for s in scenarios:
            principles_map[s["name"]] = s.get("principles_tested", [])

    for r in results:
        if r.passed:
            status = _green("PASS")
        else:
            status = _red("FAIL")
        print(f"  [{status}] {r.name}")

        if verbose:
            # Show principles tested
            principles = principles_map.get(r.name, [])
            if principles:
                print(f"         {_dim('principles:')} {', '.join(principles)}")
            if r.pass_hits:
                for ph in r.pass_hits:
                    print(f"         {_green('+')} {ph}")
            if not r.passed:
                if r.fail_hits:
                    for fh in r.fail_hits:
                        print(f"         {_red('-')} {_red('fail:')} {fh}")
                if not r.pass_hits:
                    print(f"         {_yellow('!')} {_yellow('no pass criteria matched')}")
        else:
            # Summary mode: only show failure reasons
            if not r.passed:
                if r.fail_hits:
                    for fh in r.fail_hits:
                        print(f"         {_red('fail:')} {fh}")
                if not r.pass_hits:
                    print(f"         {_yellow('no pass criteria matched')}")

    # Summary line
    print()
    if failed == 0:
        summary = _green(f"{passed}/{len(results)} scenarios passed")
    else:
        summary = _red(f"{passed}/{len(results)} scenarios passed")
    print(f"  {_bold(summary)}")

    # Principles summary in verbose mode
    if verbose and principles_map:
        all_principles: set[str] = set()
        passed_principles: set[str] = set()
        for r in results:
            ps = principles_map.get(r.name, [])
            all_principles.update(ps)
            if r.passed:
                passed_principles.update(ps)
        failed_principles = all_principles - passed_principles
        if all_principles:
            print(f"\n  {_bold('Principles:')}")
            for p in sorted(all_principles):
                if p in passed_principles and p not in failed_principles:
                    print(f"    {_green('+')} {p}")
                else:
                    print(f"    {_red('-')} {p}")


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
