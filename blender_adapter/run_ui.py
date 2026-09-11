# SPDX-License-Identifier: GPL-3.0-or-later
"""Integrate Run into the main animation workflow while keeping legacy operator compatibility."""

import bpy
from bpy.props import EnumProperty, FloatProperty

from .animation import activate_generated_action, add_run, generated_action
from .workflow import find_character, provider_for


def _character(context):
    settings = getattr(context.scene, 'humanoid_settings', None)
    root = settings.target if settings and settings.target else find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


def _select_or_generate_run(context):
    root = _character(context)
    settings = context.scene.humanoid_settings
    existing = generated_action(root, 'Run')
    if existing is not None:
        action = activate_generated_action(root, 'Run')
        end = max(context.scene.frame_start, int(round(action.frame_range[1])) - 1)
        message = 'Run selected. Existing keys were preserved.'
    else:
        action, end = add_run(root, context.scene, settings.run_duration, settings.run_strength)
        message = 'Run created. Press Play to preview.'
    if settings.idle_set_range:
        context.scene.frame_end = end
        context.scene.use_preview_range = False
    context.scene.frame_set(context.scene.frame_start)
    settings.validation_results.clear()
    return message


class HUMANOID_OT_run_clip(bpy.types.Operator):
    """Legacy Run operator retained for saved scripts and older workflows."""
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
        try:
            message = _select_or_generate_run(context)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, message)
        return {'FINISHED'}


def prepare(ui):
    """Extend the stable Animations panel before its Blender classes are registered."""
    settings_type = ui.HUMANOID_PG_settings
    settings_type.__annotations__['animation_clip'] = EnumProperty(name='Clip', default='IDLE', items=[
        ('IDLE', 'Idle', 'Generate or select the idle action'),
        ('WALK', 'Walk', 'Generate or select the in-place walk action'),
        ('RUN', 'Run', 'Generate or select the in-place run action'),
    ])
    settings_type.__annotations__['run_duration'] = FloatProperty(
        name='Cycle (seconds)', default=0.72, min=0.35, max=2.0)
    settings_type.__annotations__['run_strength'] = FloatProperty(
        name='Motion Strength', default=1.0, min=0.1, max=2.0)

    original_choice = ui._animation_choice

    def animation_choice(settings):
        if settings.animation_clip == 'RUN':
            return 'Run', 'supports_run'
        return original_choice(settings)

    ui._animation_choice = animation_choice

    original_execute = ui.HUMANOID_OT_animation_clip.execute

    def execute(self, context):
        if context.scene.humanoid_settings.animation_clip != 'RUN':
            return original_execute(self, context)
        try:
            message = _select_or_generate_run(context)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, message)
        return {'FINISHED'}

    ui.HUMANOID_OT_animation_clip.execute = execute

    original_draw = ui._WorkflowPanel.draw

    def animation_draw(self, context):
        settings = context.scene.humanoid_settings
        if settings.animation_clip != 'RUN':
            return original_draw(self, context)
        layout = self.layout
        if context.mode != 'OBJECT':
            layout.operator('object.mode_set', text='Return to Object Mode').mode = 'OBJECT'
        layout.prop(settings, 'target')
        root = ui._character(context)
        if root is None:
            layout.label(text='Create or choose a character first.')
            return
        try:
            provider = provider_for(root)
        except ValueError as error:
            layout.label(text=str(error))
            return
        if not any(obj.type == 'ARMATURE' for obj in root.children):
            layout.label(text='Add a rig before animating.')
            return
        layout.prop(settings, 'animation_clip')
        if not getattr(provider, 'supports_run', False):
            layout.label(text=provider.label + ' does not support run.')
            return
        layout.prop(settings, 'run_duration')
        layout.prop(settings, 'run_strength')
        layout.prop(settings, 'idle_set_range')
        existing = generated_action(root, 'Run')
        layout.operator('humanoid.select_animation_clip',
                        text='Select Run' if existing else 'Generate Run')
        layout.operator('humanoid.preview_idle')
        layout.operator('screen.animation_play', text='Play / Pause', icon='PLAY')
        layout.label(text=('Existing generated keys are preserved.' if existing
                           else 'Creates a separate editable action.'))
        layout.label(text='All generated clips are exported together.')
        layout.label(text='Artist actions, NLA and drivers are never overwritten.')

    ui.HUMANOID_PT_animations.draw = animation_draw


def register(_settings_type=None):
    bpy.utils.register_class(HUMANOID_OT_run_clip)


def unregister(_settings_type=None):
    bpy.utils.unregister_class(HUMANOID_OT_run_clip)
