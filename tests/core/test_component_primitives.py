# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.component_primitives import ring_mesh


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


if __name__ == "__main__":
    unittest.main()
