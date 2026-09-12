# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.component_primitives import hair_shell_mesh, ring_mesh


class ComponentPrimitiveTests(unittest.TestCase):
    def test_ring_mesh_is_lightweight_closed_torus(self):
        mesh = ring_mesh()
        self.assertEqual(1, len(mesh.parts))
        self.assertEqual("Ring", mesh.parts[0].name)
        self.assertEqual(24 * 8, mesh.vertex_count)
        self.assertEqual(24 * 8, mesh.face_count)

    def test_ring_mesh_can_scale_down_for_finger_or_up_for_bracelet(self):
        finger = ring_mesh(1.0, 0.15)
        bracelet = ring_mesh(3.5, 0.4)
        self.assertLess(finger.bounds_cm[1][0], bracelet.bounds_cm[1][0])

    def test_ring_mesh_rejects_invalid_radii(self):
        with self.assertRaises(ValueError):
            ring_mesh(1.0, 1.0)

    def test_hair_shell_is_lightweight_separate_mesh(self):
        mesh = hair_shell_mesh()
        self.assertEqual(1, len(mesh.parts))
        self.assertEqual("Hair", mesh.parts[0].name)
        self.assertLess(mesh.vertex_count, 128)
        self.assertLess(mesh.face_count, 128)
        self.assertLess(mesh.bounds_cm[0][2], 0.0)
        self.assertGreater(mesh.bounds_cm[1][2], 0.0)

    def test_hair_shell_zero_back_length_keeps_cap_only(self):
        short = hair_shell_mesh(back_length_cm=0.0)
        long = hair_shell_mesh(back_length_cm=30.0)
        self.assertGreater(long.vertex_count, short.vertex_count)
        self.assertLess(long.bounds_cm[0][2], short.bounds_cm[0][2])

    def test_hair_shell_rejects_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            hair_shell_mesh(width_cm=0.0)


if __name__ == "__main__":
    unittest.main()
