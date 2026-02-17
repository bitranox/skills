"""Integration tests for multi-screen flows in bx_skills.app."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.app import (
    ConfirmScreen,
    ResultsScreen,
    ScopeScreen,
    SkillItem,
    SkillsInstallerApp,
    SkillsScreen,
    TargetsScreen,
)
from bx_skills.core import CLITarget, Scope, SkillAction, SkillInfo

pytestmark = [pytest.mark.os_agnostic, pytest.mark.integration]


def _make_skill(name: str, source: Path) -> SkillInfo:
    return SkillInfo(
        dir_name=name,
        name=name.replace("-", " ").title(),
        description=f"Desc {name}",
        source_path=source,
    )


async def test_full_install_flow(tmp_path: Path, fake_home: Path, fake_cwd: Path) -> None:
    """Walk through Targets → Scope → Skills → Confirm → Results for an install."""
    skill_dir = tmp_path / "src" / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: My Skill\n---\n", encoding="utf-8")

    target = CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test")

    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("my-skill", skill_dir)]

        # Screen 1: Targets
        app.push_screen(TargetsScreen())
        await pilot.pause()
        sel_list = app.screen.query_one("#targets-list")
        sel_list.select(0)
        await pilot.pause()
        app.selected_targets = [target]
        app.push_screen(ScopeScreen())
        await pilot.pause()

        # Screen 2: Scope — select USER
        scope_list = app.screen.query_one("#scope-list")
        scope_list.select(0)
        scope_list.deselect(1)
        await pilot.pause()
        app.selected_scopes = [Scope.USER]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        # Screen 3: Skills — toggle first skill to INSTALL
        items = list(app.screen.query(SkillItem))
        assert len(items) == 1
        items[0].toggle()  # SKIP → INSTALL
        assert items[0].action == SkillAction.INSTALL

        # Collect actions and advance
        app.skill_actions = {items[0].skill.dir_name: items[0].action}
        app.push_screen(ConfirmScreen())
        await pilot.pause()

        # Screen 4: Confirm — verify plans exist
        assert isinstance(app.screen, ConfirmScreen)
        assert len(app._plans) > 0

        # Screen 5: Results — execute
        app.push_screen(ResultsScreen())
        await pilot.pause()
        # Give the worker time to complete
        await pilot.pause(delay=0.5)
        assert isinstance(app.screen, ResultsScreen)

        # Verify the skill was actually installed
        installed = fake_home / ".test" / "skills" / "my-skill" / "SKILL.md"
        assert installed.is_file()


async def test_full_uninstall_flow(tmp_path: Path, fake_home: Path, fake_cwd: Path) -> None:
    """Walk through to uninstall a previously installed skill."""
    skill_dir = tmp_path / "src" / "old-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: Old Skill\n---\n", encoding="utf-8")

    target = CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test")

    # Pre-install the skill
    installed_dir = fake_home / ".test" / "skills" / "old-skill"
    installed_dir.mkdir(parents=True)
    (installed_dir / "SKILL.md").write_text("installed", encoding="utf-8")

    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("old-skill", skill_dir)]
        app.selected_targets = [target]
        app.selected_scopes = [Scope.USER]

        app.push_screen(SkillsScreen())
        await pilot.pause()

        # The installed skill defaults to UPDATE; toggle to UNINSTALL
        items = list(app.screen.query(SkillItem))
        assert items[0].action == SkillAction.UPDATE
        items[0].toggle_uninstall()
        assert items[0].action == SkillAction.UNINSTALL

        app.skill_actions = {items[0].skill.dir_name: items[0].action}
        app.push_screen(ConfirmScreen())
        await pilot.pause()
        app.push_screen(ResultsScreen())
        await pilot.pause()
        await pilot.pause(delay=0.5)

        # Verify uninstalled
        assert not installed_dir.exists()


async def test_quit_from_targets_screen() -> None:
    """Pressing q on the first screen exits the app."""
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [
            SkillInfo("s", "S", "desc", Path("/fake")),
        ]
        app.push_screen(TargetsScreen())
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()
        # After quit the app should be exiting — screen stack is unwound
        # The app.return_code is set or the app is no longer running
