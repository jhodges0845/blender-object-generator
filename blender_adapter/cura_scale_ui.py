# SPDX-License-Identifier: GPL-3.0-or-later
"""Cura-only print-scale controls kept separate from the shared export workflow."""

import bpy
from bpy.props import EnumProperty


def _clear_report(settings, context):
    settings.validation_results.clear()
    settings.last_export = ''


class ASSETASSISTANT_PT_cura_scale(bpy.types.Panel):
    bl_label = 'Cura Print Scale'
    bl_idname = 'ASSETASSISTANT_PT_cura_scale'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export'
    bl_parent_id = 'HUMANOID_PT_export'

    @classmethod
    def poll(cls, context):
        return (context.scene is not None and
                hasattr(context.scene, 'humanoid_settings') and
                context.scene.humanoid_settings.output_target == 'CURA')

    def draw(self, context):
        settings = context.scene.humanoid_settings
        layout = self.layout
        layout.prop(settings, 'cura_print_scale', text='Scale')
        divisor = int(settings.cura_print_scale)
        layout.label(text=('Full physical size.' if divisor == 1 else
                           'STL dimensions divided by %d.' % divisor))
        if divisor == 10:
            layout.label(text='Example: 180 cm becomes 180 mm.')


_CLASSES = (ASSETASSISTANT_PT_cura_scale,)


def register(settings_type):
    settings_type.cura_print_scale = EnumProperty(
        name='Print Scale',
        default='1',
        items=(
            ('1', '1:1', 'Full physical size'),
            ('2', '1:2', 'Half physical size'),
            ('5', '1:5', 'One fifth physical size'),
            ('10', '1:10', 'One tenth physical size; 180 cm becomes 180 mm'),
            ('20', '1:20', 'One twentieth physical size'),
            ('50', '1:50', 'One fiftieth physical size'),
            ('100', '1:100', 'One hundredth physical size'),
        ),
        update=_clear_report,
        description='Scale only the Cura STL derivative; the Blender asset is unchanged')
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister(settings_type):
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    if hasattr(settings_type, 'cura_print_scale'):
        del settings_type.cura_print_scale
