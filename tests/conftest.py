"""Shared fixtures for bx_skills tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from bx_skills.core import CLITarget, SkillInfo


@pytest.fixture()
def cli_runner() -> CliRunner:
    """Click CliRunner for CLI tests."""
    return CliRunner()


@pytest.fixture()
def sample_target() -> CLITarget:
    """A typical CLI target supporting both user and project scope."""
    return CLITarget(
        name="TestCLI",
        user_path_tpl=".testcli/skills/{skill}",
        project_path_tpl=".testcli/skills/{skill}",
        project_only=False,
        detect_dir=".testcli",
    )


@pytest.fixture()
def project_only_target() -> CLITarget:
    """A CLI target that only supports project-level installation (like Windsurf)."""
    return CLITarget(
        name="ProjectOnlyCLI",
        user_path_tpl="",
        project_path_tpl=".projonly/rules/{skill}",
        project_only=True,
        detect_dir=".projonly",
    )


@pytest.fixture()
def sample_skill(tmp_path: Path) -> SkillInfo:
    """A SkillInfo backed by a real temp directory with SKILL.md."""
    skill_dir = tmp_path / "catalog" / "alpha-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: Alpha Skill\ndescription: First test skill\n---\n# Alpha\n",
        encoding="utf-8",
    )
    (skill_dir / "extra.md").write_text("extra content", encoding="utf-8")
    return SkillInfo(
        dir_name="alpha-skill",
        name="Alpha Skill",
        description="First test skill",
        source_path=skill_dir,
    )


@pytest.fixture()
def second_skill(tmp_path: Path) -> SkillInfo:
    """A second SkillInfo for multi-skill tests."""
    skill_dir = tmp_path / "catalog" / "beta-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: Beta Skill\ndescription: Second test skill\n---\n# Beta\n",
        encoding="utf-8",
    )
    return SkillInfo(
        dir_name="beta-skill",
        name="Beta Skill",
        description="Second test skill",
        source_path=skill_dir,
    )


@pytest.fixture()
def catalog_dir(tmp_path: Path) -> Path:
    """A temp catalog with 2 skill dirs, a hidden dir, and a regular file."""
    cat = tmp_path / "catalog"
    cat.mkdir()

    # Two valid skills
    for name in ("bravo-skill", "alpha-skill"):
        d = cat / name
        d.mkdir()
        (d / "SKILL.md").write_text(
            f"---\nname: {name.title().replace('-', ' ')}\ndescription: Desc for {name}\n---\n",
            encoding="utf-8",
        )

    # Hidden directory — should be skipped
    hidden = cat / ".hidden-dir"
    hidden.mkdir()
    (hidden / "SKILL.md").write_text("---\nname: Hidden\n---\n", encoding="utf-8")

    # Regular file — should be skipped
    (cat / "README.md").write_text("catalog readme", encoding="utf-8")

    return cat


@pytest.fixture()
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect Path.home() to a temp directory."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    return home


@pytest.fixture()
def fake_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect Path.cwd() to a temp directory."""
    cwd = tmp_path / "project"
    cwd.mkdir()
    monkeypatch.setattr(Path, "cwd", staticmethod(lambda: cwd))
    return cwd
