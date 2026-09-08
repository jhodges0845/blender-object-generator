# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_asset
from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderHumanUVTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def test_generated_human_gets_editable_uv_map(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(proportions)
        root = create_asset(mesh, name="UVHuman")
        obj = next(child for child in root.children if child.type == "MESH")

        self.assertEqual(len(obj.data.uv_layers), 1)
        layer = obj.data.uv_layers[0]
        self.assertEqual(layer.name, "UVMap")
        self.assertEqual(len(layer.data), len(obj.data.loops))
        self.assertTrue(all(0.0 <= item.uv[0] <= 1.0 and 0.0 <= item.uv[1] <= 1.0
                            for item in layer.data))


if __name__ == "__main__":
    unittest.main()
