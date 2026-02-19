"""Tests for bx_skills.core.parse_frontmatter."""

from __future__ import annotations

from pathlib import Path

import pytest

from bx_skills.core import parse_frontmatter

pytestmark = pytest.mark.os_agnostic


def test_bare_values_are_parsed(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: My Skill\ndescription: A great skill\n---\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "My Skill"
    assert desc == "A great skill"


def test_quoted_values_strip_quotes(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text('---\nname: "Quoted Name"\ndescription: "Quoted desc"\n---\n', encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "Quoted Name"
    assert desc == "Quoted desc"


def test_folded_block_scalar(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Test\ndescription: >\n  Line one\n  line two\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    assert desc == "Line one line two"


def test_folded_block_scalar_strip(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Test\ndescription: >-\n  Stripped line\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    assert desc == "Stripped line"


def test_literal_block_scalar(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Test\ndescription: |\n  Line one\n  line two\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    # Literal block scalar newlines are collapsed to spaces for descriptions
    assert desc == "Line one line two"


def test_literal_block_scalar_strip(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Test\ndescription: |-\n  Stripped line\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    assert desc == "Stripped line"


def test_missing_file_returns_fallback(tmp_path: Path) -> None:
    md = tmp_path / "my-skill" / "SKILL.md"
    md.parent.mkdir()
    name, desc = parse_frontmatter(md)
    assert name == "my-skill"
    assert desc == ""


def test_empty_file_returns_fallback(tmp_path: Path) -> None:
    md = tmp_path / "empty-skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "empty-skill"
    assert desc == ""


def test_no_opening_fence_returns_fallback(tmp_path: Path) -> None:
    md = tmp_path / "nofence" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("name: Test\ndescription: Oops\n---\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "nofence"
    assert desc == ""


def test_no_closing_fence_still_parses_fields(tmp_path: Path) -> None:
    md = tmp_path / "noclose" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Unclosed\ndescription: Still works\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "Unclosed"
    assert desc == "Still works"


def test_missing_name_falls_back_to_dir(tmp_path: Path) -> None:
    md = tmp_path / "dir-fallback" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\ndescription: Has desc only\n---\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "dir-fallback"
    assert desc == "Has desc only"


def test_missing_description_defaults_to_empty(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Only Name\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    assert desc == ""


def test_colon_in_value_preserved(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: My Skill\ndescription: Key: value pair inside\n---\n", encoding="utf-8")
    _, desc = parse_frontmatter(md)
    # partition(":") splits on FIRST colon only, so everything after "description:" is kept
    assert desc == "Key: value pair inside"


def test_colon_in_quoted_value_preserved(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text('---\nname: My Skill\ndescription: "Key: value pair inside"\n---\n', encoding="utf-8")
    _, desc = parse_frontmatter(md)
    assert desc == "Key: value pair inside"


def test_utf8_content_handled(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Ünïcödé Skïll\ndescription: Ëmöjis 🎉 and ñ\n---\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "Ünïcödé Skïll"
    assert "🎉" in desc


def test_extra_fields_ignored(tmp_path: Path) -> None:
    md = tmp_path / "skill" / "SKILL.md"
    md.parent.mkdir()
    md.write_text("---\nname: Test\nauthor: Someone\ndescription: Desc\nversion: 1.0\n---\n", encoding="utf-8")
    name, desc = parse_frontmatter(md)
    assert name == "Test"
    assert desc == "Desc"
