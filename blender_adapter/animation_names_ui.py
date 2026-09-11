# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing controls for generated animation clip export names."""

import bpy
from bpy.props import StringProperty

from .animation import clip_export_name, generated_action, generated_actions, set_clip_export_name
from .workflow import find_character


def _character(context):
    settings = getattr(context.scene, 'humanoid_settings', None) if context.scene else None
    root = settings.target if settings and settings.target else find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


class ASSET_ASSISTANT_OT_rename_animation_clip(bpy.types.Operator):
    bl_idname = 'asset_assistant.rename_animation_clip'
    bl_label = 'Rename Animation Clip'
    bl_description = 'Choose the animation name written to game-engine exports'
    bl_options = {'REGISTER', 'UNDO'}

    clip_name: StringProperty(options={'HIDDEN'})
    export_name: StringProperty(name='Export Name')

    def invoke(self, context, event):
        root = _character(context)
        action = generated_action(root, self.clip_name) if root else None
        if action is None:
            self.report({'ERROR'}, 'Generate this clip before renaming it.')
            return {'CANCELLED'}
        self.export_name = clip_export_name(action)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        root = _character(context)
        if root is None:
            self.report({'ERROR'}, 'Choose a generated character first.')
            return {'CANCELLED'}
        try:
            action = set_clip_export_name(root, self.clip_name, self.export_name)
        except ValueError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        context.scene.humanoid_settings.validation_results.clear()
        self.report({'INFO'}, self.clip_name + ' will export as ' + clip_export_name(action) + '.')
        return {'FINISHED'}


class ASSET_ASSISTANT_PT_animation_names(bpy.types.Panel):
    bl_label = 'Clip Export Names'
    bl_idname = 'ASSET_ASSISTANT_PT_animation_names'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animations'
    bl_parent_id = 'HUMANOID_PT_animations'

    @classmethod
    def poll(cls, context):
        root = _character(context) if context.scene else None
        return root is not None and bool(generated_actions(root))

    def draw(self, context):
        layout = self.layout
        root = _character(context)
        actions = sorted(generated_actions(root),
                         key=lambda action: str(action.get('asset_assistant_clip') or action.name))
        layout.label(text='Engine clips use simple names by default.')
        for action in actions:
            clip_name = str(action.get('asset_assistant_clip') or action.name)
            row = layout.row(align=True)
            row.label(text=clip_name + ' → ' + clip_export_name(action))
            button = row.operator('asset_assistant.rename_animation_clip', text='Rename')
            button.clip_name = clip_name


_CLASSES = (ASSET_ASSISTANT_OT_rename_animation_clip, ASSET_ASSISTANT_PT_animation_names)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
