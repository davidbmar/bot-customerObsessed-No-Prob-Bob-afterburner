"""Evaluation runner — test personalities against conversation scenarios.

Phase 2 implementation. This is the scaffold.

Usage:
    python -m evaluations.runner customer-discovery
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


SCENARIOS_DIR = Path(__file__).parent / "scenarios"


def load_scenarios(personality_name: str | None = None) -> list[dict]:
    """Load all YAML scenario files."""
    scenarios = []
    for f in sorted(SCENARIOS_DIR.glob("*.yaml")):
        with open(f) as fh:
            scenarios.append(yaml.safe_load(fh))
    return scenarios


def run_evaluation(personality_name: str) -> None:
    """Run all scenarios against a personality (stub for Phase 2)."""
    scenarios = load_scenarios(personality_name)
    print(f"Loaded {len(scenarios)} scenarios for '{personality_name}':")
    for s in scenarios:
        print(f"  - {s['name']}: tests {', '.join(s['principles_tested'])}")
    print("\nFull evaluation requires Phase 2 implementation.")
    print("Each scenario will send the input to the LLM and check pass/fail criteria.")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "customer-discovery"
    run_evaluation(name)
