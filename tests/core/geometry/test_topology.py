# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import (
    boundary_edges,
    connected_surface_count,
    generate_deformable_mesh,
    is_closed_manifold,
    nonmanifold_edges,
)


class HumanTopologyTests(unittest.TestCase):
    def test_deformable_human_is_one_closed_manifold(self):
        for body_type in BodyType:
            with self.subTest(body_type=body_type):
                p = generate_proportions(HumanoidSpec(180, 95, body_type))
                mesh = generate_deformable_mesh(p)
                self.assertEqual(len(mesh.parts), 1)
                part = mesh.parts[0]
                self.assertEqual(connected_surface_count(part), 1)
                self.assertTrue(is_closed_manifold(part))
                self.assertEqual(boundary_edges(part), ())
                self.assertEqual(nonmanifold_edges(part), ())

    def test_topology_helpers_reject_non_mesh_parts(self):
        with self.assertRaisesRegex(TypeError, "MeshPart"):
            boundary_edges(object())
        with self.assertRaisesRegex(TypeError, "MeshPart"):
            connected_surface_count(object())


if __name__ == "__main__":
    unittest.main()
