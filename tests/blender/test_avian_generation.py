# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class AvianGenerationTests(unittest.TestCase):
    def setUp(self):
        import blender_adapter as addon
        self.addon = addon
        self.previous_scene = bpy.context.window.scene
        self.scene = bpy.data.scenes.new("AvianGenerationTest")
        bpy.context.window.scene = self.scene
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ("objects", "meshes", "armatures", "collections")}
        addon.register()

    def tearDown(self):
        self.addon.unregister()
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)

    def test_avian_generates_and_rigs_through_shared_ui(self):
        settings = self.scene.humanoid_settings
        options = settings.bl_rna.properties["object_type"].enum_items
        self.assertIn(("avian", "Avian"),
                      [(item.identifier, item.name) for item in options])

        settings.object_type = "avian"
        settings.avian_body_length_cm = 48
        settings.avian_body_width_cm = 17
        settings.avian_body_height_cm = 22
        settings.avian_wingspan_cm = 120
        settings.avian_tail_length_cm = 26
        self.scene.cursor.location = (1, 2, 3)

        self.assertEqual(bpy.ops.humanoid.generate_blockout(), {"FINISHED"})
        root = settings.target
        self.assertEqual(root["object_type"], "avian")
        self.assertEqual(root["wingspan_cm"], 120)
        self.assertEqual(tuple(root.location), (1, 2, 3))
        self.assertEqual(settings.asset_use, "RIGGED")
        meshes = [obj for obj in root.children if obj.type == "MESH"]
        self.assertEqual(len(meshes), 1)
        self.assertEqual(meshes[0].get("part_name", meshes[0].get("body_part")), "avian")

        self.assertTrue(bpy.ops.humanoid.add_basic_rig.poll())
        self.assertEqual(bpy.ops.humanoid.add_basic_rig(), {"FINISHED"})
        rig = next(obj for obj in root.children if obj.type == "ARMATURE")
        self.assertIn("spine", rig.data.bones)
        self.assertIn("wing.upper.left", rig.data.bones)
        self.assertIn("wing.lower.right", rig.data.bones)
        self.assertIn("tail.2", rig.data.bones)
        self.assertEqual(len(meshes[0].modifiers), 1)
        self.assertIs(meshes[0].modifiers[0].object, rig)
        self.assertGreater(len(meshes[0].vertex_groups), 0)

        self.assertTrue(bpy.ops.humanoid.generate_idle.poll())
        settings.animation_clip = "FLIGHT"
        self.assertTrue(bpy.ops.humanoid.select_animation_clip.poll())
        settings.animation_clip = "RUN"
        self.assertFalse(bpy.ops.humanoid.select_animation_clip.poll())


if __name__ == "__main__":
    unittest.main()
