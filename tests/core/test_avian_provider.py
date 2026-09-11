# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.models import ObjectMesh
from object_core.objects import get_provider


class AvianProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("avian")
        self.defaults = {field.key: field.default for field in self.provider.parameters}

    def test_avian_identity_and_foundation_capabilities(self):
        self.assertEqual(self.provider.key, "avian")
        self.assertEqual(self.provider.label, "Avian")
        self.assertFalse(self.provider.supports_rig)
        self.assertFalse(self.provider.supports_idle)
        self.assertFalse(self.provider.supports_locomotion)
        self.assertFalse(self.provider.supports_run)
        self.assertFalse(self.provider.uses_skin_weights)
        self.assertFalse(self.provider.supports_materials)

    def test_default_avian_blockout_is_deterministic_and_editable(self):
        mesh = self.provider.mesh(self.defaults)
        self.assertIsInstance(mesh, ObjectMesh)
        self.assertEqual(mesh, self.provider.mesh(self.defaults))
        self.assertEqual(
            tuple(part.name for part in mesh.parts),
            ("avian.body", "avian.head", "avian.wing.left", "avian.wing.right", "avian.tail"),
        )
        self.assertEqual(mesh.vertex_count, 34)
        self.assertEqual(mesh.face_count, 27)
        for part in mesh.parts:
            referenced = {index for face in part.faces for index in face}
            self.assertEqual(referenced, set(range(len(part.vertices))))

    def test_wingspan_parameter_controls_lateral_extent(self):
        narrow = self.provider.mesh(dict(self.defaults, wingspan_cm=50))
        wide = self.provider.mesh(dict(self.defaults, wingspan_cm=180))
        narrow_width = narrow.bounds_cm[1][0] - narrow.bounds_cm[0][0]
        wide_width = wide.bounds_cm[1][0] - wide.bounds_cm[0][0]
        self.assertAlmostEqual(narrow_width, 50)
        self.assertAlmostEqual(wide_width, 180)
        self.assertGreater(wide_width, narrow_width)

    def test_body_and_tail_dimensions_control_expected_axes(self):
        short_body = self.provider.mesh(dict(self.defaults, body_length_cm=25))
        long_body = self.provider.mesh(dict(self.defaults, body_length_cm=90))
        short_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=6))
        long_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=70))
        low = self.provider.mesh(dict(self.defaults, body_height_cm=8))
        tall = self.provider.mesh(dict(self.defaults, body_height_cm=50))

        self.assertGreater(long_body.bounds_cm[1][1], short_body.bounds_cm[1][1])
        self.assertLess(long_tail.bounds_cm[0][1], short_tail.bounds_cm[0][1])
        self.assertGreater(tall.bounds_cm[1][2], low.bounds_cm[1][2])

    def test_invalid_parameters_are_rejected(self):
        for field in self.provider.parameters:
            for value in (True, "bad", float("nan"), field.minimum - 1, field.maximum + 1):
                values = dict(self.defaults)
                values[field.key] = value
                with self.subTest(parameter=field.key, value=value):
                    with self.assertRaises((TypeError, ValueError)):
                        self.provider.mesh(values)

    def test_wingspan_must_exceed_body_width(self):
        values = dict(self.defaults, body_width_cm=30, wingspan_cm=20)
        with self.assertRaisesRegex(ValueError, "Wingspan"):
            self.provider.mesh(values)


if __name__ == "__main__":
    unittest.main()
