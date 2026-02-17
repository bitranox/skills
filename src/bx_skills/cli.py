"""Rich-click CLI for bx_skills — install, update, and uninstall AI coding assistant skills."""

from __future__ import annotations

import sys

import rich_click as click
from rich.console import Console
from rich.table import Table

from bx_skills.__init__conf__ import version
from bx_skills.core import (
    CATALOG_DIR,
    CLI_TARGETS,
    CLITarget,
    Scope,
    SkillAction,
    build_plans,
    check_installed,
    detect_installed_targets,
    discover_skills,
    get_active_targets,
    get_all_target_slugs,
    get_target_slug,
    install_skill,
    resolve_skills_by_names,
    resolve_target_by_slug,
    uninstall_skill,
)

# ── Rich-click configuration ────────────────────────────────────────────────

click.rich_click.TEXT_MARKUP = "rich"
click.rich_click.COMMAND_GROUPS = {
    "bx-skills": [
        {"name": "Skill Management", "commands": ["install", "uninstall"]},
        {"name": "Information", "commands": ["list", "status", "info"]},
        {"name": "Interactive", "commands": ["tui"]},
    ]
}
click.rich_click.OPTION_GROUPS = {
    "bx-skills install": [
        {"name": "Selection", "options": ["skills", "--all"]},
        {"name": "Targeting", "options": ["--target", "--scope"]},
        {"name": "Output", "options": ["--quiet"]},
    ],
    "bx-skills uninstall": [
        {"name": "Selection", "options": ["skills", "--all"]},
        {"name": "Targeting", "options": ["--target", "--scope"]},
        {"name": "Confirmation", "options": ["--yes"]},
        {"name": "Output", "options": ["--quiet"]},
    ],
}


# ── Console helpers ──────────────────────────────────────────────────────────


def _out_console() -> Console:
    """Return a Console bound to the current stdout (works with CliRunner)."""
    return Console(file=sys.stdout, highlight=False)


def _err_console() -> Console:
    """Return a Console bound to the current stderr."""
    return Console(file=sys.stderr, highlight=False)


# ── Internal helpers ─────────────────────────────────────────────────────────

_ALL_SLUGS = get_all_target_slugs()


def _resolve_targets(raw: tuple[str, ...]) -> list[CLITarget]:
    """Convert --target values to CLITarget list."""
    if not raw or raw == ("auto",):
        detected = detect_installed_targets()
        if not detected:
            click.echo("Error: No supported CLIs detected. Use --target to specify.", err=True)
            sys.exit(1)
        return detected

    if "all" in raw:
        return list(CLI_TARGETS)

    targets: list[CLITarget] = []
    for slug in raw:
        t = resolve_target_by_slug(slug)
        if t is None:
            click.echo(f"Error: Unknown target: {slug}", err=True)
            sys.exit(1)
        if t not in targets:
            targets.append(t)
    return targets


def _resolve_scopes(scope: str) -> list[Scope]:
    """Convert --scope value to Scope list."""
    if scope == "both":
        return [Scope.USER, Scope.PROJECT]
    return [Scope(scope)]


# ── Root group ───────────────────────────────────────────────────────────────

