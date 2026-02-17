"""Textual TUI application for installing AI coding assistant skills."""

from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Label,
    ListItem,
    ListView,
    RichLog,
    SelectionList,
    Static,
)
from textual.widgets.selection_list import Selection
from textual.worker import get_current_worker

from bx_skills.core import (
    CLI_TARGETS,
    CLITarget,
    InstallPlan,
    Scope,
    SkillAction,
    SkillInfo,
    build_plans,
    check_installed,
    discover_skills,
    get_active_targets,
    install_skill,
    resolve_destination,
    uninstall_skill,
)
from bx_skills.theme import CATPPUCCIN_MOCHA, SUBTEXT0, SURFACE1, SURFACE2, TEAL

# ── CSS ───────────────────────────────────────────────────────────────────────

APP_CSS = """\
Screen {
    background: $background;
}

.screen-title {
    dock: top;
    width: 100%;
    text-align: center;
    padding: 1 0;
    text-style: bold;
    color: $primary;
    background: $panel;
}

.screen-subtitle {
    dock: top;
    width: 100%;
    text-align: center;
    padding: 0 0 1 0;
    color: """ + SUBTEXT0 + """;
    background: $panel;
}

.screen-body {
    padding: 1 2;
}

.error-label {
    color: $error;
    text-style: bold;
    padding: 1 2;
    display: none;
}

.error-label.visible {
    display: block;
}

.windsurf-warning {
    color: $warning;
    padding: 0 2 1 2;
    display: none;
}

.windsurf-warning.visible {
    display: block;
}

.nothing-label {
    color: $warning;
    text-style: bold;
    padding: 1 2;
    display: none;
}

.nothing-label.visible {
    display: block;
}

.button-bar {
    dock: bottom;
    height: 3;
    padding: 0 2;
    align: center middle;
}

.button-bar Button {
    margin: 0 1;
}

SkillItem {
    height: auto;
    padding: 0 1;
}

SkillItem .skill-row {
    height: auto;
}

SkillItem .skill-prefix {
    width: 6;
    min-width: 6;
}

SkillItem .skill-name {
    width: 1fr;
}

SkillItem .skill-tag {
    width: auto;
    min-width: 14;
    text-align: right;
}

SkillItem .skill-desc {
    padding-left: 6;
    color: """ + SUBTEXT0 + """;
}

SkillItem.action-install .skill-prefix {
    color: $primary;
}

SkillItem.action-install .skill-name {
    color: $primary;
}

SkillItem.action-install .skill-tag {
    color: $primary;
}

SkillItem.action-update .skill-prefix {
    color: $primary;
}

SkillItem.action-update .skill-name {
    color: $primary;
}

SkillItem.action-update .skill-tag {
    color: $primary;
}

SkillItem.action-keep .skill-prefix {
    color: $success 60%;
}

SkillItem.action-keep .skill-name {
    color: $success 60%;
}

SkillItem.action-keep .skill-tag {
    color: $success 60%;
}

SkillItem.action-skip .skill-prefix {
    color: """ + SURFACE2 + """;
}

SkillItem.action-skip .skill-name {
    color: """ + SURFACE2 + """;
}

SkillItem.action-skip .skill-tag {
    color: """ + SURFACE2 + """;
}

SkillItem.action-uninstall .skill-prefix {
    color: $error;
}

SkillItem.action-uninstall .skill-name {
    color: $error;
}

SkillItem.action-uninstall .skill-tag {
    color: $error;
}

HelpScreen {
    align: center middle;
}

HelpScreen .help-container {
    width: 72;
    max-height: 80%;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

HelpScreen .help-title {
    text-align: center;
    text-style: bold;
    color: $primary;
    padding-bottom: 1;
}

HelpScreen .help-body {
    color: $foreground;
}

RichLog {
    padding: 1 2;
}

.summary-line {
    dock: bottom;
    height: 1;
    padding: 0 2;
    text-style: bold;
    color: """ + TEAL + """;
    background: $panel;
}
"""


# ── HelpScreen ────────────────────────────────────────────────────────────────

HELP_TEXT = """\
[bold]Navigation[/bold]
  Enter       Next step
  Escape      Previous step / close help
  q           Quit

[bold]Targets & Scope[/bold]
  Multiple CLIs and scopes can be selected simultaneously.
  Detected CLIs are pre-selected based on ~/.<cli-dir>/ existence.

[bold]Skills Screen[/bold]
  Space       Toggle: install <-> skip (new) or update <-> keep (installed)
  d           Toggle uninstall for installed skills
  a           Select all for install/update
  n           Deselect all (reset to skip/keep)

[bold]Defaults[/bold]
  Installed skills default to UPDATE (will overwrite with latest).
  Deselected installed skills are KEPT (no changes).
  Not-installed skills default to SKIP.
  Uninstall removes from ALL selected scopes where present.
"""


