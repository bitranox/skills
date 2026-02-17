"""Tests for bx_skills.core._ignore_pycache, install_skill, uninstall_skill."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.core import (
    InstallPlan,
    Scope,
    SkillAction,
    SkillInfo,
    _ignore_pycache,
    install_skill,
    uninstall_skill,
)

pytestmark = pytest.mark.os_agnostic


# ── _ignore_pycache ─────────────────────────────────────────────────────────


def test_ignore_pycache_filters_pycache_dir() -> None:
    ignored = _ignore_pycache("some/dir", ["__pycache__", "SKILL.md", "utils.py"])
    assert "__pycache__" in ignored
    assert "SKILL.md" not in ignored


def test_ignore_pycache_filters_pyc_files() -> None:
    ignored = _ignore_pycache("some/dir", ["module.pyc", "module.py"])
    assert "module.pyc" in ignored
    assert "module.py" not in ignored


def test_ignore_pycache_passes_normal_files() -> None:
    ignored = _ignore_pycache("some/dir", ["readme.md", "config.toml"])
    assert ignored == set()


def test_ignore_pycache_handles_empty_list() -> None:
    assert _ignore_pycache("some/dir", []) == set()


# ── install_skill ────────────────────────────────────────────────────────────


def _make_plan(
    source: Path, dest: Path, action: SkillAction = SkillAction.INSTALL
) -> InstallPlan:
    skill = SkillInfo(
        dir_name="test-skill",
        name="Test Skill",
        description="For testing",
        source_path=source,
    )
    from tests.conftest import sample_target as _  # noqa: F401

    target_obj = __import__("bx_skills.core", fromlist=["CLITarget"]).CLITarget(
        name="TestCLI",
        user_path_tpl=".testcli/skills/{skill}",
        project_path_tpl=".testcli/skills/{skill}",
        project_only=False,
        detect_dir=".testcli",
    )
    return InstallPlan(
        skill=skill,
        target=target_obj,
        scope=Scope.USER,
        destination=dest,
        action=action,
    )


def test_install_copies_files(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-a"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("content", encoding="utf-8")
    (src / "extra.txt").write_text("bonus", encoding="utf-8")

    dest = tmp_path / "dest" / "skills" / "skill-a"
    plan = _make_plan(src, dest)
    install_skill(plan)

    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "content"
    assert (dest / "extra.txt").read_text(encoding="utf-8") == "bonus"


def test_install_creates_parent_directories(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-b"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("data", encoding="utf-8")

    dest = tmp_path / "deep" / "nested" / "path" / "skill-b"
    plan = _make_plan(src, dest)
    install_skill(plan)
    assert dest.is_dir()


def test_install_overwrites_existing(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-c"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("new content", encoding="utf-8")

    dest = tmp_path / "dest" / "skill-c"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("old content", encoding="utf-8")

    plan = _make_plan(src, dest)
    install_skill(plan)
    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "new content"


def test_install_excludes_pycache(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-d"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("ok", encoding="utf-8")
    pycache = src / "__pycache__"
    pycache.mkdir()
    (pycache / "mod.cpython-312.pyc").write_bytes(b"\x00")
    (src / "compiled.pyc").write_bytes(b"\x00")

    dest = tmp_path / "dest" / "skill-d"
    plan = _make_plan(src, dest)
    install_skill(plan)

    assert (dest / "SKILL.md").is_file()
    assert not (dest / "__pycache__").exists()
    assert not (dest / "compiled.pyc").exists()


# ── uninstall_skill ──────────────────────────────────────────────────────────


def test_uninstall_removes_directory(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-e"
    src.mkdir(parents=True)
    (src / "SKILL.md").write_text("data", encoding="utf-8")

    dest = tmp_path / "dest" / "skill-e"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("installed", encoding="utf-8")

    plan = _make_plan(src, dest, SkillAction.UNINSTALL)
    uninstall_skill(plan)
    assert not dest.exists()


def test_uninstall_noop_when_missing(tmp_path: Path) -> None:
    src = tmp_path / "source" / "skill-f"
    src.mkdir(parents=True)

    dest = tmp_path / "dest" / "skill-f"
    plan = _make_plan(src, dest, SkillAction.UNINSTALL)
    uninstall_skill(plan)  # should not raise
    assert not dest.exists()
