"""Tests for screen navigation and validation in bx_skills.app."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from bx_skills.app import (
    ScopeScreen,
    SkillsInstallerApp,
    SkillsScreen,
    TargetsScreen,
)
from bx_skills.core import CLI_TARGETS, CLITarget, Scope, SkillAction, SkillInfo

pytestmark = pytest.mark.os_agnostic


def _make_skill(name: str, source: Path) -> SkillInfo:
    return SkillInfo(
        dir_name=name,
        name=name.replace("-", " ").title(),
        description=f"Desc {name}",
        source_path=source,
    )


# ── TargetsScreen ────────────────────────────────────────────────────────────


async def test_targets_screen_shows_all_cli_targets() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.push_screen(TargetsScreen())
        await pilot.pause()
        # The screen should have the selection list with all targets
        sel_list = app.screen.query_one("#targets-list")
        assert sel_list is not None


async def test_targets_screen_blocks_without_selection() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.push_screen(TargetsScreen())
        await pilot.pause()

        # Deselect all targets first
        sel_list = app.screen.query_one("#targets-list")
        for i in range(len(CLI_TARGETS)):
            sel_list.deselect(i)
        await pilot.pause()

        # Try to advance — should show error, not push new screen
        screen_before = app.screen
        await pilot.press("enter")
        await pilot.pause()
        error_label = app.screen.query_one("#targets-error")
        assert "visible" in error_label.classes
        assert app.screen is screen_before


# ── ScopeScreen ──────────────────────────────────────────────────────────────


async def test_scope_screen_windsurf_warning_shown() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        # Include a project_only target (Windsurf-like)
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
            CLITarget("Windsurf", "", ".windsurf/rules/{skill}", True, ".codeium/windsurf"),
        ]
        app.push_screen(ScopeScreen())
        await pilot.pause()
        warn = app.screen.query_one("#windsurf-warn")
        assert "visible" in warn.classes


async def test_scope_screen_blocks_user_only_with_all_project_only_targets() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("Windsurf", "", ".windsurf/rules/{skill}", True, ".codeium/windsurf"),
        ]
        app.push_screen(ScopeScreen())
        await pilot.pause()

        # Select only USER scope
        sel_list = app.screen.query_one("#scope-list")
        sel_list.select(0)      # USER
        sel_list.deselect(1)    # deselect PROJECT
        await pilot.pause()

        screen_before = app.screen
        await pilot.press("enter")
        await pilot.pause()
        error = app.screen.query_one("#scope-error")
        assert "visible" in error.classes
        assert app.screen is screen_before


async def test_scope_screen_blocks_without_selection() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(ScopeScreen())
        await pilot.pause()

        sel_list = app.screen.query_one("#scope-list")
        sel_list.deselect(0)
        sel_list.deselect(1)
        await pilot.pause()

        screen_before = app.screen
        await pilot.press("enter")
        await pilot.pause()
        error = app.screen.query_one("#scope-error")
        assert "visible" in error.classes
        assert app.screen is screen_before


# ── SkillsScreen ─────────────────────────────────────────────────────────────


async def test_skills_screen_defaults_new_to_skip(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("new-skill", Path("/fake/new-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.selected_scopes = [Scope.USER]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        from bx_skills.app import SkillItem

        items = list(app.screen.query(SkillItem))
        assert len(items) == 1
        assert items[0].action == SkillAction.SKIP


async def test_skills_screen_defaults_installed_to_update(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("inst-skill", Path("/fake/inst-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.selected_scopes = [Scope.USER]

        # Pre-install the skill
        dest = fake_home / ".test" / "skills" / "inst-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("installed", encoding="utf-8")

        app.push_screen(SkillsScreen())
        await pilot.pause()

        from bx_skills.app import SkillItem

        items = list(app.screen.query(SkillItem))
        assert len(items) == 1
        assert items[0].action == SkillAction.UPDATE


async def test_skills_screen_nothing_label_when_all_skip(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("new-skill", Path("/fake/new-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.selected_scopes = [Scope.USER]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        # All skills default to SKIP → pressing enter should show nothing label
        await pilot.press("enter")
        await pilot.pause()
        nothing = app.screen.query_one("#nothing-label")
        assert "visible" in nothing.classes


# ── Escape goes back ────────────────────────────────────────────────────────


async def test_escape_from_scope_returns_to_targets() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(TargetsScreen())
        await pilot.pause()
        app.push_screen(ScopeScreen())
        await pilot.pause()
        assert isinstance(app.screen, ScopeScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, TargetsScreen)
