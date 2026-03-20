"""Tests for bot.memory.ConversationMemory."""

from __future__ import annotations

import json

import pytest

from bot.memory import ConversationMemory


@pytest.fixture
def memory(tmp_path):
    """Create a ConversationMemory backed by a temporary directory."""
    return ConversationMemory(storage_dir=tmp_path)


class TestAddAndRetrieve:
    def test_add_and_get_history(self, memory: ConversationMemory):
        memory.add("conv1", "user", "Hello")
        memory.add("conv1", "assistant", "Hi there!")

        history = memory.get_history("conv1")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    def test_entries_have_required_fields(self, memory: ConversationMemory):
        entry = memory.add("conv1", "user", "test message", metadata={"source": "cli"})
        assert entry["role"] == "user"
        assert entry["content"] == "test message"
        assert "timestamp" in entry
        assert entry["metadata"] == {"source": "cli"}

    def test_metadata_defaults_to_empty_dict(self, memory: ConversationMemory):
        entry = memory.add("conv1", "user", "hi")
        assert entry["metadata"] == {}

    def test_get_history_limit(self, memory: ConversationMemory):
        for i in range(10):
            memory.add("conv1", "user", f"msg {i}")

        history = memory.get_history("conv1", limit=3)
        assert len(history) == 3
        assert history[0]["content"] == "msg 7"
        assert history[2]["content"] == "msg 9"

    def test_get_history_empty_conversation(self, memory: ConversationMemory):
        history = memory.get_history("nonexistent")
        assert history == []


class TestConversationIsolation:
    def test_different_ids_dont_mix(self, memory: ConversationMemory):
        memory.add("alice", "user", "I am Alice")
        memory.add("bob", "user", "I am Bob")

        alice_history = memory.get_history("alice")
        bob_history = memory.get_history("bob")

        assert len(alice_history) == 1
        assert len(bob_history) == 1
        assert alice_history[0]["content"] == "I am Alice"
        assert bob_history[0]["content"] == "I am Bob"

    def test_clearing_one_does_not_affect_other(self, memory: ConversationMemory):
        memory.add("alice", "user", "hello")
        memory.add("bob", "user", "hello")

        memory.clear("alice")

        assert memory.get_history("alice") == []
        assert len(memory.get_history("bob")) == 1


class TestListConversations:
    def test_list_empty(self, memory: ConversationMemory):
        assert memory.list_conversations() == []

    def test_list_returns_correct_ids(self, memory: ConversationMemory):
        memory.add("conv-a", "user", "hi")
        memory.add("conv-b", "user", "hi")
        memory.add("conv-c", "user", "hi")

        ids = memory.list_conversations()
        assert ids == ["conv-a", "conv-b", "conv-c"]

    def test_list_after_clear(self, memory: ConversationMemory):
        memory.add("conv-a", "user", "hi")
        memory.add("conv-b", "user", "hi")

        memory.clear("conv-a")

        assert memory.list_conversations() == ["conv-b"]


class TestClear:
    def test_clear_deletes_conversation(self, memory: ConversationMemory):
        memory.add("conv1", "user", "hello")
        assert len(memory.get_history("conv1")) == 1

        memory.clear("conv1")
        assert memory.get_history("conv1") == []

    def test_clear_nonexistent_is_noop(self, memory: ConversationMemory):
        memory.clear("nonexistent")  # should not raise

    def test_message_count_after_clear(self, memory: ConversationMemory):
        memory.add("conv1", "user", "hello")
        assert memory.message_count("conv1") == 1

        memory.clear("conv1")
        assert memory.message_count("conv1") == 0


class TestExportMarkdown:
    def test_export_basic_conversation(self, memory: ConversationMemory):
        memory.add("conv1", "user", "Hello")
        memory.add("conv1", "assistant", "Hi there!")
        md = memory.export_markdown("conv1")
        assert "# Conversation conv1" in md
        assert "**User:** Hello" in md
        assert "**Bot:** Hi there!" in md
        assert "---" in md

    def test_export_empty_conversation(self, memory: ConversationMemory):
        md = memory.export_markdown("nonexistent")
        assert md == ""

    def test_export_multiple_exchanges(self, memory: ConversationMemory):
        memory.add("conv1", "user", "Q1")
        memory.add("conv1", "assistant", "A1")
        memory.add("conv1", "user", "Q2")
        memory.add("conv1", "assistant", "A2")
        md = memory.export_markdown("conv1")
        assert md.count("**User:**") == 2
        assert md.count("**Bot:**") == 2

    def test_export_preserves_content(self, memory: ConversationMemory):
        memory.add("conv1", "user", "Tell me about **markdown**")
        md = memory.export_markdown("conv1")
        assert "**markdown**" in md


class TestJsonlFormat:
    def test_stored_as_valid_jsonl(self, memory: ConversationMemory, tmp_path):
        memory.add("conv1", "user", "line 1")
        memory.add("conv1", "assistant", "line 2")

        jsonl_path = tmp_path / "conv1.jsonl"
        assert jsonl_path.exists()

        lines = jsonl_path.read_text().strip().splitlines()
        assert len(lines) == 2

        for line in lines:
            entry = json.loads(line)
            assert "role" in entry
            assert "content" in entry
            assert "timestamp" in entry
            assert "metadata" in entry
