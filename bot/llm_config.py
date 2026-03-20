"""LLM provider config persistence — per-provider settings stored in JSON."""

from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "afterburner-bots" / "llm-providers.json"


def _load_all(path: Path | None = None) -> dict:
    """Load the full config file."""
    p = path or CONFIG_PATH
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all(data: dict, path: Path | None = None) -> None:
    """Save the full config file."""
    p = path or CONFIG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n")


def load_provider_config(provider_id: str, path: Path | None = None) -> dict:
    """Load config for a specific provider.

    Returns dict with keys: base_url, model, api_key (from config or env).
    """
    from .llm import LLM_PROVIDERS

    data = _load_all(path)
    providers = data.get("providers", {})
    saved = providers.get(provider_id, {})

    provider_def = LLM_PROVIDERS.get(provider_id, {})
    base_url = saved.get("base_url", provider_def.get("default_base_url", ""))
    model = saved.get("model", provider_def.get("default_model", ""))

    # API key: config file -> env var -> empty
    api_key = saved.get("api_key", "")
    if not api_key:
        fmt = provider_def.get("api_format", "openai")
        if fmt == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        else:
            api_key = os.environ.get("OPENAI_API_KEY", "")

    return {
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
    }


def save_provider_config(
    provider_id: str,
    config: dict,
    path: Path | None = None,
) -> None:
    """Save config for a specific provider.

    config may contain: base_url, model, api_key.
    """
    data = _load_all(path)
    providers = data.setdefault("providers", {})
    existing = providers.get(provider_id, {})
    if "base_url" in config:
        existing["base_url"] = config["base_url"]
    if "model" in config:
        existing["model"] = config["model"]
    if "api_key" in config:
        existing["api_key"] = config["api_key"]
    providers[provider_id] = existing
    _save_all(data, path)


def get_active_provider(path: Path | None = None) -> str:
    """Return the active provider ID, defaulting to 'qwen-3.5'."""
    data = _load_all(path)
    return data.get("active_provider", "qwen-3.5")


def set_active_provider(provider_id: str, path: Path | None = None) -> None:
    """Set the active provider ID."""
    data = _load_all(path)
    data["active_provider"] = provider_id
    _save_all(data, path)
