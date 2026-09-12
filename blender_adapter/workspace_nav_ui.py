# SPDX-License-Identifier: GPL-3.0-or-later
"""Visual identity for the four primary Asset Assistant workspaces.

Blender's standard UI API deliberately uses the active theme color for selected
buttons, so add-ons cannot safely assign an arbitrary background color per tab.
We keep the navigation Blender-native while giving every workspace a distinct
icon and a stronger selected state. This preserves theme compatibility and all
existing workflow behavior.
"""

_WORKSPACES = (
    ("CREATE", "Create", "USER"),
    ("ANIMATE", "Animate", "ACTION"),
    ("COMPONENTS", "Components", "CUBE"),
    ("EXPORT", "Export", "EXPORT"),
)


def _draw_workspace_nav(layout, settings):
    """Draw the four workflow tabs with stable, recognizable iconography."""
    row = layout.row(align=True)
    row.scale_y = 1.55
    active = settings.asset_assistant_workspace
    for key, label, icon in _WORKSPACES:
        text = label if active != key else "  " + label
        row.prop_enum(
            settings,
            "asset_assistant_workspace",
            key,
            text=text,
            icon=icon,
        )


def install(workflow_ui):
    """Install the navigation renderer without coupling it to core asset logic."""
    workflow_ui._draw_workspace_nav = _draw_workspace_nav
