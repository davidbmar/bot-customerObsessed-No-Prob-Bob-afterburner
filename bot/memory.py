"""Conversation memory — JSONL-backed per-conversation history.

Storage layout:
    ~/.local/share/afterburner-bot/conversations/<conversation_id>.jsonl

Each line is a JSON object:
    {"role": "user"|"assistant", "content": "...", "timestamp": "...", "metadata": {...}}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import DEFAULT_DATA_DIR


class ConversationMemory:
    """Manages conversation history across multiple conversation IDs.

    All conversations are stored as JSONL files in a single directory,
    one file per conversation_id.
    """

    def __init__(self, storage_dir: Path | str | None = None) -> None:
        self._storage_dir = Path(storage_dir) if storage_dir else DEFAULT_DATA_DIR / "conversations"
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _conversation_path(self, conversation_id: str) -> Path:
        return self._storage_dir / f"{conversation_id}.jsonl"

    def add(self, conversation_id: str, role: str, content: str, metadata: dict | None = None) -> dict:
        """Append a message to a conversation's JSONL file."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        path = self._conversation_path(conversation_id)
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def get_history(self, conversation_id: str, limit: int = 50) -> list[dict]:
        """Return the most recent messages for a conversation."""
        path = self._conversation_path(conversation_id)
        if not path.exists():
            return []

        messages: list[dict] = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                messages.append(json.loads(line))

        return messages[-limit:]

    def list_conversations(self) -> list[str]:
        """Return all conversation IDs (filenames without .jsonl extension)."""
        return sorted(
            p.stem for p in self._storage_dir.glob("*.jsonl")
        )

    def clear(self, conversation_id: str) -> None:
        """Delete a conversation's data file."""
        path = self._conversation_path(conversation_id)
        if path.exists():
            path.unlink()

    def message_count(self, conversation_id: str) -> int:
        """Return the number of messages in a conversation."""
        path = self._conversation_path(conversation_id)
        if not path.exists():
            return 0
        return sum(1 for line in path.read_text().splitlines() if line.strip())

    def export_markdown(self, conversation_id: str) -> str:
        """Export a conversation as formatted markdown."""
        messages = self.get_history(conversation_id, limit=10000)
        if not messages:
            return ""

        parts = [f"# Conversation {conversation_id}\n"]
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            label = "User" if role == "user" else "Bot"
            parts.append(f"**{label}:** {content}\n\n---\n")

        return "\n".join(parts)
