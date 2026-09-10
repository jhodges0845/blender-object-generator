# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.models import ObjectMesh
from object_core.objects import get_provider


class DogProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("dog")
        self.defaults = {field.key: field.default for field in self.provider.parameters}

    def test_dog_provider_is_registered_as_static_foundation(self):
        self.assertEqual(self.provider.label, "Dog")
        self.assertFalse(self.provider.supports_rig)
        self.assertFalse(self.provider.supports_idle)
        self.assertFalse(self.provider.supports_locomotion)
        self.assertFalse(self.provider.uses_skin_weights)
        self.assertFalse(self.provider.supports_materials)

    def test_default_dog_generates_deterministic_quadruped_blockout(self):
        mesh = self.provider.mesh(self.defaults)
        self.assertIsInstance(mesh, ObjectMesh)
        self.assertEqual(mesh, self.provider.mesh(self.defaults))
        self.assertEqual(
            tuple(part.name for part in mesh.parts),
            (
                "dog_torso", "dog_head", "dog_muzzle",
                "dog_foreleg_left", "dog_hindleg_left",
                "dog_foreleg_right", "dog_hindleg_right",
                "dog_tail_1", "dog_tail_2", "dog_tail_3",
            ),
        )
        self.assertEqual(mesh.vertex_count, 80)
        self.assertEqual(mesh.face_count, 60)

    def test_dimensions_drive_independent_dog_axes(self):
        short = self.provider.mesh(dict(self.defaults, body_length_cm=40))
        long = self.provider.mesh(dict(self.defaults, body_length_cm=120))
        narrow = self.provider.mesh(dict(self.defaults, body_width_cm=10))
        wide = self.provider.mesh(dict(self.defaults, body_width_cm=50))
        low = self.provider.mesh(dict(self.defaults, shoulder_height_cm=20))
        tall = self.provider.mesh(dict(self.defaults, shoulder_height_cm=90))

        self.assertGreater(long.bounds_cm[1][1] - long.bounds_cm[0][1],
                           short.bounds_cm[1][1] - short.bounds_cm[0][1])
        self.assertGreater(wide.bounds_cm[1][0] - wide.bounds_cm[0][0],
                           narrow.bounds_cm[1][0] - narrow.bounds_cm[0][0])
        self.assertGreater(tall.bounds_cm[1][2], low.bounds_cm[1][2])

    def test_tail_length_changes_rear_extent(self):
        short_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=5))
        long_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=80))
        self.assertLess(long_tail.bounds_cm[0][1], short_tail.bounds_cm[0][1])

    def test_invalid_parameters_are_rejected(self):
        for field in self.provider.parameters:
            for value in (True, "bad", float("nan"), field.minimum - 1, field.maximum + 1):
                values = dict(self.defaults)
                values[field.key] = value
                with self.subTest(parameter=field.key, value=value):
                    with self.assertRaises((TypeError, ValueError)):
                        self.provider.mesh(values)


if __name__ == "__main__":
    unittest.main()
