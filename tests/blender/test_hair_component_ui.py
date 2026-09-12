# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.hair_component_ui import _default_attachment
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class HairComponentUiTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def _human(self, rigged):
        provider = get_provider("human_experimental")
        values = {field.key: field.default for field in provider.parameters}
        mesh = provider.mesh(values)
        kwargs = {}
        if rigged:
            kwargs["skeleton"] = provider.skeleton(values)
            kwargs["skin_weights"] = provider.skin_weights(mesh, values)
        root = create_character(mesh, name="Human", scene=bpy.context.scene, **kwargs)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def test_rigged_human_defaults_hair_to_head_bone(self):
        self.assertEqual("bone:head", _default_attachment(self._human(True)))

    def test_unrigged_asset_defaults_hair_to_asset_root(self):
        self.assertEqual("asset_root", _default_attachment(self._human(False)))


if __name__ == "__main__":
    unittest.main()
