"""Configuration — reads from ~/.config/afterburner-bots/config.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "afterburner-bots" / "config.json"

DEFAULT_CONFIG = {
    "personality": "customer-discovery",
    "llm": {
        "provider": "ollama",
        "model": "qwen3:4b",
        "baseUrl": "http://localhost:11434",
    },
    "telegram": {
        "botToken": "",
        "enabled": False,
    },
    "server": {
        "port": 1203,
        "host": "127.0.0.1",
    },
}


@dataclass
class BotConfig:
    personality: str = "customer-discovery"
    model: str = "qwen3:4b"
    ollama_url: str = "http://localhost:11434"
    telegram_token: str = ""
    telegram_enabled: bool = False
    server_port: int = 1203
    server_host: str = "127.0.0.1"

    @classmethod
    def load(cls, path: Path | None = None) -> BotConfig:
        """Load config from JSON file, falling back to defaults."""
        config_path = path or CONFIG_PATH
        if not config_path.exists():
            return cls()

        try:
            data = json.loads(config_path.read_text())
        except (json.JSONDecodeError, OSError):
            return cls()

        llm = data.get("llm", {})
        telegram = data.get("telegram", {})
        server = data.get("server", {})

        return cls(
            personality=data.get("personality", "customer-discovery"),
            model=llm.get("model", "qwen3:4b"),
            ollama_url=llm.get("baseUrl", "http://localhost:11434"),
            telegram_token=telegram.get("botToken", ""),
            telegram_enabled=telegram.get("enabled", False),
            server_port=server.get("port", 1203),
            server_host=server.get("host", "127.0.0.1"),
        )

    def save(self, path: Path | None = None) -> None:
        """Write config to disk."""
        config_path = path or CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "personality": self.personality,
            "llm": {
                "provider": "ollama",
                "model": self.model,
                "baseUrl": self.ollama_url,
            },
            "telegram": {
                "botToken": self.telegram_token,
                "enabled": self.telegram_enabled,
            },
            "server": {
                "port": self.server_port,
                "host": self.server_host,
            },
        }
        config_path.write_text(json.dumps(data, indent=2) + "\n")
