# SPDX-License-Identifier: GPL-3.0-or-later
"""Compatibility coverage for saved provider identifiers."""

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_asset
from blender_adapter.workflow import provider_for
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class ProviderKeyMigrationTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.scene = bpy.data.scenes.new("ProviderKeyMigrationTest")
        bpy.context.window.scene = self.scene
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ("objects", "meshes", "collections")}

    def tearDown(self):
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)

    def test_saved_pre_quadruped_key_is_rewritten_when_asset_is_resolved(self):
        provider = get_provider("quadruped")
        values = {field.key: field.default for field in provider.parameters}
        root = create_asset(provider.mesh(values), name="LegacyQuadruped", scene=self.scene)
        root["generator"] = "object_generator"
        # Historical persisted value retained only as migration input.
        root["object_type"] = "dog"
        mesh = next(obj for obj in root.children if obj.type == "MESH")
        mesh["part_name"] = "dog"
        mesh["body_part"] = "dog"

        resolved = provider_for(root)

        self.assertIs(resolved, provider)
        self.assertEqual(root["object_type"], "quadruped")
        self.assertEqual(mesh["part_name"], "quadruped")
        self.assertEqual(mesh["body_part"], "quadruped")


if __name__ == "__main__":
    unittest.main()
