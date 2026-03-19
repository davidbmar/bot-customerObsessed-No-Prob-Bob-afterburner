# Sprint 1 — Agent Notes

*Started: 2026-03-19 23:46 UTC*

Phase 1 Agents: 3
- agentA-personality
- agentB-llm-webchat
- agentC-memory-cli

Phase 2 Agents: 0
(none)

Automated summaries from each agent are appended below as they complete.

---

## agentA-personality

*Completed: 2026-03-19 23:49 UTC*

```
All done. Here's the summary:

## Files Changed

| File | Action |
|------|--------|
| `bot/personality.py` | Rewritten — `PersonalityLoader` + `PersonalityDoc` with YAML frontmatter, inheritance, principle extraction |
| `personalities/base.md` | Rewritten — YAML frontmatter, `## Principles` with Polite/Honest/Helpful/Curious |
| `personalities/customer-discovery.md` | Rewritten — `extends: base` frontmatter, 5 discovery principles |
| `tests/__init__.py` | Created |
| `tests/test_personality.py` | Created — 10 tests, all passing |
| `docs/project-memory/sessions/S-2026-03-19-2349-sprint1-personality-framework.md` | Created — session doc |

## Commands Run

- `git pull origin main` — synced with main
- `python3 -m pytest tests/test_personality.py -v` — **10 passed**
- `git push -u origin HEAD` — pushed to `agentA-personality`

## Notes / Follow-on Work

- The old `Personality` class and `list_personalities()` function were replaced. Any code importing the old API (e.g., `server.py`, `cli.py`) will need updating to use `PersonalityLoader`.
- `customer-discovery` loads with **9 merged principles** (4 base + 5 discovery), exceeding the 5+ acceptance criterion.
- The `pyyaml` dependency was already in `pyproject.toml` — no new deps needed.
```


---

## agentC-memory-cli

*Completed: 2026-03-19 23:51 UTC*

```
All tasks complete. Here's the summary:

---

## Files Changed

| File | Change |
|------|--------|
| `bot/config.py` | Added `data_dir` field, `conversations_dir` property, `DEFAULT_DATA_DIR` constant |
| `bot/memory.py` | Replaced `ChatMemory` with `ConversationMemory` class (JSONL-per-conversation) |
| `bot/gateway.py` | Updated to use single `ConversationMemory` instance |
| `bot/server.py` | Updated `/api/history` endpoint for new memory API |
| `cli.py` | Rewritten with `start`/`chat`/`status` commands; status checks server via HTTP |
| `tests/__init__.py` | New (empty) |
| `tests/test_memory.py` | New — 14 tests all passing |
| `docs/project-memory/sessions/S-2026-03-19-2350-memory-cli.md` | Session doc |

## Commands Run

- `python3 -m pytest tests/test_memory.py -v` — 14/14 passed
- `git push -u origin HEAD` — pushed to `agentC-memory-cli`

## Notes / Follow-on Work

- The `ConversationMemory` stores at `~/.local/share/afterburner-bot/conversations/` (XDG data dir) rather than the old `~/.config/` location
- `cli.py status` uses `httpx` to probe the server — requires httpx (already a dependency)
- Gateway imports are deferred in `cmd_start`/`cmd_chat` so `cli.py status` doesn't need Ollama running
```


---

## agentB-llm-webchat

*Completed: 2026-03-19 23:53 UTC*

```
The background task already completed — I read its output earlier and all acceptance criteria passed. The work is done and pushed to `agentB-llm-webchat`.
```

