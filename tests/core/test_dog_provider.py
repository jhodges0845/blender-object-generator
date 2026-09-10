# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.models import ObjectMesh, Skeleton
from object_core.objects import get_provider


class DogProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("dog")
        self.defaults = {field.key: field.default for field in self.provider.parameters}

    def test_dog_provider_declares_initial_deforming_rig_capabilities(self):
        self.assertEqual(self.provider.label, "Dog")
        self.assertTrue(self.provider.supports_rig)
        self.assertFalse(self.provider.supports_idle)
        self.assertFalse(self.provider.supports_locomotion)
        self.assertTrue(self.provider.uses_skin_weights)
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

    def test_quadruped_skeleton_is_deterministic_and_parented(self):
        skeleton = self.provider.skeleton(self.defaults)
        self.assertIsInstance(skeleton, Skeleton)
        self.assertEqual(skeleton, self.provider.skeleton(self.defaults))
        names = [bone.name for bone in skeleton.bones]
        self.assertEqual(names[:4], ["root", "spine", "neck", "head"])
        for name in ("fore_upper.left", "fore_lower.left", "fore_upper.right", "fore_lower.right",
                     "hind_upper.left", "hind_lower.left", "hind_upper.right", "hind_lower.right",
                     "tail.1", "tail.2", "tail.3"):
            self.assertIn(name, names)
        by_name = {bone.name: bone for bone in skeleton.bones}
        self.assertEqual(by_name["fore_lower.left"].parent, "fore_upper.left")
        self.assertEqual(by_name["hind_lower.right"].parent, "hind_upper.right")
        self.assertEqual(by_name["tail.3"].parent, "tail.2")

    def test_skin_weights_cover_every_vertex_and_stay_local(self):
        mesh = self.provider.mesh(self.defaults)
        skeleton = self.provider.skeleton(self.defaults)
        weights = self.provider.skin_weights(mesh, self.defaults)
        self.assertEqual({item.part_name for item in weights}, {part.name for part in mesh.parts})
        bone_names = {bone.name for bone in skeleton.bones}
        by_part = {item.part_name: item for item in weights}
        for part in mesh.parts:
            rows = by_part[part.name].vertices
            self.assertEqual(len(rows), len(part.vertices))
            for influences in rows:
                self.assertAlmostEqual(sum(item.weight for item in influences), 1.0)
                self.assertTrue(all(item.bone_name in bone_names for item in influences))
        fore = by_part["dog_foreleg_left"].vertices
        self.assertEqual({i.bone_name for row in fore for i in row}, {"fore_upper.left", "fore_lower.left"})
        self.assertEqual({i.bone_name for row in by_part["dog_tail_2"].vertices for i in row}, {"tail.2"})

    def test_invalid_parameters_are_rejected(self):
        for field in self.provider.parameters:
            for value in (True, "bad", float("nan"), field.minimum - 1, field.maximum + 1):
                values = dict(self.defaults)
                values[field.key] = value
                with self.subTest(parameter=field.key, value=value):
                    with self.assertRaises((TypeError, ValueError)):
                        self.provider.mesh(values)
                    with self.assertRaises((TypeError, ValueError)):
                        self.provider.skeleton(values)


if __name__ == "__main__":
    unittest.main()
