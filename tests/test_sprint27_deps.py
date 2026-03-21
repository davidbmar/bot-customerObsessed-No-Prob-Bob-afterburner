"""Sprint 27 — dependency completeness tests (B-035).

Verify that `pip install -e '.[dev]'` installs every package the bot
needs at runtime (LLM providers + Google auth).
"""


def test_anthropic_importable():
    import anthropic  # noqa: F401


def test_openai_importable():
    import openai  # noqa: F401


def test_google_auth_importable():
    from google.oauth2 import id_token  # noqa: F401


def test_google_auth_requests_transport():
    from google.auth.transport import requests  # noqa: F401
