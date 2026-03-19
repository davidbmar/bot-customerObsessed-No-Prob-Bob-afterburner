"""Personality loader — reads markdown personality docs and builds system prompts."""

from __future__ import annotations

import re
from pathlib import Path

# Default location for personality files
DEFAULT_PERSONALITIES_DIR = Path(__file__).resolve().parent.parent / "personalities"
USER_PERSONALITIES_DIR = Path.home() / ".config" / "afterburner-bots" / "personalities"


class Personality:
    """Load a markdown personality document and produce a system prompt.

    Supports inheritance via ``Extends: base.md`` in the personality doc.
    """

    def __init__(
        self,
        name: str,
        personalities_dir: Path | None = None,
    ) -> None:
        self.name = name
        self.dir = personalities_dir or _resolve_dir(name)
        self.path = self.dir / f"{name}.md"
        if not self.path.exists():
            raise FileNotFoundError(f"Personality not found: {self.path}")
        self.content = self.path.read_text()
        self.base: str | None = self._load_base()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def to_system_prompt(self) -> str:
        """Return full system prompt: base personality + this personality."""
        parts: list[str] = []
        if self.base:
            parts.append(self.base)
        parts.append(self.content)
        return "\n\n---\n\n".join(parts)

    def get_principles(self) -> list[str]:
        """Extract principle heading names (### headings under ## Your Principles)."""
        in_principles = False
        principles: list[str] = []
        for line in self.content.splitlines():
            if line.strip().startswith("## Your Principles"):
                in_principles = True
                continue
            if in_principles and line.strip().startswith("## "):
                break  # next top-level section
            if in_principles and line.strip().startswith("### "):
                principles.append(line.strip().lstrip("# ").strip())
        return principles

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_base(self) -> str | None:
        """Read the 'Extends: <file>' directive if present."""
        m = re.search(r"^Extends:\s*(.+)$", self.content, re.MULTILINE)
        if not m:
            return None
        base_filename = m.group(1).strip()
        base_path = self.dir / base_filename
        if not base_path.exists():
            raise FileNotFoundError(f"Base personality not found: {base_path}")
        return base_path.read_text()


def _resolve_dir(name: str) -> Path:
    """Check user dir first, then fall back to project-bundled personalities."""
    user_path = USER_PERSONALITIES_DIR / f"{name}.md"
    if user_path.exists():
        return USER_PERSONALITIES_DIR
    return DEFAULT_PERSONALITIES_DIR


def list_personalities(personalities_dir: Path | None = None) -> list[str]:
    """Return available personality names."""
    dirs = [DEFAULT_PERSONALITIES_DIR]
    if USER_PERSONALITIES_DIR.exists():
        dirs.append(USER_PERSONALITIES_DIR)
    if personalities_dir and personalities_dir.exists():
        dirs.append(personalities_dir)

    names: set[str] = set()
    for d in dirs:
        for f in d.glob("*.md"):
            if f.name.startswith("_"):
                continue
            names.add(f.stem)
    return sorted(names)
