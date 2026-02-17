"""Comprehensive tests for the rich-click CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from bx_skills.cli import cli


@pytest.fixture(autouse=True)
def _patch_catalog(catalog_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point all CLI commands at the temp catalog."""
    monkeypatch.setattr("bx_skills.core.CATALOG_DIR", catalog_dir)
    monkeypatch.setattr("bx_skills.cli.CATALOG_DIR", catalog_dir)


# ── Root group ───────────────────────────────────────────────────────────────


class TestRootGroup:
    def test_no_subcommand_shows_help(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "install" in result.output
        assert "uninstall" in result.output

    def test_version(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "bx-skills" in result.output

    def test_help_shows_command_groups(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "install" in result.output
        assert "list" in result.output
        assert "tui" in result.output


# ── install ──────────────────────────────────────────────────────────────────


class TestInstall:
    def test_no_args_fails(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["install"])
        assert result.exit_code != 0

    def test_all_and_names_fails(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["install", "--all", "alpha-skill"])
        assert result.exit_code != 0

    def test_unknown_skill_fails(self, cli_runner: CliRunner, fake_home: Path) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["install", "nonexistent-skill"])
        assert result.exit_code != 0
        assert "Unknown skill" in result.stderr

    def test_all_with_auto_detect(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
        fake_cwd: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["install", "--all"])
        assert result.exit_code == 0
        assert "installed" in result.output

    def test_specific_skills(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["install", "alpha-skill"])
        assert result.exit_code == 0
        assert "alpha-skill" in result.output

    def test_specific_target(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        result = cli_runner.invoke(cli, ["install", "--all", "--target", "claude-code"])
        assert result.exit_code == 0

    def test_both_scopes(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
        fake_cwd: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["install", "--all", "--scope", "both"])
        assert result.exit_code == 0
        assert "user" in result.output
        assert "project" in result.output

    def test_quiet_flag(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["install", "--all", "-q"])
        assert result.exit_code == 0
        # quiet mode should produce no normal output
        assert result.output == ""


# ── uninstall ────────────────────────────────────────────────────────────────


class TestUninstall:
    def test_no_args_fails(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["uninstall"])
        assert result.exit_code != 0

    def test_confirmation_prompt(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        # Install first so there's something to uninstall
        (fake_home / ".claude").mkdir()
        cli_runner.invoke(cli, ["install", "--all", "-q"])
        result = cli_runner.invoke(cli, ["uninstall", "--all"], input="y\n")
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_abort_on_no(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        cli_runner.invoke(cli, ["install", "--all", "-q"])
        result = cli_runner.invoke(cli, ["uninstall", "--all"], input="n\n")
        assert result.exit_code == 0
        assert "Aborted" in result.output

    def test_yes_skips_prompt(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        cli_runner.invoke(cli, ["install", "--all", "-q"])
        result = cli_runner.invoke(cli, ["uninstall", "--all", "-y"])
        assert result.exit_code == 0

    def test_noop_when_not_installed(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["uninstall", "alpha-skill", "-y"])
        assert result.exit_code == 0
        assert "Nothing to uninstall" in result.output

    def test_all_yes(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        cli_runner.invoke(cli, ["install", "--all", "-q"])
        result = cli_runner.invoke(cli, ["uninstall", "--all", "-y"])
        assert result.exit_code == 0


# ── list ─────────────────────────────────────────────────────────────────────


class TestList:
    def test_normal_table(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "alpha-skill" in result.output
        assert "bravo-skill" in result.output

    def test_quiet_one_per_line(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["list", "-q"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        assert len(lines) == 2
        assert "alpha-skill" in lines
        assert "bravo-skill" in lines


# ── status ───────────────────────────────────────────────────────────────────


class TestStatus:
    def test_shows_installed_markers(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        cli_runner.invoke(cli, ["install", "alpha-skill", "-q"])
        result = cli_runner.invoke(cli, ["status", "--target", "claude-code", "--scope", "user"])
        assert result.exit_code == 0
        assert "installed" in result.output

    def test_shows_missing(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["status", "--target", "claude-code", "--scope", "user"])
        assert result.exit_code == 0
        assert "--" in result.output

    def test_quiet_mode(
        self,
        cli_runner: CliRunner,
        fake_home: Path,
    ) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["status", "-q", "--target", "claude-code", "--scope", "user"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        assert len(lines) >= 2
        for line in lines:
            assert "\t" in line


# ── info ─────────────────────────────────────────────────────────────────────


class TestInfo:
    def test_shows_version(self, cli_runner: CliRunner, fake_home: Path) -> None:
        result = cli_runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert "version" in result.output

    def test_shows_detected_clis(self, cli_runner: CliRunner, fake_home: Path) -> None:
        (fake_home / ".claude").mkdir()
        result = cli_runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert "claude-code" in result.output


# ── tui ──────────────────────────────────────────────────────────────────────


class TestTui:
    def test_tui_help(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli, ["tui", "--help"])
        assert result.exit_code == 0
        assert "TUI" in result.output or "tui" in result.output.lower()
