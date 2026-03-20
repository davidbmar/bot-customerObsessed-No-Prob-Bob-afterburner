"""Tests for bot/config.py — multi-project support: add, switch, list, persist."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bot.config import BotConfig, _auto_discover_projects


@pytest.fixture
def empty_config() -> BotConfig:
    """Create a config with no auto-discovery."""
    with patch("bot.config._auto_discover_projects", return_value={}):
        return BotConfig()


@pytest.fixture
def config_with_projects() -> BotConfig:
    """Create a config with pre-populated projects."""
    with patch("bot.config._auto_discover_projects", return_value={}):
        return BotConfig(
            projects={"alpha": "/tmp/alpha", "beta": "/tmp/beta"},
            active_project="alpha",
        )


class TestMultiProjectAdd:
    def test_add_project_registers_slug(self, empty_config: BotConfig) -> None:
        empty_config.add_project("myapp", "/home/user/myapp")
        assert "myapp" in empty_config.projects
        assert empty_config.projects["myapp"] == "/home/user/myapp"

    def test_add_project_sets_active_if_first(self, empty_config: BotConfig) -> None:
        assert empty_config.active_project == ""
        empty_config.add_project("first", "/tmp/first")
        assert empty_config.active_project == "first"

    def test_add_project_does_not_override_active(self, config_with_projects: BotConfig) -> None:
        config_with_projects.add_project("gamma", "/tmp/gamma")
        assert config_with_projects.active_project == "alpha"


class TestMultiProjectSwitch:
    def test_switch_to_existing_project(self, config_with_projects: BotConfig) -> None:
        assert config_with_projects.switch_project("beta")
        assert config_with_projects.active_project == "beta"

    def test_switch_to_nonexistent_returns_false(self, config_with_projects: BotConfig) -> None:
        assert not config_with_projects.switch_project("nonexistent")
        assert config_with_projects.active_project == "alpha"


class TestMultiProjectList:
    def test_list_projects_returns_slugs(self, config_with_projects: BotConfig) -> None:
        slugs = config_with_projects.list_projects()
        assert set(slugs) == {"alpha", "beta"}

    def test_list_projects_empty_when_none(self, empty_config: BotConfig) -> None:
        assert empty_config.list_projects() == []


class TestActiveProjectRoot:
    def test_active_project_root_returns_path(self, config_with_projects: BotConfig) -> None:
        root = config_with_projects.active_project_root
        assert root == Path("/tmp/alpha")

    def test_active_project_root_none_when_empty(self, empty_config: BotConfig) -> None:
        assert empty_config.active_project_root is None

    def test_active_project_root_none_when_not_in_dict(self) -> None:
        with patch("bot.config._auto_discover_projects", return_value={}):
            cfg = BotConfig(active_project="missing")
        assert cfg.active_project_root is None


class TestConfigPersistence:
    def test_save_and_load_preserves_projects(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        with patch("bot.config._auto_discover_projects", return_value={}):
            cfg = BotConfig(
                projects={"proj1": "/a/b", "proj2": "/c/d"},
                active_project="proj2",
            )
        cfg.save(path=config_path)

        with patch("bot.config._auto_discover_projects", return_value={}):
            loaded = BotConfig.load(path=config_path)
        assert loaded.projects == {"proj1": "/a/b", "proj2": "/c/d"}
        assert loaded.active_project == "proj2"

    def test_load_missing_file_returns_defaults(self, tmp_path: Path) -> None:
        with patch("bot.config._auto_discover_projects", return_value={}):
            cfg = BotConfig.load(path=tmp_path / "nonexistent.json")
        assert cfg.personality == "customer-discovery"
        assert cfg.projects == {}

    def test_load_invalid_json_returns_defaults(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")
        with patch("bot.config._auto_discover_projects", return_value={}):
            cfg = BotConfig.load(path=bad_file)
        assert cfg.personality == "customer-discovery"


class TestAutoDiscovery:
    def test_discovers_from_registry(self, tmp_path: Path) -> None:
        registry = tmp_path / "registry.json"
        registry.write_text(json.dumps([
            {"slug": "proj-a", "rootPath": "/home/user/proj-a"},
            {"slug": "proj-b", "rootPath": "/home/user/proj-b"},
        ]))
        with patch("bot.config.REGISTRY_PATH", registry), \
             patch("bot.config.DASHBOARD_PROJECTS_PATH", tmp_path / "nope.json"):
            result = _auto_discover_projects()
        assert "proj-a" in result
        assert "proj-b" in result

    def test_discovers_from_dashboard_fallback(self, tmp_path: Path) -> None:
        dashboard = tmp_path / "projects.json"
        dashboard.write_text(json.dumps([
            {"slug": "dash-proj", "rootPath": "/home/user/dash-proj"},
        ]))
        with patch("bot.config.REGISTRY_PATH", tmp_path / "nope.json"), \
             patch("bot.config.DASHBOARD_PROJECTS_PATH", dashboard):
            result = _auto_discover_projects()
        assert "dash-proj" in result

    def test_returns_empty_when_no_files(self, tmp_path: Path) -> None:
        with patch("bot.config.REGISTRY_PATH", tmp_path / "no.json"), \
             patch("bot.config.DASHBOARD_PROJECTS_PATH", tmp_path / "nope.json"):
            result = _auto_discover_projects()
        assert result == {}

    def test_post_init_auto_selects_first_project(self) -> None:
        with patch("bot.config._auto_discover_projects", return_value={"auto": "/tmp/auto"}):
            cfg = BotConfig()
        assert cfg.active_project == "auto"
        assert "auto" in cfg.projects
