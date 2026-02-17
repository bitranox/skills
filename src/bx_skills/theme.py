"""Catppuccin Mocha theme for the Skills Installer TUI."""

from __future__ import annotations

from textual.theme import Theme

CATPPUCCIN_MOCHA = Theme(
    name="catppuccin-mocha",
    primary="#89b4fa",
    secondary="#cba6f7",
    accent="#f9e2af",
    foreground="#cdd6f4",
    background="#1e1e2e",
    success="#a6e3a1",
    warning="#fab387",
    error="#f38ba8",
    surface="#313244",
    panel="#181825",
    dark=True,
)

# Extra palette constants for CSS / Rich markup
SUBTEXT0 = "#a6adc8"
SURFACE1 = "#45475a"
SURFACE2 = "#585b70"
TEAL = "#94e2d5"
