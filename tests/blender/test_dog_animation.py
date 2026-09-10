# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from object_core.objects import get_provider
from humanoid_blender.adapter import create_character
from humanoid_blender.animation import add_idle, add_locomotion, generated_action


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class DogAnimationBlenderTests(unittest.TestCase):
    def setUp(self):
        self.scene = bpy.data.scenes.new("DogAnimationTest")
        self.previous_scene = bpy.context.window.scene
        bpy.context.window.scene = self.scene
        self.objects_before = set(bpy.data.objects)
        self.meshes_before = set(bpy.data.meshes)
        self.armatures_before = set(bpy.data.armatures)
        self.collections_before = set(bpy.data.collections)
        self.actions_before = set(bpy.data.actions)

    def tearDown(self):
        bpy.context.window.scene = self.previous_scene
        for action in set(bpy.data.actions) - self.actions_before:
            bpy.data.actions.remove(action)
        for obj in set(bpy.data.objects) - self.objects_before:
            bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in set(bpy.data.meshes) - self.meshes_before:
            bpy.data.meshes.remove(mesh)
        for collection in set(bpy.data.collections) - self.collections_before:
            bpy.data.collections.remove(collection)
        for data in set(bpy.data.armatures) - self.armatures_before:
            bpy.data.armatures.remove(data)
        bpy.data.scenes.remove(self.scene)

    def _dog(self):
        provider = get_provider("dog")
        values = {field.key: field.default for field in provider.parameters}
        mesh = provider.mesh(values)
        skeleton = provider.skeleton(values)
        weights = provider.skin_weights(mesh, values)
        root = create_character(mesh, scene=self.scene, skeleton=skeleton, skin_weights=weights)
        root["object_type"] = "dog"
        for key, value in values.items():
            root[key] = value
        return root

    def test_idle_and_walk_actions_generate_and_drive_connected_dog_surface(self):
        root = self._dog()
        rig = next(obj for obj in root.children if obj.type == "ARMATURE")
        mesh = next(obj for obj in root.children if obj.type == "MESH")

        idle, _ = add_idle(root, self.scene, 4.0, 1.0)
        self.assertIs(idle, generated_action(root, "Idle"))
        self.assertIs(rig.animation_data.action, idle)

        walk, _ = add_locomotion(root, self.scene, 1.2, 1.0)
        self.assertIs(walk, generated_action(root, "Walk"))
        self.assertIs(rig.animation_data.action, walk)

        graph = bpy.context.evaluated_depsgraph_get()
        self.scene.frame_set(self.scene.frame_start)
        bpy.context.view_layer.update()
        start = [v.co.copy() for v in mesh.evaluated_get(graph).data.vertices]
        self.scene.frame_set(self.scene.frame_start + max(1, round(self.scene.render.fps * 0.3)))
        bpy.context.view_layer.update()
        later = [v.co.copy() for v in mesh.evaluated_get(graph).data.vertices]
        self.assertTrue(any((a - b).length > 1e-5 for a, b in zip(start, later)))

        self.assertIn("fore_upper.left", rig.pose.bones)
        self.assertIn("hind_upper.right", rig.pose.bones)
        self.assertIn("tail.3", rig.pose.bones)


if __name__ == "__main__":
    unittest.main()
