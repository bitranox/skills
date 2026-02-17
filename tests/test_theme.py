"""Tests for bx_skills.theme constants."""

from __future__ import annotations

import re

import pytest

from bx_skills.theme import CATPPUCCIN_MOCHA, SUBTEXT0, SURFACE2, TEAL

pytestmark = pytest.mark.os_agnostic

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_theme_is_dark() -> None:
    assert CATPPUCCIN_MOCHA.dark is True


def test_theme_name() -> None:
    assert CATPPUCCIN_MOCHA.name == "catppuccin-mocha"


def test_extra_palette_constants_are_hex() -> None:
    for color in (SUBTEXT0, SURFACE2, TEAL):
        assert _HEX_RE.match(color), f"{color!r} is not a valid hex color"
