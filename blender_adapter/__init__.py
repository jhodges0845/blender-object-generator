# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender adapter entry point. Importing this package does not require Blender."""

import sys

from . import core_gateway as core

sys.modules[__name__ + ".core"] = core

bl_info = {
    "name": "Asset Assistant",
    "author": "Asset Assistant contributors",
    "version": (0, 9, 0),
    "blender": (5, 2, 1),
    "location": "3D View > Sidebar > Asset Assistant",
    "description": "Generate, modify, rig, animate, validate, and export editable 3D assets",
    "category": "3D View",
}


def register():
    from . import (
        animation_adoption_ui, animation_modify_exchange, animation_names_ui, animation_tuning_ui, avian_ui,
        clothing_component_ui, component_adoption_ui, component_modify_apply,
        component_modify_exchange, cura_scale_ui, hair_component_ui, modification,
        modify_fastpath, modify_ui, run_ui, self_rigged_accessory, ui, ui_fastpath,
        workflow_ui, working_asset_ui,
    )
    run_ui.prepare(ui)
    avian_ui.prepare(ui)
    animation_tuning_ui.prepare(ui)
    workflow_ui.prepare(
        ui, modify_ui, animation_names_ui, working_asset_ui,
        component_adoption_ui, hair_component_ui, clothing_component_ui,
        animation_adoption_ui, self_rigged_accessory,
    )
    ui_fastpath.install(ui)
    animation_modify_exchange.install(modification, modify_ui)
    modify_fastpath.install(modify_ui)
    component_modify_exchange.install(modify_ui)
    component_modify_apply.install(modify_ui)
    ui.register()
    animation_names_ui.register()
    animation_tuning_ui.register()
    animation_adoption_ui.register()
    run_ui.register(ui.HUMANOID_PG_settings)
    cura_scale_ui.register(ui.HUMANOID_PG_settings)
    modify_ui.register()
    working_asset_ui.register()
    component_adoption_ui.register()
    hair_component_ui.register()
    clothing_component_ui.register()
    self_rigged_accessory.register()


def unregister():
    from . import (
        animation_adoption_ui, animation_names_ui, animation_tuning_ui, clothing_component_ui,
        component_adoption_ui, cura_scale_ui, hair_component_ui, modify_ui,
        run_ui, self_rigged_accessory, ui, working_asset_ui,
    )
    self_rigged_accessory.unregister()
    clothing_component_ui.unregister()
    hair_component_ui.unregister()
    component_adoption_ui.unregister()
    working_asset_ui.unregister()
    modify_ui.unregister()
    cura_scale_ui.unregister(ui.HUMANOID_PG_settings)
    run_ui.unregister(ui.HUMANOID_PG_settings)
    animation_adoption_ui.unregister()
    animation_tuning_ui.unregister()
    animation_names_ui.unregister()
    ui.unregister()
