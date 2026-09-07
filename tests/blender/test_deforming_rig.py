# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

import bpy

from blender_adapter.adapter import create_asset
from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.rigging import generate_deforming_skeleton, generate_skin_weights


class BlenderDeformingRigTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def test_unified_human_gets_vertex_groups_and_armature_modifier(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        skeleton = generate_deforming_skeleton(proportions)
        weights = generate_skin_weights(mesh, skeleton)
        root = create_asset(
            mesh,
            name="DeformingHuman",
            skeleton=skeleton,
            skin_weights=weights,
        )

        mesh_objects = [obj for obj in root.children if obj.type == "MESH"]
        armatures = [obj for obj in root.children if obj.type == "ARMATURE"]
        self.assertEqual(len(mesh_objects), 1)
        self.assertEqual(len(armatures), 1)
        obj = mesh_objects[0]
        armature = armatures[0]
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

    def test_weighted_path_requires_complete_matching_weights(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        skeleton = generate_deforming_skeleton(proportions)
        with self.assertRaisesRegex(ValueError, "cover every mesh part"):
            create_asset(mesh, skeleton=skeleton, skin_weights=())


if __name__ == "__main__":
    unittest.main()
