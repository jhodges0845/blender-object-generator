# SPDX-License-Identifier: GPL-3.0-or-later
"""Real Blender deformation checks for the connected Quadruped surface."""

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from object_core.objects import get_provider
from blender_adapter.adapter import create_character


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class QuadrupedDeformationTests(unittest.TestCase):
    def setUp(self):
        self.scene = bpy.data.scenes.new("QuadrupedDeformationTest")
        self.previous_scene = bpy.context.window.scene
        bpy.context.window.scene = self.scene
        self.objects_before = set(bpy.data.objects)
        self.meshes_before = set(bpy.data.meshes)
        self.armatures_before = set(bpy.data.armatures)
        self.collections_before = set(bpy.data.collections)

        provider = get_provider("quadruped")
        values = {field.key: field.default for field in provider.parameters}
        mesh = provider.mesh(values)
        skeleton = provider.skeleton(values)
        weights = provider.skin_weights(mesh, values)
        self.root = create_character(
            mesh,
            name="QuadrupedDeformation",
            scene=self.scene,
            skeleton=skeleton,
            skin_weights=weights,
        )
        self.rig = next(obj for obj in self.root.children if obj.type == "ARMATURE")
        self.quadruped = next(obj for obj in self.root.children if obj.type == "MESH")

    def tearDown(self):
        bpy.context.window.scene = self.previous_scene
        for obj in set(bpy.data.objects) - self.objects_before:
            bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in set(bpy.data.meshes) - self.meshes_before:
            bpy.data.meshes.remove(mesh)
        for collection in set(bpy.data.collections) - self.collections_before:
            bpy.data.collections.remove(collection)
        for armature in set(bpy.data.armatures) - self.armatures_before:
            bpy.data.armatures.remove(armature)
        bpy.data.scenes.remove(self.scene)

    def _evaluated_points(self):
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        evaluated = self.quadruped.evaluated_get(graph)
        return [evaluated.matrix_world @ vertex.co for vertex in evaluated.data.vertices]

    def _indices_weighted_to(self, bone_name, minimum=0.12):
        group = self.quadruped.vertex_groups.get(bone_name)
        self.assertIsNotNone(group, bone_name)
        indices = []
        for vertex in self.quadruped.data.vertices:
            try:
                weight = group.weight(vertex.index)
            except RuntimeError:
                continue
            if weight >= minimum:
                indices.append(vertex.index)
        self.assertTrue(indices, bone_name)
        return indices

    def _assert_bone_bends_surface(self, bone_name, axis, angle=0.35):
        before = self._evaluated_points()
        indices = self._indices_weighted_to(bone_name)
        pose_bone = self.rig.pose.bones[bone_name]
        pose_bone.rotation_mode = "XYZ"
        setattr(pose_bone.rotation_euler, axis, angle)
        after = self._evaluated_points()
        movement = [(after[index] - before[index]).length for index in indices]
        self.assertGreater(max(movement), 0.003, bone_name)
        pose_bone.rotation_euler = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()

    def test_major_quadruped_junctions_deform_when_bent(self):
        for bone_name, axis in (
            ("fore_upper.left", "x"),
            ("hind_upper.left", "x"),
            ("neck", "x"),
            ("tail.1", "x"),
            ("tail.2", "x"),
        ):
            with self.subTest(bone=bone_name):
                self._assert_bone_bends_surface(bone_name, axis)

    def test_bends_remain_local_to_the_target_region(self):
        before = self._evaluated_points()
        target = self._indices_weighted_to("fore_upper.left")
        opposite = self._indices_weighted_to("hind_lower.right", minimum=0.20)
        bone = self.rig.pose.bones["fore_upper.left"]
        bone.rotation_mode = "XYZ"
        bone.rotation_euler.x = 0.35
        after = self._evaluated_points()
        target_move = max((after[index] - before[index]).length for index in target)
        opposite_move = max((after[index] - before[index]).length for index in opposite)
        self.assertGreater(target_move, 0.003)
        self.assertLess(opposite_move, target_move * 0.20)


if __name__ == "__main__":
    unittest.main()
