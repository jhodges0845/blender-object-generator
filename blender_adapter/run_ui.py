# SPDX-License-Identifier: GPL-3.0-or-later
"""Run-animation controls kept separate from the stable animation panel."""

import bpy
from bpy.props import FloatProperty

from .animation import activate_generated_action, add_run, generated_action
from .workflow import find_character, provider_for


def _character(context):
    settings = getattr(context.scene, 'humanoid_settings', None)
    root = settings.target if settings and settings.target else find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


class HUMANOID_OT_run_clip(bpy.types.Operator):
    bl_idname = 'humanoid.select_run_clip'
    bl_label = 'Generate / Select Run'
    bl_description = 'Generate the Run clip once, then select it without overwriting edits'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene is None or context.mode != 'OBJECT':
            return False
        root = _character(context)
        if root is None or sum(obj.type == 'ARMATURE' for obj in root.children) != 1:
            return False
        try:
            return bool(getattr(provider_for(root), 'supports_run', False))
        except (ValueError, TypeError, AttributeError):
            return False

    def execute(self, context):
        root = _character(context)
        settings = context.scene.humanoid_settings
        try:
            existing = generated_action(root, 'Run')
            if existing is not None:
                action = activate_generated_action(root, 'Run')
                end = max(context.scene.frame_start, int(round(action.frame_range[1])) - 1)
                message = 'Run selected. Existing keys were preserved.'
            else:
                action, end = add_run(root, context.scene,
                                      settings.run_duration, settings.run_strength)
                message = 'Run created. Press Play to preview.'
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        if settings.idle_set_range:
            context.scene.frame_end = end
            context.scene.use_preview_range = False
        context.scene.frame_set(context.scene.frame_start)
        settings.validation_results.clear()
        self.report({'INFO'}, message)
        return {'FINISHED'}


class HUMANOID_PT_run_animation(bpy.types.Panel):
    bl_label = 'Run'
    bl_idname = 'HUMANOID_PT_run_animation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animations'

    def draw(self, context):
        layout = self.layout
        root = _character(context)
        if root is None:
            layout.label(text='Create or choose a character first.')
            return
        try:
            provider = provider_for(root)
        except ValueError as error:
            layout.label(text=str(error))
            return
        if not getattr(provider, 'supports_run', False):
            layout.label(text=provider.label + ' does not support Run.')
            return
        if not any(obj.type == 'ARMATURE' for obj in root.children):
            layout.label(text='Add a rig before animating.')
            return
        settings = context.scene.humanoid_settings
        layout.prop(settings, 'run_duration')
        layout.prop(settings, 'run_strength')
        existing = generated_action(root, 'Run')
        layout.operator('humanoid.select_run_clip',
                        text='Select Run' if existing else 'Generate Run')
        layout.operator('screen.animation_play', text='Play / Pause', icon='PLAY')
        layout.label(text='Run exports with Idle and Walk.')


_CLASSES = (HUMANOID_OT_run_clip, HUMANOID_PT_run_animation)


def register(settings_type):
    settings_type.__annotations__['run_duration'] = FloatProperty(
        name='Cycle (seconds)', default=0.72, min=0.35, max=2.0)
    settings_type.__annotations__['run_strength'] = FloatProperty(
        name='Motion Strength', default=1.0, min=0.1, max=2.0)
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister(settings_type):
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
