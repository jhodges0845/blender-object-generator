# SPDX-License-Identifier: GPL-3.0-or-later
"""Visual identity for the four primary Asset Assistant workspaces.

Blender's standard UI API deliberately uses the active theme color for selected
buttons, so add-ons cannot safely assign an arbitrary background color per tab.
We keep the navigation Blender-native while making each workspace read like a
larger two-line card: centered icon above centered label, with a stronger active
state and more breathing room.
"""

_WORKSPACES = (
    ("CREATE", "Create", "USER"),
    ("ANIMATE", "Animate", "ACTION"),
    ("COMPONENTS", "Components", "CUBE"),
    ("EXPORT", "Export", "EXPORT"),
)


def _draw_workspace_nav(layout, settings):
    """Draw four large workspace cards with icons centered above their labels."""
    cards = layout.row(align=True)
    cards.scale_y = 1.0

    for key, label, icon in _WORKSPACES:
        card = cards.column(align=True)
        card.scale_x = 1.12

        icon_button = card.row(align=True)
        icon_button.scale_y = 1.9
        icon_button.prop_enum(
            settings,
            "asset_assistant_workspace",
            key,
            text="",
            icon=icon,
        )

        label_button = card.row(align=True)
        label_button.scale_y = 1.2
        label_button.prop_enum(
            settings,
            "asset_assistant_workspace",
            key,
            text=label,
        )


def install(workflow_ui):
    """Install the navigation renderer without coupling it to core asset logic."""
    workflow_ui._draw_workspace_nav = _draw_workspace_nav
