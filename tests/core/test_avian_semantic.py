# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.modification import SemanticOperation
from object_core.providers.avian import AvianProvider


class AvianSemanticTests(unittest.TestCase):
    def setUp(self):
        self.provider = AvianProvider()
        self.values = {
            "body_length_cm": 42.0,
            "body_width_cm": 16.0,
            "body_height_cm": 20.0,
            "wingspan_cm": 90.0,
            "tail_length_cm": 22.0,
        }

    def test_beak_shape_changes_vertices_without_changing_topology(self):
        base = self.provider.mesh(self.values)
        modified = self.provider.apply_semantics(
            base,
            (SemanticOperation("shape", "beak", (("length_factor", 1.35), ("hook", 0.8))),),
            self.values,
        )
        self.assertEqual(base.face_count, modified.face_count)
        self.assertEqual(base.vertex_count, modified.vertex_count)
        base_tip = max(base.parts[0].vertices, key=lambda vertex: vertex[1])
        modified_tip = max(modified.parts[0].vertices, key=lambda vertex: vertex[1])
        self.assertGreater(modified_tip[1], base_tip[1])
        self.assertLess(modified_tip[2], base_tip[2])

    def test_wing_shape_can_change_one_side_without_mirroring_other_side(self):
        base = self.provider.mesh(self.values)
        modified = self.provider.apply_semantics(
            base,
            (SemanticOperation("shape", "wing.left", (("length_factor", 1.25),)),),
            self.values,
        )
        base_min_x = min(vertex[0] for vertex in base.parts[0].vertices)
        modified_min_x = min(vertex[0] for vertex in modified.parts[0].vertices)
        base_max_x = max(vertex[0] for vertex in base.parts[0].vertices)
        modified_max_x = max(vertex[0] for vertex in modified.parts[0].vertices)
        self.assertLess(modified_min_x, base_min_x)
        self.assertAlmostEqual(base_max_x, modified_max_x)

    def test_semantic_stack_composes_in_order(self):
        base = self.provider.mesh(self.values)
        operations = (
            SemanticOperation("shape", "chest", (("width_factor", 1.2),)),
            SemanticOperation("scale", "chest", (("z", 1.1),)),
        )
        modified = self.provider.apply_semantics(base, operations, self.values)
        self.assertNotEqual(base.parts[0].vertices, modified.parts[0].vertices)
        self.assertEqual(base.parts[0].faces, modified.parts[0].faces)

    def test_invalid_semantic_argument_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported beak shape argument"):
            self.provider.validate_semantic_operation(
                SemanticOperation("shape", "beak", (("magic", 1.0),))
            )


if __name__ == "__main__":
    unittest.main()
