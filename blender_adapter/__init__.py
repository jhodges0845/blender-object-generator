# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender adapter entry point. Importing this package does not require Blender."""

import sys

from . import core_gateway as core

# Preserve the historical ``.core`` import path while the source file uses the
# clearer ``core_gateway.py`` name. This keeps internal/third-party imports
# working without keeping a misleading core.py file in the source tree.
sys.modules[__name__ + ".core"] = core

bl_info = {
    "name": "Asset Assistant",
    "author": "Asset Assistant contributors",
    "version": (0, 9, 0),
    "blender": (2, 92, 0),
    "location": "3D View > Sidebar > Asset Assistant",
    "description": "Generate, modify, rig, animate, validate, and export editable 3D assets",
    "category": "3D View",
}


def register():
    from . import (
        animation_names_ui,
        avian_ui,
        component_adoption_ui,
        component_modify_apply,
        component_modify_exchange,
        cura_scale_ui,
        modify_fastpath,
        modify_ui,
        run_ui,
        ui,
        ui_fastpath,
        workflow_ui,
        working_asset_ui,
    )
    # Keep stable class/operator IDs for compatibility while presenting one
    # ordered Asset Assistant workflow to artists.
    run_ui.prepare(ui)
    avian_ui.prepare(ui)
    workflow_ui.prepare(ui, modify_ui, animation_names_ui, working_asset_ui, component_adoption_ui)
    ui_fastpath.install(ui)
    modify_fastpath.install(modify_ui)
    component_modify_exchange.install(modify_ui)
    component_modify_apply.install(modify_ui)
    ui.register()
    animation_names_ui.register()
    run_ui.register(ui.HUMANOID_PG_settings)
    cura_scale_ui.register(ui.HUMANOID_PG_settings)
    modify_ui.register()
    working_asset_ui.register()
    component_adoption_ui.register()


def unregister():
    from . import (
        animation_names_ui,
        component_adoption_ui,
        cura_scale_ui,
        modify_ui,
        run_ui,
        ui,
        working_asset_ui,
    )
    component_adoption_ui.unregister()
    working_asset_ui.unregister()
    modify_ui.unregister()
    cura_scale_ui.unregister(ui.HUMANOID_PG_settings)
    run_ui.unregister(ui.HUMANOID_PG_settings)
    animation_names_ui.unregister()
    ui.unregister()
