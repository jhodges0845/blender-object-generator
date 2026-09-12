# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.modification import SemanticOperation
from object_core.objects import get_provider


class AvianSemanticGeometryTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("avian")
        self.values = {field.key: field.default for field in self.provider.parameters}

    def test_hooked_beak_preserves_topology_and_changes_forward_geometry(self):
        base = self.provider.mesh(self.values)
        operation = SemanticOperation(
            "shape", "beak", (("profile", "hooked"), ("amount", 0.9)),
        )
        patched = self.provider.semantic_mesh(base, self.values, (operation,))
        self.assertEqual(base.face_count, patched.face_count)
        self.assertEqual(base.vertex_count, patched.vertex_count)
        self.assertEqual(base.parts[0].faces, patched.parts[0].faces)
        self.assertNotEqual(base.parts[0].vertices, patched.parts[0].vertices)

    def test_semantic_operations_compose_in_order(self):
        base = self.provider.mesh(self.values)
        operations = (
            SemanticOperation("shape", "beak", (("profile", "hooked"), ("amount", 0.7))),
            SemanticOperation("shape", "chest", (("profile", "powerful"), ("amount", 0.8))),
            SemanticOperation("shape", "wing.left", (("profile", "broad"), ("amount", 0.6))),
            SemanticOperation("shape", "wing.right", (("profile", "broad"), ("amount", 0.6))),
            SemanticOperation("shape", "tail", (("profile", "fan"), ("amount", 0.5))),
        )
        patched = self.provider.semantic_mesh(base, self.values, operations)
        self.assertEqual(base.parts[0].faces, patched.parts[0].faces)
        self.assertNotEqual(base.bounds_cm, patched.bounds_cm)

    def test_scale_operation_rejects_extreme_values(self):
        base = self.provider.mesh(self.values)
        operation = SemanticOperation("scale", "head", (("factor", 12.0),))
        with self.assertRaisesRegex(ValueError, "scale must be between"):
            self.provider.semantic_mesh(base, self.values, (operation,))

    def test_unknown_profile_is_rejected_in_provider_owned_layer(self):
        base = self.provider.mesh(self.values)
        operation = SemanticOperation("shape", "beak", (("profile", "dragon"),))
        with self.assertRaisesRegex(ValueError, "Unsupported Avian semantic profile"):
            self.provider.semantic_mesh(base, self.values, (operation,))


if __name__ == "__main__":
    unittest.main()
