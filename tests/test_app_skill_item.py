"""Tests for bx_skills.app.SkillItem widget state machine."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.app import SkillItem, SkillsInstallerApp
from bx_skills.core import SkillAction, SkillInfo

pytestmark = pytest.mark.os_agnostic


def _make_skill(name: str = "test-skill") -> SkillInfo:
    return SkillInfo(
        dir_name=name,
        name=name.replace("-", " ").title(),
        description=f"Description for {name}",
        source_path=Path("/fake/catalog") / name,
    )


def _make_item(
    action: SkillAction = SkillAction.SKIP,
    *,
    is_installed: bool = False,
) -> SkillItem:
    return SkillItem(_make_skill(), action, is_installed=is_installed)


# ── toggle (Space key) ──────────────────────────────────────────────────────


async def test_toggle_skip_to_install() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.SKIP, is_installed=False)
        await pilot.app.mount(item)
        item.toggle()
        assert item.action == SkillAction.INSTALL


async def test_toggle_install_to_skip() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.INSTALL, is_installed=False)
        await pilot.app.mount(item)
        item.toggle()
        assert item.action == SkillAction.SKIP


async def test_toggle_update_to_keep() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.UPDATE, is_installed=True)
        await pilot.app.mount(item)
        item.toggle()
        assert item.action == SkillAction.KEEP


async def test_toggle_keep_to_update() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.KEEP, is_installed=True)
        await pilot.app.mount(item)
        item.toggle()
        assert item.action == SkillAction.UPDATE


async def test_toggle_uninstall_to_update() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.UNINSTALL, is_installed=True)
        await pilot.app.mount(item)
        item.toggle()
        assert item.action == SkillAction.UPDATE


# ── toggle_uninstall (d key) ────────────────────────────────────────────────


async def test_toggle_uninstall_from_update() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.UPDATE, is_installed=True)
        await pilot.app.mount(item)
        item.toggle_uninstall()
        assert item.action == SkillAction.UNINSTALL


async def test_toggle_uninstall_from_keep() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.KEEP, is_installed=True)
        await pilot.app.mount(item)
        item.toggle_uninstall()
        assert item.action == SkillAction.UNINSTALL


async def test_toggle_uninstall_reversal() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.UNINSTALL, is_installed=True)
        await pilot.app.mount(item)
        item.toggle_uninstall()
        assert item.action == SkillAction.KEEP


async def test_toggle_uninstall_noop_when_not_installed() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.SKIP, is_installed=False)
        await pilot.app.mount(item)
        item.toggle_uninstall()
        assert item.action == SkillAction.SKIP


# ── select_all / deselect_all ────────────────────────────────────────────────


async def test_select_all_new_skill_sets_install() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.SKIP, is_installed=False)
        await pilot.app.mount(item)
        item.select_all()
        assert item.action == SkillAction.INSTALL


async def test_select_all_installed_skill_sets_update() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.KEEP, is_installed=True)
        await pilot.app.mount(item)
        item.select_all()
        assert item.action == SkillAction.UPDATE


async def test_deselect_all_new_skill_sets_skip() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.INSTALL, is_installed=False)
        await pilot.app.mount(item)
        item.deselect_all()
        assert item.action == SkillAction.SKIP


async def test_deselect_all_installed_skill_sets_keep() -> None:
    async with SkillsInstallerApp().run_test() as pilot:
        item = _make_item(SkillAction.UPDATE, is_installed=True)
        await pilot.app.mount(item)
        item.deselect_all()
        assert item.action == SkillAction.KEEP
