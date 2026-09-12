# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import patch

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

import blender_adapter.modification as modification
from blender_adapter.adapter import create_character
from object_core.modification import ModificationRequest, plan_modification
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderParameterModificationPerformanceTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for collection in tuple(bpy.data.collections):
            if collection.users == 0:
                bpy.data.collections.remove(collection)

    def _avian(self):
        provider = get_provider("avian")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name=provider.label, scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def test_parameter_apply_reuses_staged_mesh_for_post_apply_validation(self):
        root = self._avian()
        snapshot = modification.inspect_generated_asset(root)
        plan = plan_modification(
            snapshot,
            ModificationRequest(parameter_changes=(("wingspan_cm", 120.0),)),
        )

        with patch.object(modification, "_expected_mesh", wraps=modification._expected_mesh) as expected_mesh:
            result = modification.apply_parameter_modification(root, plan)

        self.assertTrue(result.owns_geometry)
        self.assertEqual(120.0, result.parameter_values()["wingspan_cm"])
        self.assertEqual(1, expected_mesh.call_count)


if __name__ == "__main__":
    unittest.main()
