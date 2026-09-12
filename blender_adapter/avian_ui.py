# SPDX-License-Identifier: GPL-3.0-or-later
"""Expose Avian Flight through the shared animation workflow."""

from math import ceil
from bpy.props import EnumProperty

from .animation import activate_generated_action, add_flight, generated_action


def prepare(ui):
    """Extend the shared clip selector with Flight before Blender registration."""
    settings_type = ui.HUMANOID_PG_settings
    settings_type.__annotations__['animation_clip'] = EnumProperty(name='Clip', default='IDLE', items=[
        ('IDLE', 'Idle', 'Generate or select the idle action'),
        ('WALK', 'Walk', 'Generate or select the in-place walk action'),
        ('RUN', 'Run', 'Generate or select the in-place run action'),
        ('FLIGHT', 'Flight', 'Generate or select the in-place flight action'),
    ])

    original_choice = ui._animation_choice

    def animation_choice(settings):
        if settings.animation_clip == 'FLIGHT':
            return 'Flight', 'supports_flight'
        return original_choice(settings)

    ui._animation_choice = animation_choice

    original_execute = ui.HUMANOID_OT_animation_clip.execute

    def execute(self, context):
        settings = context.scene.humanoid_settings
        if settings.animation_clip != 'FLIGHT':
            return original_execute(self, context)
        root = ui._character(context)
        existing = generated_action(root, 'Flight')
        try:
            if existing is not None:
                action = activate_generated_action(root, 'Flight')
                end = max(context.scene.frame_start, ceil(action.frame_range[1]) - 1)
                message = 'Flight selected. Existing keys were preserved.'
            else:
                action, end = add_flight(root, context.scene,
                                         settings.walk_duration, settings.walk_strength)
                message = 'Flight created. Press Play to preview.'
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

    ui.HUMANOID_OT_animation_clip.execute = execute
