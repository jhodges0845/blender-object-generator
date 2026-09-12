# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class ModifyUITests(unittest.TestCase):
    def setUp(self):
        import blender_adapter as addon
        from blender_adapter.adapter import create_character
        from object_core.objects import get_provider

        self.addon = addon
        self.previous_scene = bpy.context.window.scene
        self.scene = bpy.data.scenes.new("ModifyUITest")
        bpy.context.window.scene = self.scene
        addon.register()

        provider = get_provider("avian")
        values = {field.key: field.default for field in provider.parameters}
        self.root = create_character(provider.mesh(values), name=provider.label, scene=self.scene)
        self.root["object_type"] = provider.key
        for key, value in values.items():
            self.root[key] = value
        self.scene.humanoid_settings.target = self.root
        bpy.context.view_layer.objects.active = self.root
        self.root.select_set(True)

    def tearDown(self):
        try:
            self.addon.unregister()
        finally:
            bpy.context.window.scene = self.previous_scene
            bpy.data.scenes.remove(self.scene)
            for action in tuple(bpy.data.actions):
                if action.users == 0:
                    bpy.data.actions.remove(action)
            for collection in tuple(bpy.data.collections):
                if collection.users == 0:
                    bpy.data.collections.remove(collection)

    def test_inspect_preview_and_apply_parameter_change(self):
        from blender_adapter import ui
        from object_core.objects import get_provider

        provider = get_provider("avian")
        self.assertEqual({"FINISHED"}, bpy.ops.asset_assistant.modify_inspect())
        self.assertEqual("INSPECTED", self.scene.get("asset_assistant_modify_status"))

        wingspan_property = ui._field_name(
            provider, next(field for field in provider.parameters if field.key == "wingspan_cm")
        )
        self.assertEqual(90.0, getattr(self.scene.humanoid_settings, wingspan_property))
        setattr(self.scene.humanoid_settings, wingspan_property, 120.0)

        self.assertEqual({"FINISHED"}, bpy.ops.asset_assistant.modify_preview())
        self.assertEqual("READY", self.scene.get("asset_assistant_modify_status"))
        self.assertIn("wingspan_cm", self.scene.get("asset_assistant_modify_summary"))
        self.assertEqual(90.0, self.root["wingspan_cm"])

        self.assertEqual({"FINISHED"}, bpy.ops.asset_assistant.modify_apply())
        self.assertEqual(120.0, self.root["wingspan_cm"])
        self.assertEqual("APPLIED", self.scene.get("asset_assistant_modify_status"))
        self.assertIn("Validation refreshed", self.scene.get("asset_assistant_modify_summary"))

    def test_preview_reports_no_changes_without_mutation(self):
        self.assertEqual({"FINISHED"}, bpy.ops.asset_assistant.modify_inspect())
        before = tuple(child.as_pointer() for child in self.root.children if child.type == "MESH")

        self.assertEqual({"FINISHED"}, bpy.ops.asset_assistant.modify_preview())

        after = tuple(child.as_pointer() for child in self.root.children if child.type == "MESH")
        self.assertEqual(before, after)
        self.assertEqual("NO_CHANGES", self.scene.get("asset_assistant_modify_status"))


if __name__ == "__main__":
    unittest.main()
