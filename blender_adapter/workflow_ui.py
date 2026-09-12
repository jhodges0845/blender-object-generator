# SPDX-License-Identifier: GPL-3.0-or-later
"""Present Asset Assistant as one ordered Blender sidebar workflow.

This module only changes artist-facing panel placement/labels. Stable panel and
operator identifiers remain untouched for saved files and scripts.
"""


_CATEGORY = "Asset Assistant"


def prepare(ui, modify_ui, animation_names_ui):
    """Place workflow panels under one ordered Asset Assistant sidebar tab."""
    panels = (
        (ui.HUMANOID_PT_panel, "Generate", 0),
        (modify_ui.ASSET_ASSISTANT_PT_modify, "Modify", 1),
        (ui.HUMANOID_PT_rigging, "Rig", 2),
        (ui.HUMANOID_PT_animations, "Animate", 3),
        (ui.HUMANOID_PT_validation, "Validate", 4),
        (ui.HUMANOID_PT_export, "Export", 5),
    )
    for panel, label, order in panels:
        panel.bl_label = label
        panel.bl_category = _CATEGORY
        panel.bl_order = order

    # This remains a child of Animate, but keep its declared category aligned so
    # Blender never exposes a stray legacy Animations tab.
    animation_names_ui.ASSET_ASSISTANT_PT_animation_names.bl_category = _CATEGORY

    # Keep the visible generation stage terminology consistent with the six-step
    # workflow even though the saved enum identifiers remain legacy-compatible.
    ui.HUMANOID_PG_settings.__annotations__["workflow_tab"].keywords["items"] = [
        ("MODEL", "Generate", "Create a new asset"),
        ("RIGGING", "Rig", "Rig an existing generated asset"),
        ("ANIMATION", "Animate", "Create or select generated animation clips"),
        ("VALIDATION", "Validate", "Check the selected asset"),
        ("EXPORT", "Export", "Export the selected asset"),
    ]
