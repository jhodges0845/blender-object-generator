# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify saved animation deforms meshes without the add-on being registered."""
import bpy

rig = next(obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE')
hand = next(obj for obj in rig.parent.children if obj.get('part_name') == 'hand.left')
foot = next(obj for obj in rig.parent.children if obj.get('part_name') == 'foot.left')


def vertices(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]


start, end = rig.animation_data.action.frame_range
bpy.context.scene.frame_set(int(start))
first, planted = vertices(hand), vertices(foot)
bpy.context.scene.frame_set(int((start + end) / 2))
movement = max((a-b).length for a, b in zip(first, vertices(hand)))
assert movement > 0.02, movement
assert max((a-b).length for a, b in zip(planted, vertices(foot))) < 1e-5
bpy.context.scene.frame_set(int(end))
assert max((a-b).length for a, b in zip(first, vertices(hand))) < 1e-5
print('SAVED_ANIMATION_OK: mesh displacement %.4f meters; loop and planted foot verified' % movement)
