"""Real Blender integration tests; skipped by ordinary Python discovery."""

import unittest
from unittest.mock import patch

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from humanoid_core import BodyType, HumanoidSpec, generate_mesh, generate_proportions
from humanoid_blender.adapter import create_character


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderAdapterTests(unittest.TestCase):
    def setUp(self):
        self.scene = bpy.data.scenes.new("AdapterTest")
        self.objects_before = set(bpy.data.objects)
        self.meshes_before = set(bpy.data.meshes)
        self.collections_before = set(bpy.data.collections)
        self.mesh = generate_mesh(generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE)))

    def tearDown(self):
        for obj in set(bpy.data.objects) - self.objects_before:
            bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in set(bpy.data.meshes) - self.meshes_before:
            bpy.data.meshes.remove(mesh)
        for collection in set(bpy.data.collections) - self.collections_before:
            bpy.data.collections.remove(collection)
        bpy.data.scenes.remove(self.scene)

    def test_editable_parts_match_source_and_scene_units(self):
        for scale in (1.0, 0.01):
            self.scene.unit_settings.scale_length = scale
            root = create_character(self.mesh, scene=self.scene)
            self.assertEqual(root.type, "EMPTY")
            self.assertEqual(len(root.children), 15)
            parts = {obj["body_part"]: obj for obj in root.children}
            for source in self.mesh.parts:
                obj = parts[source.name]
                self.assertEqual(obj.type, "MESH")
                self.assertEqual(tuple(tuple(face.vertices) for face in obj.data.polygons), source.faces)
                self.assertFalse(obj.data.validate())
                for actual, expected in zip(obj.data.vertices, source.vertices):
                    for coordinate, value in zip(actual.co, expected):
                        self.assertAlmostEqual(coordinate * scale, value * 0.01, places=5)
                self.assertEqual(tuple(obj.scale), (1, 1, 1))
            self.assertAlmostEqual(self.scene.unit_settings.scale_length, scale)

    def test_repeated_generation_preserves_existing_objects(self):
        first = create_character(self.mesh, scene=self.scene)
        first_names = {obj.name for obj in first.children}
        second = create_character(self.mesh, scene=self.scene)
        self.assertNotEqual(first.name, second.name)
        self.assertTrue(first_names.isdisjoint({obj.name for obj in second.children}))
        self.assertEqual(len(first.children), 15)
        self.assertEqual(len(self.scene.collection.children), 2)
        self.assertTrue(self.objects_before.issubset(set(bpy.data.objects)))

    def test_failed_creation_cleans_up_only_its_own_data(self):
        import humanoid_blender.adapter as adapter
        first = create_character(self.mesh, scene=self.scene)
        before = (set(bpy.data.objects), set(bpy.data.meshes), set(bpy.data.collections))
        real_populate = adapter._populate_mesh
        calls = [0]

        def fail_second_mesh(*args):
            calls[0] += 1
            if calls[0] == 2:
                raise RuntimeError("injected mesh creation failure")
            return real_populate(*args)

        with patch.object(adapter, "_populate_mesh", side_effect=fail_second_mesh):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                create_character(self.mesh, scene=self.scene)
        self.assertEqual(before, (set(bpy.data.objects), set(bpy.data.meshes), set(bpy.data.collections)))
        self.assertEqual(len(first.children), 15)

    def test_registration_and_sidebar_operator(self):
        import humanoid_blender
        previous_scene = bpy.context.window.scene
        bpy.context.window.scene = self.scene
        humanoid_blender.register()
        try:
            self.scene.cursor.location = (2, 3, 4)
            for preset in BodyType:
                self.scene.humanoid_settings.body_type = preset.value
                self.assertEqual(bpy.ops.humanoid.generate_blockout(), {"FINISHED"})
                root = bpy.context.view_layer.objects.active
                self.assertEqual(root["body_type"], preset.value)
                self.assertEqual(tuple(root.location), (2, 3, 4))
                self.assertEqual(len(root.children), 15)
            self.assertTrue(bpy.types.HUMANOID_PT_panel.is_registered)
        finally:
            humanoid_blender.unregister()
            bpy.context.window.scene = previous_scene
        self.assertFalse(hasattr(bpy.types.Scene, "humanoid_settings"))
        humanoid_blender.register()
        humanoid_blender.unregister()
