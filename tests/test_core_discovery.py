"""Tests for bx_skills.core.discover_skills."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.core import CATALOG_DIR, discover_skills

pytestmark = pytest.mark.os_agnostic


def test_discovers_skills_sorted_by_name(catalog_dir: Path) -> None:
    skills = discover_skills(catalog_dir)
    names = [s.dir_name for s in skills]
    assert names == ["alpha-skill", "bravo-skill"]


def test_hidden_directories_are_skipped(catalog_dir: Path) -> None:
    skills = discover_skills(catalog_dir)
    dir_names = [s.dir_name for s in skills]
    assert ".hidden-dir" not in dir_names


def test_regular_files_are_skipped(catalog_dir: Path) -> None:
    skills = discover_skills(catalog_dir)
    dir_names = [s.dir_name for s in skills]
    assert "README.md" not in dir_names


def test_empty_catalog_returns_empty_list(tmp_path: Path) -> None:
    empty = tmp_path / "empty-catalog"
    empty.mkdir()
    assert discover_skills(empty) == []


def test_nonexistent_path_returns_empty_list(tmp_path: Path) -> None:
    assert discover_skills(tmp_path / "does-not-exist") == []


def test_skill_without_skill_md_uses_dir_name_as_fallback(tmp_path: Path) -> None:
    cat = tmp_path / "catalog"
    cat.mkdir()
    (cat / "no-md-skill").mkdir()
    skills = discover_skills(cat)
    assert len(skills) == 1
    assert skills[0].name == "no-md-skill"
    assert skills[0].description == ""


@pytest.mark.local_only
def test_default_catalog_returns_skills() -> None:
    """Verify the real bundled catalog produces results."""
    assert CATALOG_DIR.is_dir()
    skills = discover_skills(None)
    assert len(skills) > 0
