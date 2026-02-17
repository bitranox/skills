"""Tests for bx_skills.core.resolve_destination and check_installed."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.core import CLITarget, Scope, SkillInfo, check_installed, resolve_destination

pytestmark = pytest.mark.os_agnostic


def test_user_scope_resolves_under_home(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_home: Path
) -> None:
    dest = resolve_destination(sample_skill, sample_target, Scope.USER)
    assert dest == fake_home / ".testcli" / "skills" / "alpha-skill"


def test_project_scope_resolves_under_cwd(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_cwd: Path
) -> None:
    dest = resolve_destination(sample_skill, sample_target, Scope.PROJECT)
    assert dest == fake_cwd / ".testcli" / "skills" / "alpha-skill"


def test_template_substitutes_skill_dir_name(
    sample_skill: SkillInfo, fake_home: Path
) -> None:
    target = CLITarget(
        name="Custom",
        user_path_tpl=".custom/rules/{skill}",
        project_path_tpl=".custom/rules/{skill}",
        project_only=False,
        detect_dir=".custom",
    )
    dest = resolve_destination(sample_skill, target, Scope.USER)
    assert dest == fake_home / ".custom" / "rules" / "alpha-skill"


def test_project_only_target_project_scope(
    sample_skill: SkillInfo, project_only_target: CLITarget, fake_cwd: Path
) -> None:
    dest = resolve_destination(sample_skill, project_only_target, Scope.PROJECT)
    assert dest == fake_cwd / ".projonly" / "rules" / "alpha-skill"


def test_check_installed_true_when_skill_md_exists(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_home: Path
) -> None:
    dest = fake_home / ".testcli" / "skills" / "alpha-skill"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("installed", encoding="utf-8")
    assert check_installed(sample_skill, sample_target, Scope.USER) is True


def test_check_installed_false_when_dir_missing(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_home: Path
) -> None:
    assert check_installed(sample_skill, sample_target, Scope.USER) is False


def test_check_installed_false_when_dir_exists_but_no_skill_md(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_home: Path
) -> None:
    dest = fake_home / ".testcli" / "skills" / "alpha-skill"
    dest.mkdir(parents=True)
    assert check_installed(sample_skill, sample_target, Scope.USER) is False


def test_check_installed_project_scope(
    sample_skill: SkillInfo, sample_target: CLITarget, fake_cwd: Path
) -> None:
    dest = fake_cwd / ".testcli" / "skills" / "alpha-skill"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("installed", encoding="utf-8")
    assert check_installed(sample_skill, sample_target, Scope.PROJECT) is True
