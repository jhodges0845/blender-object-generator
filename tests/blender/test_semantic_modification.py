# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.modification import apply_semantic_modification, inspect_generated_asset
from object_core.modification import ModificationRequest, SemanticOperation, plan_modification
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderSemanticModificationTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def _avian(self):
        provider = get_provider("avian")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name="Avian", scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def test_semantic_apply_persists_stack_and_remains_owned(self):
        root = self._avian()
        mesh = next(obj for obj in root.children if obj.type == "MESH")
        before = tuple(tuple(vertex.co) for vertex in mesh.data.vertices)
        snapshot = inspect_generated_asset(root)
        request = ModificationRequest(semantic_operations=(
            SemanticOperation("shape", "beak", (("length_factor", 1.3), ("hook", 0.7))),
        ))
        plan = plan_modification(snapshot, request)
        self.assertTrue(plan.safe_to_apply)

        result = apply_semantic_modification(root, plan)

        mesh = next(obj for obj in root.children if obj.type == "MESH")
        after = tuple(tuple(vertex.co) for vertex in mesh.data.vertices)
        self.assertNotEqual(before, after)
        self.assertEqual(1, len(result.semantic_operations))
        self.assertEqual("beak", result.semantic_operations[0].target)
        self.assertTrue(result.owns_geometry)
        reinspected = inspect_generated_asset(root)
        self.assertTrue(reinspected.owns_geometry)
        self.assertEqual(result.semantic_operations, reinspected.semantic_operations)

    def test_second_semantic_apply_appends_to_existing_non_destructive_stack(self):
        root = self._avian()
        first = plan_modification(
            inspect_generated_asset(root),
            ModificationRequest(semantic_operations=(
                SemanticOperation("shape", "beak", (("hook", 0.5),)),
            )),
        )
        apply_semantic_modification(root, first)
        second = plan_modification(
            inspect_generated_asset(root),
            ModificationRequest(semantic_operations=(
                SemanticOperation("shape", "chest", (("width_factor", 1.15),)),
            )),
        )
        result = apply_semantic_modification(root, second)
        self.assertEqual(("beak", "chest"), tuple(op.target for op in result.semantic_operations))
        self.assertTrue(result.owns_geometry)


if __name__ == "__main__":
    unittest.main()
