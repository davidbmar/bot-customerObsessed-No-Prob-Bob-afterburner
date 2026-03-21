"""Fast-path intent matching — intercepts simple queries before the LLM.

For a voice-enabled discovery bot, some queries have deterministic answers
that don't need an LLM round trip. This module pattern-matches STT output
and returns an instant response, or None to fall through to the LLM.

Current fast paths:
  - "help" / "what can you do" → describe the bot's purpose
  - "reset" / "start over" → signal to clear conversation
  - "who are you" / "what are you" → personality description
"""

import re
import logging
from typing import Optional

log = logging.getLogger("fast_path")

# ── Pattern groups ────────────────────────────────────────────

_HELP_PATTERNS = [
    re.compile(r"^help[\?\.\!]?\s*$", re.I),
    re.compile(r"^what can you do[\?\.\!]?\s*$", re.I),
    re.compile(r"^what do you do[\?\.\!]?\s*$", re.I),
    re.compile(r"^how does this work[\?\.\!]?\s*$", re.I),
]

_RESET_PATTERNS = [
    re.compile(r"^reset[\.\!]?\s*$", re.I),
    re.compile(r"^start over[\.\!]?\s*$", re.I),
    re.compile(r"^new conversation[\.\!]?\s*$", re.I),
    re.compile(r"^clear[\.\!]?\s*$", re.I),
]

_IDENTITY_PATTERNS = [
    re.compile(r"^who are you[\?\.\!]?\s*$", re.I),
    re.compile(r"^what are you[\?\.\!]?\s*$", re.I),
    re.compile(r"^who is this[\?\.\!]?\s*$", re.I),
]

# ── Response templates ────────────────────────────────────────

_HELP_RESPONSE = (
    "I'm a discovery bot — I help you explore and refine your product ideas. "
    "Tell me about a problem you're trying to solve, the users you're building for, "
    "or an idea you want to validate. I'll ask follow-up questions to help you think "
    "it through. You can also say 'reset' to start a new conversation."
)

_RESET_RESPONSE = (
    "Got it — let's start fresh! Tell me about a problem you'd like to explore, "
    "or describe the product idea you're working on."
)

_IDENTITY_RESPONSE = (
    "I'm No-Prob Bob, a discovery bot powered by AI. I help teams explore product ideas "
    "through structured conversation — identifying problems, users, use cases, and success "
    "criteria. Think of me as a brainstorming partner for early-stage product thinking."
)


def try_fast_path(text: str) -> Optional[str]:
    """Try to answer a query without the LLM. Returns response or None.

    Args:
        text: The STT transcription or chat message.

    Returns:
        A natural language response string, or None if no fast path matched.
    """
    text_clean = text.strip()
    if not text_clean:
        return None

    # Help
    for pattern in _HELP_PATTERNS:
        if pattern.match(text_clean):
            log.info("Fast path (help): %r", text_clean)
            return _HELP_RESPONSE

    # Reset
    for pattern in _RESET_PATTERNS:
        if pattern.match(text_clean):
            log.info("Fast path (reset): %r", text_clean)
            return _RESET_RESPONSE

    # Identity
    for pattern in _IDENTITY_PATTERNS:
        if pattern.match(text_clean):
            log.info("Fast path (identity): %r", text_clean)
            return _IDENTITY_RESPONSE

    return None
