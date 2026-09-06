# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert portable idle samples into editable Blender action curves."""

from math import ceil
from .workflow import provider_for


def add_idle(root, scene, duration=4.0, strength=1.0):
    import bpy
    from mathutils import Vector, Quaternion, Matrix

    provider = provider_for(root)
    if not provider.supports_idle:
        raise ValueError(provider.label + ' does not support idle animation.')
    clip = provider.idle(duration, strength)
    rigs = [obj for obj in root.children if obj.type == 'ARMATURE']
    if len(rigs) != 1:
        raise ValueError('Add one basic rig before generating an idle.')
    rig = rigs[0]
    data = rig.animation_data
    if data and (data.action or data.nla_tracks or data.drivers):
        raise ValueError('Existing animation preserved. Use a fresh rig for this idle generator.')
    for bone in rig.pose.bones:
        if bone.constraints or any(abs(bone.matrix_basis[i][j] - Matrix.Identity(4)[i][j]) > 1e-6
                                   for i in range(4) for j in range(4)):
            raise ValueError('Start from an unconstrained rest pose; existing pose preserved.')
    if any(track.bone not in rig.pose.bones for track in clip.tracks):
        raise ValueError('This rig is missing required humanoid bones.')
    fps = scene.render.fps / scene.render.fps_base
    start = scene.frame_start
    action = bpy.data.actions.new(rig.name + '.Idle')
    modes = {bone.name: bone.rotation_mode for bone in rig.pose.bones}
    had_data = data is not None
    try:
        for track in clip.tracks:
            bone = rig.pose.bones[track.bone]
            axis = bone.bone.matrix_local.to_3x3().inverted() @ Vector(track.axis)
            samples = [(start + seconds * fps, Quaternion(axis, angle)) for seconds, angle in track.keys]
            for component in range(4):
                curve = action.fcurves.new(bone.path_from_id('rotation_quaternion'), index=component,
                                           action_group=bone.name)
                curve.keyframe_points.add(len(samples))
                for key, (frame, rotation) in zip(curve.keyframe_points, samples):
                    key.co = (frame, rotation[component])
                    key.interpolation = 'LINEAR'
                curve.modifiers.new('CYCLES')
                curve.update()
        for track in clip.tracks:
            rig.pose.bones[track.bone].rotation_mode = 'QUATERNION'
        rig.animation_data_create().action = action
        action.use_fake_user = True
        rig.data.pose_position = 'POSE'
    except Exception:
        if rig.animation_data:
            rig.animation_data.action = None
        if not had_data:
            rig.animation_data_clear()
        for name, mode in modes.items():
            rig.pose.bones[name].rotation_mode = mode
        bpy.data.actions.remove(action)
        raise
    return action, max(start, ceil(start + clip.duration * fps) - 1)
