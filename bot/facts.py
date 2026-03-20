"""Fact extraction from conversation messages.

FactExtractor uses pattern matching to identify problems, users,
use cases, and constraints from natural language messages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# Pattern definitions: (category, regex pattern, base confidence)
PATTERNS: list[tuple[str, str, float]] = [
    ("problem", r"(?:the\s+)?problem\s+is\s+(.+?)(?:\.|$)", 0.9),
    ("problem", r"(?:we\s+)?struggle\s+(?:with\s+)?(.+?)(?:\.|$)", 0.8),
    ("problem", r"(?:the\s+)?issue\s+is\s+(.+?)(?:\.|$)", 0.85),
    ("problem", r"(?:the\s+)?challenge\s+is\s+(.+?)(?:\.|$)", 0.8),
    ("problem", r"pain\s+point\s+(?:is\s+)?(.+?)(?:\.|$)", 0.85),
    ("user", r"our\s+users?\s+(?:are\s+)?(.+?)(?:\.|$)", 0.9),
    ("user", r"(?:the\s+)?customers?\s+(?:are\s+)?(.+?)(?:\.|$)", 0.8),
    ("user", r"(?:we\s+)?serve\s+(.+?)(?:\.|$)", 0.75),
    ("user", r"target\s+(?:audience|users?)\s+(?:is|are)\s+(.+?)(?:\.|$)", 0.9),
    ("use_case", r"we\s+need\s+(?:to\s+)?(.+?)(?:\.|$)", 0.85),
    ("use_case", r"(?:the\s+)?goal\s+is\s+(?:to\s+)?(.+?)(?:\.|$)", 0.9),
    ("use_case", r"(?:we\s+)?want\s+to\s+(.+?)(?:\.|$)", 0.75),
    ("use_case", r"use\s+case\s+(?:is\s+)?(.+?)(?:\.|$)", 0.9),
    ("constraint", r"must\s+not\s+(.+?)(?:\.|$)", 0.9),
    ("constraint", r"(?:we\s+)?cannot\s+(.+?)(?:\.|$)", 0.85),
    ("constraint", r"(?:it\s+)?should\s+not\s+(.+?)(?:\.|$)", 0.8),
    ("constraint", r"(?:the\s+)?requirement\s+is\s+(.+?)(?:\.|$)", 0.85),
    ("constraint", r"(?:we\s+)?have\s+to\s+(.+?)(?:\.|$)", 0.7),
]


@dataclass
class Fact:
    category: str
    content: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
        }


class FactExtractor:
    """Extract structured facts from conversation messages."""

    def extract(self, messages: list[str]) -> list[dict[str, Any]]:
        """Extract facts from a list of message strings.

        Returns a list of dicts with category, content, and confidence.
        """
        facts: list[Fact] = []
        seen: set[str] = set()

        for message in messages:
            for category, pattern, confidence in PATTERNS:
                for match in re.finditer(pattern, message, re.IGNORECASE):
                    content = match.group(1).strip()
                    if not content or len(content) < 3:
                        continue
                    # Deduplicate by content
                    key = f"{category}:{content.lower()}"
                    if key in seen:
                        continue
                    seen.add(key)
                    facts.append(Fact(category=category, content=content, confidence=confidence))

        return [f.to_dict() for f in facts]

    def summarize(self, facts: list[dict[str, Any]]) -> str:
        """Generate a markdown summary grouped by category."""
        if not facts:
            return "No facts extracted."

        grouped: dict[str, list[dict[str, Any]]] = {}
        for fact in facts:
            cat = fact["category"]
            grouped.setdefault(cat, []).append(fact)

        category_labels = {
            "problem": "Problems",
            "user": "Users",
            "use_case": "Use Cases",
            "constraint": "Constraints",
        }

        lines: list[str] = ["# Extracted Facts", ""]
        for cat in ["problem", "user", "use_case", "constraint"]:
            items = grouped.get(cat, [])
            if not items:
                continue
            label = category_labels.get(cat, cat.title())
            lines.append(f"## {label}")
            for item in items:
                conf = item["confidence"]
                lines.append(f"- {item['content']} (confidence: {conf:.1f})")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"
