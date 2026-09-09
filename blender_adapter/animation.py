# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert portable provider animation samples into editable Blender actions."""

from math import ceil
from .workflow import provider_for


_GENERATED = 'asset_assistant_generated'
_GENERATED_RIG = 'asset_assistant_rig'
_GENERATED_CLIP = 'asset_assistant_clip'


def action_curves(action, slot=None):
    """Read only the assigned slot on layered actions, or legacy action curves."""
    if hasattr(action, 'fcurves') and not getattr(action, 'is_action_layered', False):
        return tuple(action.fcurves)
    if slot is None:
        return ()
    return tuple(curve for layer in action.layers for strip in layer.strips
                 if strip.type == 'KEYFRAME'
                 for bag in [strip.channelbag(slot)] if bag is not None
                 for curve in bag.fcurves)


def _rig(root):
    rigs = [obj for obj in root.children if obj.type == 'ARMATURE']
    if len(rigs) != 1:
        raise ValueError('Add one basic rig before generating animation.')
    return rigs[0]


def generated_actions(root):
    """Return generated Asset Assistant actions belonging to this rig."""
    import bpy
    rig = _rig(root)
    return tuple(action for action in bpy.data.actions
                 if action.get(_GENERATED) and action.get(_GENERATED_RIG) == rig.name)


def generated_action(root, clip_name):
    return next((action for action in generated_actions(root)
                 if action.get(_GENERATED_CLIP) == clip_name), None)


def activate_generated_action(root, clip_name):
    """Activate an existing generated clip without changing or rebuilding it."""
    rig = _rig(root)
    action = generated_action(root, clip_name)
    if action is None:
        raise ValueError('Generate the ' + clip_name + ' clip first.')
    data = rig.animation_data_create()
    if data.nla_tracks or data.drivers:
        raise ValueError('Existing NLA tracks or drivers are preserved; prepare them manually before switching clips.')
    if data.action and not (data.action.get(_GENERATED) and data.action.get(_GENERATED_RIG) == rig.name):
        raise ValueError('Existing artist animation preserved; generated clips cannot replace it.')
    data.action = action
    if hasattr(action, 'slots') and len(action.slots):
        data.action_slot = action.slots[0]
    rig.data.pose_position = 'POSE'
    return action


def _add_clip(root, scene, clip, suffix):
    import bpy
    from mathutils import Vector, Quaternion, Matrix

    rig = _rig(root)
    data = rig.animation_data
    if generated_action(root, suffix) is not None:
        raise ValueError('Existing animation preserved. ' + suffix + ' already exists; select that clip instead of overwriting it.')
    if data and (data.nla_tracks or data.drivers):
        raise ValueError('Existing animation preserved. NLA tracks and drivers require manual preparation.')
    if data and data.action and not (data.action.get(_GENERATED) and data.action.get(_GENERATED_RIG) == rig.name):
        raise ValueError('Existing animation preserved. Use a fresh rig or keep the artist action active.')

    previous_action = data.action if data else None
    previous_slot = getattr(data, 'action_slot', None) if data else None
    previous_frame, previous_subframe = scene.frame_current, scene.frame_subframe
    if previous_action is not None:
        data.action = None
        # Blender can retain the evaluated pose from the detached generated action,
        # especially when the user is parked on a non-start frame. Explicitly clear
        # those generated transforms before applying the artist-pose safety check.
        for bone in rig.pose.bones:
            bone.matrix_basis.identity()
        scene.frame_set(previous_frame, subframe=previous_subframe)

    try:
        for bone in rig.pose.bones:
            if bone.constraints or any(abs(bone.matrix_basis[i][j] - Matrix.Identity(4)[i][j]) > 1e-6
                                       for i in range(4) for j in range(4)):
                raise ValueError('Start from an unconstrained rest pose; existing pose preserved.')
        if any(track.bone not in rig.pose.bones for track in clip.tracks):
            raise ValueError('This rig is missing bones required by the provider animation.')

        fps = scene.render.fps / scene.render.fps_base
        start = scene.frame_start
        action = bpy.data.actions.new(rig.name + '.' + suffix)
        action[_GENERATED] = True
        action[_GENERATED_RIG] = rig.name
        action[_GENERATED_CLIP] = suffix
        modes = {bone.name: bone.rotation_mode for bone in rig.pose.bones}
        had_data = data is not None
        try:
            if hasattr(action, 'slots'):
                from bpy_extras.anim_utils import action_ensure_channelbag_for_slot
                slot = action.slots.new('OBJECT', rig.name)
                curves = action_ensure_channelbag_for_slot(action, slot).fcurves
            else:
                slot = None
                curves = action.fcurves
            for track in clip.tracks:
                bone = rig.pose.bones[track.bone]
                axis = bone.bone.matrix_local.to_3x3().inverted() @ Vector(track.axis)
                samples = [(start + seconds * fps, Quaternion(axis, angle)) for seconds, angle in track.keys]
                group = {'group_name' if slot is not None else 'action_group': bone.name}
                for component in range(4):
                    curve = curves.new(bone.path_from_id('rotation_quaternion'), index=component,
                                       **group)
                    curve.keyframe_points.add(len(samples))
                    for key, (frame, rotation) in zip(curve.keyframe_points, samples):
                        key.co = (frame, rotation[component])
                        key.interpolation = 'LINEAR'
                    curve.modifiers.new('CYCLES')
                    curve.update()
            for track in clip.tracks:
                rig.pose.bones[track.bone].rotation_mode = 'QUATERNION'
            rig.animation_data_create().action = action
            if slot is not None:
                rig.animation_data.action_slot = slot
            action.use_fake_user = True
            rig.data.pose_position = 'POSE'
        except Exception:
            if rig.animation_data:
                rig.animation_data.action = previous_action
                if previous_action is not None and previous_slot is not None and hasattr(rig.animation_data, 'action_slot'):
                    rig.animation_data.action_slot = previous_slot
            if not had_data:
                rig.animation_data_clear()
            for name, mode in modes.items():
                rig.pose.bones[name].rotation_mode = mode
            bpy.data.actions.remove(action)
            raise
        return action, max(start, ceil(start + clip.duration * fps) - 1)
    except Exception:
        if data and data.action is None and previous_action is not None:
            data.action = previous_action
            if previous_slot is not None and hasattr(data, 'action_slot'):
                data.action_slot = previous_slot
        raise
    finally:
        scene.frame_set(previous_frame, subframe=previous_subframe)


def add_idle(root, scene, duration=4.0, strength=1.0):
    provider = provider_for(root)
    if not provider.supports_idle:
        raise ValueError(provider.label + ' does not support idle animation.')
    return _add_clip(root, scene, provider.idle(duration, strength), 'Idle')


def add_locomotion(root, scene, duration=1.2, strength=1.0):
    provider = provider_for(root)
    if not getattr(provider, 'supports_locomotion', False):
        raise ValueError(provider.label + ' does not support locomotion animation.')
    return _add_clip(root, scene, provider.locomotion(duration, strength), 'Walk')
