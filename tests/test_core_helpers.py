"""Tests for core.py slug mapping and helper functions."""

from __future__ import annotations

from pathlib import Path

from bx_skills.core import (
    CLI_TARGETS,
    detect_installed_targets,
    get_all_target_slugs,
    get_target_slug,
    resolve_skills_by_names,
    resolve_target_by_slug,
)


class TestGetTargetSlug:
    def test_all_targets_have_slugs(self) -> None:
        for target in CLI_TARGETS:
            slug = get_target_slug(target)
            assert isinstance(slug, str)
            assert slug

    def test_known_slugs(self) -> None:
        slugs = {get_target_slug(t): t.name for t in CLI_TARGETS}
        assert slugs["claude-code"] == "Claude Code"
        assert slugs["codex"] == "Codex"
        assert slugs["kilo-code"] == "Kilo Code"
        assert slugs["windsurf"] == "Windsurf"


class TestGetAllTargetSlugs:
    def test_returns_four_slugs(self) -> None:
        slugs = get_all_target_slugs()
        assert len(slugs) == 4
        assert slugs == ["claude-code", "codex", "kilo-code", "windsurf"]


class TestResolveTargetBySlug:
    def test_valid_slug(self) -> None:
        target = resolve_target_by_slug("claude-code")
        assert target is not None
        assert target.name == "Claude Code"

    def test_invalid_slug(self) -> None:
        assert resolve_target_by_slug("nonexistent") is None


class TestDetectInstalledTargets:
    def test_none_detected(self, fake_home: Path) -> None:
        result = detect_installed_targets()
        assert result == []

    def test_some_detected(self, fake_home: Path) -> None:
        (fake_home / ".claude").mkdir()
        (fake_home / ".codex").mkdir()
        result = detect_installed_targets()
        names = [t.name for t in result]
        assert "Claude Code" in names
        assert "Codex" in names
        assert "Windsurf" not in names


class TestResolveSkillsByNames:
    def test_found_and_missing(self, catalog_dir: Path) -> None:
        found, missing = resolve_skills_by_names(["alpha-skill", "no-such-skill"], catalog_dir)
        assert len(found) == 1
        assert found[0].dir_name == "alpha-skill"
        assert missing == ["no-such-skill"]

    def test_all_found(self, catalog_dir: Path) -> None:
        found, missing = resolve_skills_by_names(["alpha-skill", "bravo-skill"], catalog_dir)
        assert len(found) == 2
        assert missing == []
