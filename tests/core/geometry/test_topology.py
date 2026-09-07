# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import (
    boundary_edges,
    generate_deformable_mesh,
    is_closed_manifold,
    nonmanifold_edges,
)


class HumanTopologyTests(unittest.TestCase):
    def test_current_deformable_parts_are_closed_manifolds(self):
        """Keep every surface valid while shoulder/hip junctions are replaced."""
        for body_type in BodyType:
            with self.subTest(body_type=body_type):
                p = generate_proportions(HumanoidSpec(180, 95, body_type))
                mesh = generate_deformable_mesh(p)
                for part in mesh.parts:
                    with self.subTest(part=part.name):
                        self.assertTrue(is_closed_manifold(part))
                        self.assertEqual(boundary_edges(part), ())
                        self.assertEqual(nonmanifold_edges(part), ())

    def test_topology_helpers_reject_non_mesh_parts(self):
        with self.assertRaisesRegex(TypeError, "MeshPart"):
            boundary_edges(object())


if __name__ == "__main__":
    unittest.main()
