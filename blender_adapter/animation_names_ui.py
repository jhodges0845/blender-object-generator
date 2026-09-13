# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing controls for animation clip names and lifecycle."""

import bpy
from bpy.props import StringProperty

from .animation import clip_export_name, generated_action, set_clip_export_name
from .animation_lifecycle import exportable_actions, remove_animation
from .animation_records import animation_record, has_animation_record
from .asset_structure import asset_rigs
from .workflow import find_character


def _character(context):
    settings = getattr(context.scene, 'humanoid_settings', None) if context.scene else None
    root = settings.target if settings and settings.target else find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


def _clip_label(action):
    if has_animation_record(action):
        try:
            record = animation_record(action)
            return record.display_name or record.export_name or action.name
        except ValueError:
            pass
    return str(action.get('asset_assistant_clip') or action.name)


def _clip_source(action):
    if has_animation_record(action):
        try:
            return animation_record(action).source.value.replace('_', ' ').title()
        except ValueError:
            return 'Managed'
    return 'Generated (Legacy)' if action.get('asset_assistant_generated') else 'Unmanaged'


def _remove_button_text(action):
    if has_animation_record(action):
        try:
            return 'Delete Clip' if animation_record(action).owns_curves else 'Remove from Asset Assistant'
        except ValueError:
            return 'Remove Clip'
    return 'Delete Clip'


def _remove_action(root, action, animation_id=''):
    """Apply ownership-aware removal and return the artist-facing result message."""
    if root is None or action is None:
        raise ValueError('Choose a valid asset and animation clip first.')

    if has_animation_record(action):
        record = animation_record(action)
        if animation_id and record.animation_id != animation_id:
            raise ValueError('Animation identity changed; refresh the clip library before removing it.')
        removed = remove_animation(root, record.animation_id)
        if removed.owns_curves:
            return 'Deleted Asset Assistant-owned clip: ' + removed.display_name
        return 'Removed clip from Asset Assistant; the Blender Action and artist curves were preserved.'

    if not action.get('asset_assistant_generated') or action not in exportable_actions(root):
        raise ValueError('Only managed or Asset Assistant-owned animations can be removed here.')
    rigs = asset_rigs(root)
    if len(rigs) == 1 and rigs[0].animation_data is not None and rigs[0].animation_data.action == action:
        rigs[0].animation_data.action = None
    name = action.name
    bpy.data.actions.remove(action)
    return 'Deleted legacy Asset Assistant-owned clip: ' + name


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


class ASSET_ASSISTANT_OT_remove_animation_clip(bpy.types.Operator):
    bl_idname = 'asset_assistant.remove_animation_clip'
    bl_label = 'Remove Animation Clip'
    bl_description = 'Remove this clip from the Asset Assistant animation library'
    bl_options = {'REGISTER', 'UNDO'}

    action_name: StringProperty(options={'HIDDEN'})
    animation_id: StringProperty(options={'HIDDEN'})

    def invoke(self, context, event):
        action = bpy.data.actions.get(self.action_name)
        if action is None:
            self.report({'ERROR'}, 'The animation Action no longer exists.')
            return {'CANCELLED'}
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        root = _character(context)
        action = bpy.data.actions.get(self.action_name)
        try:
            message = _remove_action(root, action, self.animation_id)
        except (ValueError, RuntimeError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

        settings = getattr(context.scene, 'humanoid_settings', None)
        if settings is not None:
            settings.validation_results.clear()
        self.report({'INFO'}, message)
        return {'FINISHED'}


class ASSET_ASSISTANT_PT_animation_names(bpy.types.Panel):
    bl_label = 'Clip Library'
    bl_idname = 'ASSET_ASSISTANT_PT_animation_names'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animations'
    bl_parent_id = 'HUMANOID_PT_animations'

    @classmethod
    def poll(cls, context):
        root = _character(context) if context.scene else None
        return root is not None and bool(exportable_actions(root))

    def draw(self, context):
        layout = self.layout
        root = _character(context)
        actions = sorted(exportable_actions(root), key=lambda action: _clip_label(action).lower())

        intro = layout.box()
        intro.label(text='Animation Clips', icon='ACTION')
        intro.label(text='Generated clips can be deleted; imported or artist clips keep their Blender curves.')

        for action in actions:
            box = layout.box()
            title = box.row(align=True)
            title.label(text=_clip_label(action), icon='ACTION')
            title.label(text=_clip_source(action))
            box.label(text='Export Name: ' + clip_export_name(action))

            controls = box.row(align=True)
            if action.get('asset_assistant_generated'):
                rename = controls.operator('asset_assistant.rename_animation_clip', text='Rename for Export')
                rename.clip_name = str(action.get('asset_assistant_clip') or action.name)

            remove = controls.operator(
                'asset_assistant.remove_animation_clip',
                text=_remove_button_text(action),
                icon='TRASH',
            )
            remove.action_name = action.name
            if has_animation_record(action):
                try:
                    remove.animation_id = animation_record(action).animation_id
                except ValueError:
                    remove.animation_id = ''

        layout.label(text='Artist-authored curves are never deleted by Remove from Asset Assistant.')


_CLASSES = (
    ASSET_ASSISTANT_OT_rename_animation_clip,
    ASSET_ASSISTANT_OT_remove_animation_clip,
    ASSET_ASSISTANT_PT_animation_names,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
