"""Conversation memory — per-chat history with fact extraction."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

MEMORY_ROOT = Path.home() / ".config" / "afterburner-bots" / "memory"


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content, "ts": self.timestamp}

    @classmethod
    def from_dict(cls, d: dict) -> Message:
        return cls(role=d["role"], content=d["content"], timestamp=d.get("ts", 0))


class ChatMemory:
    """Manages conversation history for a single chat session."""

    def __init__(self, chat_id: str, memory_root: Path | None = None) -> None:
        self.chat_id = chat_id
        self.root = (memory_root or MEMORY_ROOT) / "conversations" / chat_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.history_path = self.root / "history.jsonl"
        self.facts_path = self.root / "facts.json"
        self.summary_path = self.root / "summary.md"
        self._messages: list[Message] = self._load_history()

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)

    def add_message(self, role: str, content: str) -> Message:
        """Append a message and persist to JSONL."""
        msg = Message(role=role, content=content)
        self._messages.append(msg)
        with open(self.history_path, "a") as f:
            f.write(json.dumps(msg.to_dict()) + "\n")
        return msg

    def get_context_messages(self, max_messages: int = 20) -> list[dict]:
        """Return recent messages formatted for LLM context."""
        recent = self._messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]

    def get_facts(self) -> dict:
        """Load extracted facts if available."""
        if self.facts_path.exists():
            return json.loads(self.facts_path.read_text())
        return {}

    def save_facts(self, facts: dict) -> None:
        """Save extracted facts."""
        self.facts_path.write_text(json.dumps(facts, indent=2))

    def save_summary(self, summary: str) -> None:
        """Save LLM-generated conversation summary."""
        self.summary_path.write_text(summary)

    def get_summary(self) -> str | None:
        if self.summary_path.exists():
            return self.summary_path.read_text()
        return None

    def message_count(self) -> int:
        return len(self._messages)

    def clear(self) -> None:
        """Reset conversation (for testing)."""
        self._messages.clear()
        if self.history_path.exists():
            self.history_path.unlink()

    def _load_history(self) -> list[Message]:
        """Load messages from JSONL file."""
        messages: list[Message] = []
        if self.history_path.exists():
            for line in self.history_path.read_text().splitlines():
                line = line.strip()
                if line:
                    messages.append(Message.from_dict(json.loads(line)))
        return messages
