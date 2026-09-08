# SPDX-License-Identifier: GPL-3.0-or-later
"""Structural deformation-quality regressions for Human 1.0 joints."""

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_asset
from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.rigging import generate_deforming_skeleton, generate_skin_weights


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderJointDeformationQualityTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def _fixture(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        skeleton = generate_deforming_skeleton(proportions)
        weights = generate_skin_weights(mesh, skeleton)
        root = create_asset(mesh, name="JointQualityHuman", skeleton=skeleton, skin_weights=weights)
        obj = next(child for child in root.children if child.type == "MESH")
        armature = next(child for child in root.children if child.type == "ARMATURE")
        return weights, obj, armature

    def _evaluated_points(self, obj):
        graph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(graph)
        return [evaluated.matrix_world @ vertex.co for vertex in evaluated.data.vertices]

    def _indices_with_bones(self, weights, *bone_names):
        required = set(bone_names)
        return [
            index for index, influences in enumerate(weights[0].vertices)
            if required <= {influence.bone_name for influence in influences}
        ]

    def _spread(self, points, indices):
        selected = [points[index] for index in indices]
        center = sum(selected, selected[0].copy() * 0.0) / len(selected)
        return max((point - center).length for point in selected)

    def _assert_retains_spread(self, parent_bone, child_bone, axis, angle):
        weights, obj, armature = self._fixture()
        bpy.context.view_layer.update()
        indices = self._indices_with_bones(weights, parent_bone, child_bone)
        self.assertGreaterEqual(len(indices), 4)

        before = self._evaluated_points(obj)
        before_spread = self._spread(before, indices)

        pose_bone = armature.pose.bones[child_bone]
        pose_bone.rotation_mode = "XYZ"
        setattr(pose_bone.rotation_euler, axis.lower(), angle)
        bpy.context.view_layer.update()

        after = self._evaluated_points(obj)
        after_spread = self._spread(after, indices)
        self.assertGreater(after_spread, before_spread * 0.55)

    def test_elbow_bend_retains_transition_spread(self):
        self._assert_retains_spread("upper_arm.left", "forearm.left", "Z", 1.20)

    def test_wrist_bend_retains_transition_spread(self):
        self._assert_retains_spread("forearm.left", "hand.left", "Z", 1.05)

    def test_hip_bend_retains_transition_spread(self):
        self._assert_retains_spread("torso", "upper_leg.left", "X", 0.95)

    def test_knee_bend_retains_transition_spread(self):
        self._assert_retains_spread("upper_leg.left", "lower_leg.left", "X", 1.20)

    def test_ankle_bend_retains_transition_spread(self):
        self._assert_retains_spread("lower_leg.left", "foot.left", "X", 1.05)


if __name__ == "__main__":
    unittest.main()
