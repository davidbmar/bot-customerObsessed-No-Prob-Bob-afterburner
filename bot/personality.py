"""Personality loader — reads markdown personality docs and builds system prompts.

Uses YAML frontmatter for metadata (name, extends) and extracts principles
from ## Principles / ### <Name> sections in markdown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class PersonalityDoc:
    """Immutable result of loading a personality."""

    name: str
    principles: list[str]
    system_prompt: str
    raw_content: str


class PersonalityLoader:
    """Load personality markdown files with inheritance support.

    Usage::

        loader = PersonalityLoader(Path("personalities"))
        doc = loader.load("customer-discovery")
        print(doc.system_prompt)
    """

    def __init__(self, personalities_dir: str | Path) -> None:
        self.dir = Path(personalities_dir)
        if not self.dir.is_dir():
            raise FileNotFoundError(
                f"Personalities directory not found: {self.dir}"
            )

    def load(self, name: str) -> PersonalityDoc:
        """Load a personality by name, resolving inheritance."""
        path = self.dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(
                f"Personality '{name}' not found at {path}"
            )

        raw_content = path.read_text()
        frontmatter, body = _parse_frontmatter(raw_content)

        # Resolve inheritance
        parent_doc: PersonalityDoc | None = None
        extends = frontmatter.get("extends")
        if extends:
            parent_doc = self.load(extends)

        principles = _extract_principles(body)

        # Merge: parent principles first, then child
        all_principles = []
        if parent_doc:
            all_principles.extend(parent_doc.principles)
        all_principles.extend(principles)

        # Build system prompt: parent body + child body
        prompt_parts: list[str] = []
        if parent_doc:
            prompt_parts.append(parent_doc.raw_content)
        prompt_parts.append(body)
        system_prompt = "\n\n---\n\n".join(prompt_parts)

        return PersonalityDoc(
            name=frontmatter.get("name", name),
            principles=all_principles,
            system_prompt=system_prompt,
            raw_content=body,
        )

    def list_personalities(self) -> list[str]:
        """Return sorted names of available personalities."""
        return sorted(
            f.stem
            for f in self.dir.glob("*.md")
            if not f.name.startswith("_")
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body.

    Returns (frontmatter_dict, body_text). If no frontmatter is found,
    returns an empty dict and the full text.
    """
    m = re.match(r"\A---\s*\n(.*?\n)---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text

    fm = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return fm, body


def _extract_principles(body: str) -> list[str]:
    """Extract principle names from ### headings under ## Principles."""
    principles: list[str] = []
    in_section = False

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Principles"):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break  # hit the next top-level section
        if in_section and stripped.startswith("### "):
            name = stripped.lstrip("#").strip()
            principles.append(name)

    return principles
