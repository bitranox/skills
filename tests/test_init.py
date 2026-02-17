"""Tests for bx_skills.__init__ and __init__conf__."""

from __future__ import annotations

import pytest

import bx_skills
from bx_skills import __init__conf__ as conf

pytestmark = pytest.mark.os_agnostic


def test_version_is_string() -> None:
    assert isinstance(bx_skills.__version__, str)
    assert len(bx_skills.__version__) > 0


def test_version_matches_conf() -> None:
    assert bx_skills.__version__ == conf.version


def test_print_info_outputs_package_name(capsys: pytest.CaptureFixture[str]) -> None:
    conf.print_info()
    captured = capsys.readouterr()
    assert "bx-skills" in captured.out
    assert "version" in captured.out
