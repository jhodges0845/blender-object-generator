# SPDX-License-Identifier: GPL-3.0-or-later
"""Visual identity for the four primary Asset Assistant workspaces.

Blender's standard UI API deliberately uses the active theme color for selected
buttons, so add-ons cannot safely assign an arbitrary background color per tab.
Keep the navigation Blender-native, but make every workspace one cohesive control
so icon and label read as a single button instead of two stacked buttons.
"""

_WORKSPACES = (
    ("CREATE", "Create", "USER"),
    ("ANIMATE", "Animate", "ACTION"),
    ("COMPONENTS", "Components", "CUBE"),
    ("EXPORT", "Export", "EXPORT"),
)


def _draw_workspace_nav(layout, settings):
    """Draw four large single-piece workspace buttons with icon + label together."""
    row = layout.row(align=True)
    row.scale_y = 1.65

    for key, label, icon in _WORKSPACES:
        row.prop_enum(
            settings,
            "asset_assistant_workspace",
            key,
            text=label,
            icon=icon,
        )


def install(workflow_ui):
    """Install the navigation renderer without coupling it to core asset logic."""
    workflow_ui._draw_workspace_nav = _draw_workspace_nav
