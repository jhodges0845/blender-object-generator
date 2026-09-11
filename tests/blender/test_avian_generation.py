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
                       ("objects", "meshes", "collections")}
        addon.register()

    def tearDown(self):
        self.addon.unregister()
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)

    def test_avian_appears_and_generates_through_shared_ui(self):
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
        self.assertEqual(settings.asset_use, "STATIC")
        self.assertEqual(
            {obj.get("part_name", obj.get("body_part")) for obj in root.children},
            {"avian.body", "avian.head", "avian.wing.left", "avian.wing.right", "avian.tail"},
        )
        self.assertFalse(bpy.ops.humanoid.add_basic_rig.poll())
        self.assertFalse(bpy.ops.humanoid.generate_idle.poll())


if __name__ == "__main__":
    unittest.main()