_target_choices = ["auto", "all", *_ALL_SLUGS]


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version, prog_name="bx-skills")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """BX Skills — install AI coding assistant skills to Claude Code, Codex, Kilo Code, and Windsurf."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ── install ──────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("skills", nargs=-1)
@click.option("--all", "install_all", is_flag=True, default=False, help="Install/update all catalog skills.")
@click.option(
    "-t",
    "--target",
    "targets",
    multiple=True,
    default=("auto",),
    type=click.Choice(_target_choices, case_sensitive=False),
    help="Target CLI(s). Repeatable.",
)
@click.option(
    "-s",
    "--scope",
    default="user",
    type=click.Choice(["user", "project", "both"], case_sensitive=False),
    help="Installation scope.",
)
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress non-error output.")
def install(skills: tuple[str, ...], install_all: bool, targets: tuple[str, ...], scope: str, quiet: bool) -> None:
    """Install or update skills from the catalog."""
    if install_all and skills:
        click.echo("Error: Cannot combine --all with specific skill names.", err=True)
        sys.exit(1)
    if not install_all and not skills:
        click.echo("Error: Specify skill name(s) or use --all.", err=True)
        sys.exit(1)

    resolved_targets = _resolve_targets(targets)
    resolved_scopes = _resolve_scopes(scope)

    if install_all:
        skill_list = discover_skills()
    else:
        skill_list, missing = resolve_skills_by_names(list(skills))
        if missing:
            click.echo(f"Error: Unknown skill(s): {', '.join(missing)}", err=True)
            sys.exit(1)

    actions = {s.dir_name: SkillAction.INSTALL for s in skill_list}
    plans = build_plans(skill_list, actions, resolved_targets, resolved_scopes)

    succeeded = 0
    failed = 0
    for plan in plans:
        try:
            install_skill(plan)
            succeeded += 1
            if not quiet:
                scope_label = "user" if plan.scope == Scope.USER else "project"
                click.echo(f"OK {plan.skill.dir_name} -> {get_target_slug(plan.target)} ({scope_label})")
        except Exception as exc:
            failed += 1
            click.echo(f"FAIL {plan.skill.dir_name}: {exc}", err=True)

    if not quiet:
        click.echo(f"\n{succeeded} installed, {failed} failed.")

    if failed:
        sys.exit(1)


# ── uninstall ────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("skills", nargs=-1)
@click.option("--all", "uninstall_all", is_flag=True, default=False, help="Uninstall all installed skills.")
@click.option(
    "-t",
    "--target",
    "targets",
    multiple=True,
    default=("auto",),
    type=click.Choice(_target_choices, case_sensitive=False),
    help="Target CLI(s). Repeatable.",
)
@click.option(
    "-s",
    "--scope",
    default="user",
    type=click.Choice(["user", "project", "both"], case_sensitive=False),
    help="Uninstall scope.",
)
@click.option("-y", "--yes", is_flag=True, default=False, help="Skip confirmation prompt.")
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress non-error output.")
def uninstall(
    skills: tuple[str, ...],
    uninstall_all: bool,
    targets: tuple[str, ...],
    scope: str,
    yes: bool,
    quiet: bool,
) -> None:
    """Remove installed skills."""
    if uninstall_all and skills:
        click.echo("Error: Cannot combine --all with specific skill names.", err=True)
        sys.exit(1)
    if not uninstall_all and not skills:
        click.echo("Error: Specify skill name(s) or use --all.", err=True)
        sys.exit(1)

    resolved_targets = _resolve_targets(targets)
    resolved_scopes = _resolve_scopes(scope)

    if uninstall_all:
        skill_list = discover_skills()
    else:
        skill_list, missing = resolve_skills_by_names(list(skills))
        if missing:
            click.echo(f"Error: Unknown skill(s): {', '.join(missing)}", err=True)
            sys.exit(1)

    actions = {s.dir_name: SkillAction.UNINSTALL for s in skill_list}
    plans = build_plans(skill_list, actions, resolved_targets, resolved_scopes)

    if not plans:
        if not quiet:
            click.echo("Nothing to uninstall.")
        return

    if not yes:
        if not quiet:
            click.echo(f"Will uninstall {len(plans)} skill(s).")
        if not click.confirm("Proceed?"):
            click.echo("Aborted.")
            return

    succeeded = 0
    failed = 0
    for plan in plans:
        try:
            uninstall_skill(plan)
            succeeded += 1
            if not quiet:
                scope_label = "user" if plan.scope == Scope.USER else "project"
                click.echo(f"OK {plan.skill.dir_name} removed from {get_target_slug(plan.target)} ({scope_label})")
        except Exception as exc:
            failed += 1
            click.echo(f"FAIL {plan.skill.dir_name}: {exc}", err=True)

    if not quiet:
        click.echo(f"\n{succeeded} removed, {failed} failed.")

    if failed:
        sys.exit(1)


# ── list ─────────────────────────────────────────────────────────────────────


@cli.command("list")
@click.option("-q", "--quiet", is_flag=True, default=False, help="One name per line (machine-readable).")
def list_skills(quiet: bool) -> None:
    """List all available skills in the catalog."""
    skills = discover_skills()
    if not skills:
        click.echo("No skills found in catalog.", err=True)
        return

    if quiet:
        for s in skills:
            click.echo(s.dir_name)
        return

    table = Table(title="Available Skills", show_lines=False)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    for s in skills:
        table.add_row(s.dir_name, s.description)
    _out_console().print(table)


# ── status ───────────────────────────────────────────────────────────────────


@cli.command()
@click.option(
    "-t",
    "--target",
    "targets",
    multiple=True,
    default=("auto",),
    type=click.Choice(_target_choices, case_sensitive=False),
    help="Target CLI(s). Repeatable.",
)
@click.option(
    "-s",
    "--scope",
    default="both",
    type=click.Choice(["user", "project", "both"], case_sensitive=False),
    help="Scope to check.",
)
@click.option("-q", "--quiet", is_flag=True, default=False, help="Machine-readable output.")
def status(targets: tuple[str, ...], scope: str, quiet: bool) -> None:
    """Show installation status of skills across targets and scopes."""
    resolved_targets = _resolve_targets(targets)
    resolved_scopes = _resolve_scopes(scope)
    active = get_active_targets(resolved_targets, resolved_scopes)
    skills = discover_skills()

    if not skills:
        click.echo("No skills found in catalog.", err=True)
        return

    if quiet:
        for skill in skills:
            for target, sc in active:
                marker = "installed" if check_installed(skill, target, sc) else "missing"
                sc_label = sc.value
                click.echo(f"{skill.dir_name}\t{get_target_slug(target)}\t{sc_label}\t{marker}")
        return

    table = Table(title="Skill Status", show_lines=False)
    table.add_column("Skill", style="cyan", no_wrap=True)
    for target, sc in active:
        sc_label = "U" if sc == Scope.USER else "P"
        table.add_column(f"{get_target_slug(target)} ({sc_label})", justify="center")

    for skill in skills:
        row: list[str] = [skill.dir_name]
        for target, sc in active:
            row.append("[green]installed[/green]" if check_installed(skill, target, sc) else "--")
        table.add_row(*row)

    _out_console().print(table)


# ── info ─────────────────────────────────────────────────────────────────────


@cli.command()
def info() -> None:
    """Show version, metadata, and detected CLIs."""
    from bx_skills.__init__conf__ import author, homepage, name, title

    table = Table(title="bx-skills Info", show_lines=False)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_row("name", name)
    table.add_row("title", title)
    table.add_row("version", version)
    table.add_row("homepage", homepage or "(not set)")
    table.add_row("author", author)
    table.add_row("catalog_dir", str(CATALOG_DIR))
    table.add_row("skills_in_catalog", str(len(discover_skills())))

    detected = detect_installed_targets()
    detected_str = ", ".join(get_target_slug(t) for t in detected) if detected else "(none)"
    table.add_row("detected_clis", detected_str)

    _out_console().print(table)


# ── tui ──────────────────────────────────────────────────────────────────────


@cli.command()
def tui() -> None:
    """Launch the interactive TUI installer."""
    from bx_skills.app import SkillsInstallerApp

    app = SkillsInstallerApp()
    app.run()


# ── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point for the bx-skills console script."""
    cli()
