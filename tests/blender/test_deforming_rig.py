# SPDX-License-Identifier: GPL-3.0-or-later
"""Real Blender integration tests; skipped by ordinary Python discovery."""

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
class BlenderDeformingRigTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def _deforming_human(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        skeleton = generate_deforming_skeleton(proportions)
        weights = generate_skin_weights(mesh, skeleton)
        root = create_asset(mesh, name="DeformingHuman", skeleton=skeleton, skin_weights=weights)
        obj = next(child for child in root.children if child.type == "MESH")
        armature = next(child for child in root.children if child.type == "ARMATURE")
        return mesh, skeleton, weights, root, obj, armature

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

    def test_unified_human_gets_vertex_groups_and_armature_modifier(self):
        _mesh, skeleton, weights, root, obj, armature = self._deforming_human()
        self.assertEqual(sum(child.type == "MESH" for child in root.children), 1)
        self.assertEqual(sum(child.type == "ARMATURE" for child in root.children), 1)
        self.assertEqual(root["stage"], "deforming_rig")
        self.assertEqual({bone.name for bone in armature.data.bones}, {bone.name for bone in skeleton.bones})
        self.assertTrue(all(bone.use_deform for bone in armature.data.bones))
        self.assertEqual(len(obj.data.vertices), len(weights[0].vertices))
        self.assertTrue(obj.vertex_groups.get("upper_arm.left"))
        self.assertTrue(obj.vertex_groups.get("upper_leg.right"))
        modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
        self.assertEqual(len(modifiers), 1)
        self.assertIs(modifiers[0].object, armature)
        self.assertTrue(modifiers[0].use_vertex_groups)
        self.assertFalse(modifiers[0].use_bone_envelopes)

        for vertex_index, expected in enumerate(weights[0].vertices):
            actual = {
                obj.vertex_groups[group.group].name: group.weight
                for group in obj.data.vertices[vertex_index].groups
            }
            self.assertEqual(set(actual), {influence.bone_name for influence in expected})
            self.assertAlmostEqual(sum(actual.values()), 1.0, places=5)
            for influence in expected:
                self.assertAlmostEqual(actual[influence.bone_name], influence.weight, places=5)

    def test_forearm_pose_deforms_local_vertices_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        left_indices = [
            index for index, influences in enumerate(weights[0].vertices)
            if any(influence.bone_name == "forearm.left" for influence in influences)
            and mesh.parts[0].vertices[index][0] > 0
        ]
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(left_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["forearm.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.z = 0.6
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in left_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_upper_arm_pose_deforms_blended_shoulder_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        shoulder_indices = self._indices_with_bones(weights, "torso", "upper_arm.left")
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(shoulder_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["upper_arm.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.y = 0.45
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in shoulder_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_hand_pose_deforms_blended_wrist_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        wrist_indices = self._indices_with_bones(weights, "forearm.left", "hand.left")
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(wrist_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["hand.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.y = 0.45
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in wrist_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_upper_leg_pose_deforms_blended_hip_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        hip_indices = self._indices_with_bones(weights, "torso", "upper_leg.left")
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(hip_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["upper_leg.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.x = 0.45
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in hip_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_lower_leg_pose_deforms_blended_knee_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        knee_indices = self._indices_with_bones(weights, "upper_leg.left", "lower_leg.left")
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(knee_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["lower_leg.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.x = 0.6
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in knee_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_foot_pose_deforms_blended_ankle_without_dragging_opposite_side(self):
        mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        ankle_indices = self._indices_with_bones(weights, "lower_leg.left", "foot.left")
        right_indices = [index for index, vertex in enumerate(mesh.parts[0].vertices) if vertex[0] < 0]
        self.assertTrue(ankle_indices)
        self.assertTrue(right_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["foot.left"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.x = 0.45
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in ankle_indices), 1e-3)
        self.assertLess(max((after[index] - before[index]).length for index in right_indices), 1e-6)

    def test_neck_pose_deforms_torso_neck_transition(self):
        _mesh, _skeleton, weights, _root, obj, armature = self._deforming_human()
        bpy.context.view_layer.update()
        neck_indices = self._indices_with_bones(weights, "torso", "neck")
        self.assertTrue(neck_indices)

        before = self._evaluated_points(obj)
        pose_bone = armature.pose.bones["neck"]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.y = 0.35
        bpy.context.view_layer.update()
        after = self._evaluated_points(obj)

        self.assertGreater(max((after[index] - before[index]).length for index in neck_indices), 1e-3)

    def test_weighted_path_requires_complete_matching_weights(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        skeleton = generate_deforming_skeleton(proportions)
        with self.assertRaisesRegex(ValueError, "cover every mesh part"):
            create_asset(mesh, skeleton=skeleton, skin_weights=())


if __name__ == "__main__":
    unittest.main()
