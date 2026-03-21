"""Configuration — reads from ~/.config/afterburner-bots/config.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "afterburner-bots" / "config.json"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "afterburner-bot"
REGISTRY_PATH = Path.home() / ".config" / "afterburner" / "registry.json"
DASHBOARD_PROJECTS_PATH = (
    Path.home() / "src" / "traceable-searchable-adr-memory-index" / "dashboard" / "projects.json"
)


@dataclass
class BotConfig:
    personality: str = "customer-discovery"
    model: str = "qwen3:4b"
    ollama_url: str = "http://localhost:11434"
    data_dir: str = ""
    telegram_token: str = ""
    telegram_enabled: bool = False
    server_port: int = 1203
    server_host: str = "127.0.0.1"
    projects: dict[str, str] = field(default_factory=dict)
    active_project: str = ""
    google_client_id: str = ""
    allowed_emails: str = ""

    def __post_init__(self) -> None:
        if not self.data_dir:
            self.data_dir = str(DEFAULT_DATA_DIR)
        if not self.projects:
            self.projects = _auto_discover_projects()
        if not self.active_project and self.projects:
            self.active_project = next(iter(self.projects))

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def personality_name(self) -> str:
        return self.personality

    @property
    def conversations_dir(self) -> Path:
        return Path(self.data_dir) / "conversations"

    @property
    def active_project_root(self) -> Path | None:
        """Return the Path for the active project, or None."""
        if self.active_project and self.active_project in self.projects:
            return Path(self.projects[self.active_project])
        return None

    def add_project(self, slug: str, root_path: str) -> None:
        """Register a project by slug and root path."""
        self.projects[slug] = root_path
        if not self.active_project:
            self.active_project = slug

    def switch_project(self, slug: str) -> bool:
        """Switch the active project. Returns True if successful."""
        if slug not in self.projects:
            return False
        self.active_project = slug
        return True

    def list_projects(self) -> list[str]:
        """Return registered project slugs."""
        return list(self.projects.keys())

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

        auth = data.get("auth", {})

        return cls(
            personality=data.get("personality", "customer-discovery"),
            model=llm.get("model", "qwen3:4b"),
            ollama_url=llm.get("baseUrl", "http://localhost:11434"),
            data_dir=data.get("data_dir", ""),
            telegram_token=telegram.get("botToken", ""),
            telegram_enabled=telegram.get("enabled", False),
            server_port=server.get("port", 1203),
            server_host=server.get("host", "127.0.0.1"),
            projects=data.get("projects", {}),
            active_project=data.get("active_project", ""),
            google_client_id=auth.get("google_client_id", ""),
            allowed_emails=auth.get("allowed_emails", ""),
        )

    def save(self, path: Path | None = None) -> None:
        """Write config to disk."""
        config_path = path or CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "personality": self.personality,
            "data_dir": self.data_dir,
            "projects": self.projects,
            "active_project": self.active_project,
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
            "auth": {
                "google_client_id": self.google_client_id,
                "allowed_emails": self.allowed_emails,
            },
        }
        config_path.write_text(json.dumps(data, indent=2) + "\n")


def _auto_discover_projects() -> dict[str, str]:
    """Auto-discover projects from registry.json or dashboard projects.json."""
    # Try afterburner registry first
    if REGISTRY_PATH.exists():
        try:
            data = json.loads(REGISTRY_PATH.read_text())
            projects: dict[str, str] = {}
            entries = data if isinstance(data, list) else data.get("projects", []) if isinstance(data, dict) else []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                slug = entry.get("slug", "")
                root = entry.get("rootPath", "").replace("~", str(Path.home()))
                if slug and root:
                    projects[slug] = root
            if projects:
                return projects
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    # Fall back to dashboard projects.json
    if DASHBOARD_PROJECTS_PATH.exists():
        try:
            data = json.loads(DASHBOARD_PROJECTS_PATH.read_text())
            if not isinstance(data, list):
                return {}
            projects = {}
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                slug = entry.get("slug", "")
                root = entry.get("rootPath", "").replace("~", str(Path.home()))
                if slug and root:
                    projects[slug] = root
            return projects
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    return {}