class HelpScreen(ModalScreen[None]):
    """Modal help overlay."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("question_mark", "dismiss", "Close", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="help-container"):
            yield Static("Skills Installer \u2014 Help", classes="help-title")
            yield Static(HELP_TEXT, classes="help-body")


# ── SkillItem widget ──────────────────────────────────────────────────────────

_ACTION_DISPLAY: dict[SkillAction, tuple[str, str, str]] = {
    SkillAction.INSTALL:   ("[+]", "(new)",       "action-install"),
    SkillAction.UPDATE:    ("[+]", "(update)",    "action-update"),
    SkillAction.KEEP:      ("[ ]", "(installed)", "action-keep"),
    SkillAction.SKIP:      ("[ ]", "",            "action-skip"),
    SkillAction.UNINSTALL: ("[-]", "(UNINSTALL)", "action-uninstall"),
}


class SkillItem(ListItem):
    """A two-line list item representing a skill with its current action."""

    def __init__(
        self,
        skill: SkillInfo,
        action: SkillAction,
        is_installed: bool,
    ) -> None:
        super().__init__()
        self.skill = skill
        self.action = action
        self.is_installed = is_installed

    def compose(self) -> ComposeResult:
        prefix, tag, css_class = _ACTION_DISPLAY[self.action]
        self.add_class(css_class)
        with Vertical():
            with Horizontal(classes="skill-row"):
                yield Static(prefix, classes="skill-prefix")
                yield Static(self.skill.name, classes="skill-name")
                yield Static(tag, classes="skill-tag")
            yield Static(self.skill.description, classes="skill-desc")

    def _update_display(self) -> None:
        """Update prefix, tag, and CSS class from current action."""
        prefix, tag, new_class = _ACTION_DISPLAY[self.action]
        self.query_one(".skill-prefix", Static).update(prefix)
        self.query_one(".skill-tag", Static).update(tag)
        # Swap CSS classes
        for cls in ("action-install", "action-update", "action-keep",
                     "action-skip", "action-uninstall"):
            self.remove_class(cls)
        self.add_class(new_class)

    def toggle(self) -> None:
        """Space key: toggle install/skip or update/keep."""
        if self.action == SkillAction.SKIP:
            self.action = SkillAction.INSTALL
        elif self.action == SkillAction.INSTALL:
            self.action = SkillAction.SKIP
        elif self.action == SkillAction.UPDATE:
            self.action = SkillAction.KEEP
        elif self.action == SkillAction.KEEP:
            self.action = SkillAction.UPDATE
        elif self.action == SkillAction.UNINSTALL:
            self.action = SkillAction.UPDATE
        self._update_display()

    def toggle_uninstall(self) -> None:
        """d key: toggle uninstall for installed skills only."""
        if not self.is_installed:
            return
        if self.action == SkillAction.UNINSTALL:
            self.action = SkillAction.KEEP
        elif self.action in (SkillAction.UPDATE, SkillAction.KEEP):
            self.action = SkillAction.UNINSTALL
        self._update_display()

    def select_all(self) -> None:
        """Set to INSTALL (new) or UPDATE (installed)."""
        self.action = SkillAction.UPDATE if self.is_installed else SkillAction.INSTALL
        self._update_display()

    def deselect_all(self) -> None:
        """Set to SKIP (new) or KEEP (installed)."""
        self.action = SkillAction.KEEP if self.is_installed else SkillAction.SKIP
        self._update_display()


# ── Screen 1: TargetsScreen ──────────────────────────────────────────────────

class TargetsScreen(Screen):
    """Select which CLI tools to install skills for."""

    BINDINGS = [
        Binding("enter", "next", "Next"),
        Binding("escape", "quit_app", "Quit"),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Select Target CLIs", classes="screen-title")
        yield Static(
            "Choose which AI coding assistants to install skills for",
            classes="screen-subtitle",
        )

        selections: list[Selection[CLITarget]] = []
        for target in CLI_TARGETS:
            detected = (Path.home() / target.detect_dir).is_dir()
            path_display = target.project_path_tpl.rsplit("/{skill}", 1)[0] + "/"
            parts = [target.name, f" ({path_display})"]
            if detected:
                parts.append("  (detected)")
            if target.project_only:
                parts.append("  [project-level only]")
            label = "".join(parts)
            selections.append(Selection(label, target, detected))

        yield SelectionList[CLITarget](*selections, id="targets-list")
        yield Label("", classes="error-label", id="targets-error")
        yield Footer()

    def action_next(self) -> None:
        sel_list = self.query_one("#targets-list", SelectionList)
        selected = list(sel_list.selected)
        error_label = self.query_one("#targets-error", Label)
        if not selected:
            error_label.update("Select at least one target CLI.")
            error_label.add_class("visible")
            return
        error_label.remove_class("visible")
        self.app.selected_targets = selected  # type: ignore[attr-defined]
        self.app.push_screen(ScopeScreen())

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ── Screen 2: ScopeScreen ────────────────────────────────────────────────────

class ScopeScreen(Screen):
    """Select user-level and/or project-level scope."""

    BINDINGS = [
        Binding("enter", "next", "Next"),
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Select Installation Scope", classes="screen-title")
        yield Static(
            "Skills can be installed globally (user) and/or per-project",
            classes="screen-subtitle",
        )

        cwd = Path.cwd()
        yield SelectionList[Scope](
            Selection("User-level  (global, in ~/)", Scope.USER, True),
            Selection(
                f"Project-level  (current directory: {cwd})",
                Scope.PROJECT,
                False,
            ),
            id="scope-list",
        )

        yield Label(
            "\u26a0 Windsurf does not support user-level skills and will be skipped for that scope.",
            classes="windsurf-warning",
            id="windsurf-warn",
        )
        yield Label("", classes="error-label", id="scope-error")
        yield Footer()

    def on_mount(self) -> None:
        # Show Windsurf warning if Windsurf is among selected targets
        targets: list[CLITarget] = self.app.selected_targets  # type: ignore[attr-defined]
        has_windsurf = any(t.project_only for t in targets)
        if has_windsurf:
            self.query_one("#windsurf-warn", Label).add_class("visible")

    def action_next(self) -> None:
        sel_list = self.query_one("#scope-list", SelectionList)
        selected = list(sel_list.selected)
        error_label = self.query_one("#scope-error", Label)

        if not selected:
            error_label.update("Select at least one scope.")
            error_label.add_class("visible")
            return

        # Check: if all selected targets are project_only, USER-only is invalid
        targets: list[CLITarget] = self.app.selected_targets  # type: ignore[attr-defined]
        all_project_only = all(t.project_only for t in targets)
        if all_project_only and selected == [Scope.USER]:
            error_label.update(
                "All selected CLIs are project-level only. "
                "Select Project-level scope or add other CLI targets."
            )
            error_label.add_class("visible")
            return

        error_label.remove_class("visible")
        self.app.selected_scopes = selected  # type: ignore[attr-defined]
        self.app.push_screen(SkillsScreen())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ── Screen 3: SkillsScreen ───────────────────────────────────────────────────

class SkillsScreen(Screen):
    """Select skills and choose actions (install/update/keep/skip/uninstall)."""

    BINDINGS = [
        Binding("enter", "next", "Next"),
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("space", "toggle_skill", "Toggle", key_display="Space"),
        Binding("d", "uninstall_skill", "Uninstall", key_display="d"),
        Binding("a", "select_all", "All", key_display="a"),
        Binding("n", "deselect_all", "None", key_display="n"),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Select Skills", classes="screen-title")
        yield Static(
            "Space: toggle  |  d: uninstall  |  a: all  |  n: none",
            classes="screen-subtitle",
        )

        skills: list[SkillInfo] = self.app.skills  # type: ignore[attr-defined]
        targets: list[CLITarget] = self.app.selected_targets  # type: ignore[attr-defined]
        scopes: list[Scope] = self.app.selected_scopes  # type: ignore[attr-defined]
        active_pairs = get_active_targets(targets, scopes)

        items: list[SkillItem] = []
        for skill in skills:
            installed = any(
                check_installed(skill, t, s) for t, s in active_pairs
            )
            if installed:
                action = SkillAction.UPDATE
            else:
                action = SkillAction.SKIP
            items.append(SkillItem(skill, action, installed))

        yield ListView(*items, id="skills-list")
        yield Label("", classes="nothing-label", id="nothing-label")

        with Horizontal(classes="button-bar"):
            yield Button("Select All", id="btn-select-all", variant="default")
            yield Button("Deselect All", id="btn-deselect-all", variant="default")

        yield Footer()

    def _get_highlighted_item(self) -> SkillItem | None:
        lv = self.query_one("#skills-list", ListView)
        if lv.highlighted_child is not None:
            return lv.highlighted_child  # type: ignore[return-value]
        return None

    def _has_actionable(self) -> bool:
        """Check if any skill has an actionable state (not KEEP/SKIP)."""
        lv = self.query_one("#skills-list", ListView)
        for child in lv.children:
            if isinstance(child, SkillItem):
                if child.action not in (SkillAction.KEEP, SkillAction.SKIP):
                    return True
        return False

    def action_toggle_skill(self) -> None:
        item = self._get_highlighted_item()
        if item:
            item.toggle()
            self._update_nothing_label()

    def action_uninstall_skill(self) -> None:
        item = self._get_highlighted_item()
        if item:
            item.toggle_uninstall()
            self._update_nothing_label()

    def action_select_all(self) -> None:
        lv = self.query_one("#skills-list", ListView)
        for child in lv.children:
            if isinstance(child, SkillItem):
                child.select_all()
        self._update_nothing_label()

    def action_deselect_all(self) -> None:
        lv = self.query_one("#skills-list", ListView)
        for child in lv.children:
            if isinstance(child, SkillItem):
                child.deselect_all()
        self._update_nothing_label()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-select-all":
            self.action_select_all()
        elif event.button.id == "btn-deselect-all":
            self.action_deselect_all()

    def _update_nothing_label(self) -> None:
        label = self.query_one("#nothing-label", Label)
        if not self._has_actionable():
            label.update("Nothing to do \u2014 select skills to install, update, or uninstall.")
            label.add_class("visible")
        else:
            label.remove_class("visible")

    def action_next(self) -> None:
        if not self._has_actionable():
            self._update_nothing_label()
            return

        # Collect actions
        actions: dict[str, SkillAction] = {}
        lv = self.query_one("#skills-list", ListView)
        for child in lv.children:
            if isinstance(child, SkillItem):
                actions[child.skill.dir_name] = child.action

        self.app.skill_actions = actions  # type: ignore[attr-defined]
        self.app.push_screen(ConfirmScreen())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ── Screen 4: ConfirmScreen ──────────────────────────────────────────────────

class ConfirmScreen(Screen):
    """Review planned operations before executing."""

    BINDINGS = [
        Binding("enter", "execute", "Execute"),
        Binding("escape", "go_back", "Back"),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Confirm Operations", classes="screen-title")
        yield Static(
            "Review changes below. Enter to execute, Escape to go back.",
            classes="screen-subtitle",
        )

        log = RichLog(id="confirm-log", highlight=True, markup=True)
        yield log
        yield Static("", classes="summary-line", id="summary-line")
        yield Footer()

    def on_mount(self) -> None:
        skills: list[SkillInfo] = self.app.skills  # type: ignore[attr-defined]
        actions: dict[str, SkillAction] = self.app.skill_actions  # type: ignore[attr-defined]
        targets: list[CLITarget] = self.app.selected_targets  # type: ignore[attr-defined]
        scopes: list[Scope] = self.app.selected_scopes  # type: ignore[attr-defined]

        plans = build_plans(skills, actions, targets, scopes)
        self.app._plans = plans  # type: ignore[attr-defined]

        log = self.query_one("#confirm-log", RichLog)

        # Group by action type
        installs = [p for p in plans if p.action in (SkillAction.INSTALL, SkillAction.UPDATE)]
        uninstalls = [p for p in plans if p.action == SkillAction.UNINSTALL]

        # Count unchanged
        keep_count = sum(
            1 for a in actions.values()
            if a in (SkillAction.KEEP, SkillAction.SKIP)
        )

        if installs:
            log.write("[bold]Will Install/Update:[/bold]")
            log.write("\u2500" * 40)
            self._write_grouped(log, installs)
            log.write("")

        if uninstalls:
            log.write("[bold red]Will Uninstall:[/bold red]")
            log.write("\u2500" * 40)
            self._write_grouped(log, uninstalls)
            log.write("")

        if keep_count:
            log.write(f"Unchanged: {keep_count} skills kept/skipped")
            log.write("")

        summary = f"Summary: {len(installs)} install(s), {len(uninstalls)} uninstall(s), {keep_count} unchanged"
        self.query_one("#summary-line", Static).update(summary)

    def _write_grouped(self, log: RichLog, plans: list[InstallPlan]) -> None:
        """Write plans grouped by (target, scope)."""
        groups: dict[str, list[InstallPlan]] = {}
        for p in plans:
            scope_label = "User" if p.scope == Scope.USER else "Project"
            if p.scope == Scope.USER:
                base = "~/"
            else:
                base = str(Path.cwd()) + "/"
            tpl = p.target.user_path_tpl if p.scope == Scope.USER else p.target.project_path_tpl
            path_base = tpl.rsplit("/{skill}", 1)[0] + "/"
            key = f"{p.target.name} \u00b7 {scope_label} ({base}{path_base})"
            groups.setdefault(key, []).append(p)

        for group_key, group_plans in groups.items():
            log.write(f"  [bold]{group_key}[/bold]")
            for p in group_plans:
                if p.action == SkillAction.INSTALL:
                    log.write(f"    [blue]\\[+][/blue] {p.skill.dir_name}/  [blue](new)[/blue]")
                elif p.action == SkillAction.UPDATE:
                    log.write(f"    [blue]\\[+][/blue] {p.skill.dir_name}/  [blue](update)[/blue]")
                elif p.action == SkillAction.UNINSTALL:
                    log.write(f"    [red]\\[-][/red] {p.skill.dir_name}/")

    def action_execute(self) -> None:
        self.app.push_screen(ResultsScreen())

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ── Screen 5: ResultsScreen ──────────────────────────────────────────────────

class ResultsScreen(Screen):
    """Execute plans and show progressive results."""

    BINDINGS = [
        Binding("escape", "quit_app", "Quit"),
        Binding("q", "quit_app", "Quit", show=False),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Executing...", classes="screen-title", id="results-title")
        yield RichLog(id="results-log", highlight=True, markup=True)
        yield Static("", classes="summary-line", id="results-summary")
        yield Footer()

    def on_mount(self) -> None:
        self._execute_plans()

    @work(thread=True)
    def _execute_plans(self) -> None:
        worker = get_current_worker()
        plans: list[InstallPlan] = self.app._plans  # type: ignore[attr-defined]
        log = self.query_one("#results-log", RichLog)

        succeeded = 0
        failed = 0

        for plan in plans:
            if worker.is_cancelled:
                break

            scope_label = "User" if plan.scope == Scope.USER else "Project"
            desc = f"{plan.skill.dir_name} \u2192 {plan.target.name} \u00b7 {scope_label}"

            try:
                if plan.action == SkillAction.UNINSTALL:
                    uninstall_skill(plan)
                    self.call_from_thread(
                        log.write,
                        f"[green]\\[OK][/green] {desc} (uninstalled)",
                    )
                elif plan.action == SkillAction.INSTALL:
                    install_skill(plan)
                    self.call_from_thread(
                        log.write,
                        f"[green]\\[OK][/green] {desc} (installed)",
                    )
                else:  # UPDATE
                    install_skill(plan)
                    self.call_from_thread(
                        log.write,
                        f"[green]\\[OK][/green] {desc} (updated)",
                    )
                succeeded += 1
            except Exception as exc:
                failed += 1
                self.call_from_thread(
                    log.write,
                    f"[red]\\[!!][/red] {desc} - {exc}",
                )

        summary = f"{succeeded} succeeded, {failed} failed"
        self.call_from_thread(
            self.query_one("#results-title", Static).update,
            "Complete",
        )
        self.call_from_thread(
            self.query_one("#results-summary", Static).update,
            summary,
        )

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


# ── App ───────────────────────────────────────────────────────────────────────

class SkillsInstallerApp(App):
    """TUI for installing AI coding assistant skills."""

    TITLE = "Skills Installer"
    SUB_TITLE = "AI Coding Assistant Skills"
    CSS = APP_CSS

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
    ]

    # State — populated by screens
    skills: list[SkillInfo] = []
    selected_targets: list[CLITarget] = []
    selected_scopes: list[Scope] = []
    skill_actions: dict[str, SkillAction] = {}
    _plans: list[InstallPlan] = []

    def on_mount(self) -> None:
        self.register_theme(CATPPUCCIN_MOCHA)
        self.theme = "catppuccin-mocha"

        self.skills = discover_skills()
        if not self.skills:
            self.notify(
                "No skills found in catalog. Check your installation.",
                severity="error",
                timeout=5,
            )
            self.exit()
            return

        self.push_screen(TargetsScreen())


def main() -> None:
    """Entry point for the bx-skills CLI."""
    app = SkillsInstallerApp()
    app.run()


if __name__ == "__main__":
    main()
