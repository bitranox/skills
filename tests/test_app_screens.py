"""Tests for screen navigation and validation in bx_skills.app."""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.app import (
    CellState,
    ConfirmScreen,
    HelpScreen,
    SkillsInstallerApp,
    SkillsScreen,
    TargetsScreen,
)
from bx_skills.core import CLITarget, Scope, SkillAction, SkillInfo

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


async def test_targets_screen_blocks_without_selection(fake_home: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.push_screen(TargetsScreen())
        await pilot.pause()

        # Deselect all targets (fake_home has no detect_dirs, so none auto-selected)
        sel_list = app.screen.query_one("#targets-list")
        sel_list.deselect_all()
        await pilot.pause()

        # Call action_next directly (Enter on SelectionList toggles the highlight first)
        screen_before = app.screen
        app.screen.action_next()
        await pilot.pause()
        error_label = app.screen.query_one("#targets-error")
        assert "visible" in error_label.classes
        assert app.screen is screen_before


# ── SkillsScreen ─────────────────────────────────────────────────────────────


async def test_new_skill_blank_by_default(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("new-skill", Path("/fake/new-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        assert screen._states[("new-skill", Scope.USER)] == CellState.SKIP
        assert screen._states[("new-skill", Scope.PROJECT)] == CellState.SKIP


async def test_installed_skill_x_by_default(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("inst-skill", Path("/fake/inst-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]

        # Pre-install the skill at user scope
        dest = fake_home / ".test" / "skills" / "inst-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("installed", encoding="utf-8")

        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        assert screen._states[("inst-skill", Scope.USER)] == CellState.SELECT


async def test_new_skill_cycles_blank_x_blank(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("new-skill", Path("/fake/new-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        table = screen.query_one("#skills-table")

        # Position cursor on User column (row 0, col 1)
        from textual.coordinate import Coordinate

        table.cursor_coordinate = Coordinate(0, 1)
        await pilot.pause()

        assert screen._states[("new-skill", Scope.USER)] == CellState.SKIP  # blank

        screen.action_toggle_cell()
        await pilot.pause()
        assert screen._states[("new-skill", Scope.USER)] == CellState.SELECT  # X

        screen.action_toggle_cell()
        await pilot.pause()
        assert screen._states[("new-skill", Scope.USER)] == CellState.SKIP  # blank again


async def test_installed_skill_cycles_x_dash_d_x(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("inst-skill", Path("/fake/inst-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]

        dest = fake_home / ".test" / "skills" / "inst-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("installed", encoding="utf-8")

        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        table = screen.query_one("#skills-table")

        from textual.coordinate import Coordinate

        table.cursor_coordinate = Coordinate(0, 1)
        await pilot.pause()

        assert screen._states[("inst-skill", Scope.USER)] == CellState.SELECT  # X (default)

        screen.action_toggle_cell()
        await pilot.pause()
        assert screen._states[("inst-skill", Scope.USER)] == CellState.KEEP  # -

        screen.action_toggle_cell()
        await pilot.pause()
        assert screen._states[("inst-skill", Scope.USER)] == CellState.DELETE  # D

        screen.action_toggle_cell()
        await pilot.pause()
        assert screen._states[("inst-skill", Scope.USER)] == CellState.SELECT  # X again


async def test_select_all_sets_x(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [
            _make_skill("s1", Path("/fake/s1")),
            _make_skill("s2", Path("/fake/s2")),
        ]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        screen.action_select_all()
        await pilot.pause()

        assert screen._states[("s1", Scope.USER)] == CellState.SELECT
        assert screen._states[("s1", Scope.PROJECT)] == CellState.SELECT
        assert screen._states[("s2", Scope.USER)] == CellState.SELECT
        assert screen._states[("s2", Scope.PROJECT)] == CellState.SELECT


async def test_deselect_all_resets_defaults(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("inst-skill", Path("/fake/inst-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]

        # Pre-install at user scope
        dest = fake_home / ".test" / "skills" / "inst-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("installed", encoding="utf-8")

        app.push_screen(SkillsScreen())
        await pilot.pause()

        screen = app.screen
        # First select all, then deselect all → installed goes to KEEP, not-installed goes to SKIP
        screen.action_select_all()
        await pilot.pause()
        screen.action_deselect_all()
        await pilot.pause()

        assert screen._states[("inst-skill", Scope.USER)] == CellState.KEEP  # installed → KEEP
        assert screen._states[("inst-skill", Scope.PROJECT)] == CellState.SKIP  # not installed → SKIP


async def test_nothing_label_when_no_actionable(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("new-skill", Path("/fake/new-skill"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        # All new skills default to SKIP → action_next should show nothing label
        app.screen.action_next()
        await pilot.pause()
        nothing = app.screen.query_one("#nothing-label")
        assert "visible" in nothing.classes


async def test_advances_with_actionable(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app.push_screen(SkillsScreen())
        await pilot.pause()

        # Select all to mark for install
        app.screen.action_select_all()
        await pilot.pause()

        app.screen.action_next()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)


async def test_go_back_pops_to_targets(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        # Push TargetsScreen first, then SkillsScreen on top (ScopeScreen removed from flow)
        app.push_screen(TargetsScreen())
        await pilot.pause()
        app.push_screen(SkillsScreen())
        await pilot.pause()
        assert isinstance(app.screen, SkillsScreen)

        app.screen.action_go_back()
        await pilot.pause()
        assert isinstance(app.screen, TargetsScreen)


# ── HelpScreen ──────────────────────────────────────────────────────────────


async def test_help_screen_opens_and_closes() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.push_screen(TargetsScreen())
        await pilot.pause()

        app.screen.action_help()
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, TargetsScreen)


# ── ConfirmScreen ───────────────────────────────────────────────────────────


async def test_confirm_screen_shows_plans(fake_home: Path, fake_cwd: Path) -> None:
    skill_dir = fake_home / "src" / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: My Skill\n---\n", encoding="utf-8")

    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("my-skill", skill_dir)]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        # Build plans directly (SkillsScreen.action_next normally does this)
        from bx_skills.core import build_plans

        app._plans = build_plans(
            app.skills,
            {"my-skill": SkillAction.INSTALL},
            app.selected_targets,
            [Scope.USER],
        )
        app.push_screen(ConfirmScreen())
        await pilot.pause()

        assert isinstance(app.screen, ConfirmScreen)
        assert len(app._plans) > 0


async def test_confirm_screen_go_back(fake_home: Path, fake_cwd: Path) -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        app = pilot.app
        app.skills = [_make_skill("s1", Path("/fake/s1"))]
        app.selected_targets = [
            CLITarget("TestCLI", ".test/skills/{skill}", ".test/skills/{skill}", False, ".test"),
        ]
        app._plans = []  # empty plans for go-back test

        app.push_screen(SkillsScreen())
        await pilot.pause()
        app.push_screen(ConfirmScreen())
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)

        app.screen.action_go_back()
        await pilot.pause()
        assert isinstance(app.screen, SkillsScreen)
