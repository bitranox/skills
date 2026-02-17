"""Dark theme for the Skills Installer TUI."""

from __future__ import annotations

from textual.theme import Theme

CATPPUCCIN_MOCHA = Theme(
    name="catppuccin-mocha",
    primary="#5fafff",
    secondary="#af87ff",
    accent="#ffaf5f",
    foreground="#d0d0d0",
    background="#000000",
    success="#5fff87",
    warning="#ffaf5f",
    error="#ff5f87",
    surface="#1a1a1a",
    panel="#0d0d0d",
    dark=True,
    variables={
        "block-cursor-background": "#333333",
        "block-cursor-foreground": "#e0e0e0",
        "block-cursor-text-style": "bold",
        "block-cursor-blurred-background": "#1a1a1a",
        "block-cursor-blurred-foreground": "#d0d0d0",
        "block-cursor-blurred-text-style": "none",
    },
)

# Extra palette constants for CSS / Rich markup
SUBTEXT0 = "#808080"
SURFACE1 = "#333333"
SURFACE2 = "#4a4a4a"
TEAL = "#5fffaf"
