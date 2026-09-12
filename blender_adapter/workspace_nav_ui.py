# SPDX-License-Identifier: GPL-3.0-or-later
"""Visual identity for the four primary Asset Assistant workspaces.

Blender's standard UI API deliberately uses the active theme color for selected
buttons, so add-ons cannot safely assign arbitrary per-button background colors.
Keep the navigation Blender-native and compact, but give each workspace enough
physical size to read as a destination rather than a toolbar item.
"""

_WORKSPACES = (
    ("CREATE", "Create", "USER"),
    ("ANIMATE", "Animate", "ACTION"),
    ("COMPONENTS", "Components", "CUBE"),
    ("EXPORT", "Export", "EXPORT"),
)


def _draw_workspace_nav(layout, settings):
    """Draw four large workspace tiles in a two-by-two navigation grid.

    Each tile remains one native Blender enum button so the entire visible control
    is clickable and selected-state behavior stays theme-safe. Blender's native
    button layout keeps the icon beside the label rather than vertically stacking
    the two inside one hit target; the taller 2x2 treatment is the safest native
    approximation without introducing a custom-drawn interaction layer.
    """
    rows = (_WORKSPACES[:2], _WORKSPACES[2:])
    for entries in rows:
        row = layout.row(align=True)
        row.scale_y = 2.0
        for key, label, icon in entries:
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
