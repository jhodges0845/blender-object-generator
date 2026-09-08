# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh


class HumanUVGenerationTests(unittest.TestCase):
    def _part(self, height=180, body_type=BodyType.AVERAGE):
        proportions = generate_proportions(HumanoidSpec(height, 95, body_type))
        return generate_deformable_mesh(proportions).parts[0]

    def test_human_generates_complete_uvs_inside_unit_square(self):
        part = self._part()
        self.assertEqual(len(part.uvs), len(part.faces))
        for face, face_uvs in zip(part.faces, part.uvs):
            self.assertEqual(len(face_uvs), len(face))
            for u, v in face_uvs:
                self.assertGreaterEqual(u, 0.0)
                self.assertLessEqual(u, 1.0)
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.0)

    def test_uv_generation_is_deterministic_and_topology_stable(self):
        first = self._part()
        second = self._part()
        self.assertEqual(first.uvs, second.uvs)
        for body_type in BodyType:
            with self.subTest(body_type=body_type):
                part = self._part(body_type=body_type)
                self.assertEqual(len(part.uvs), len(first.uvs))
                self.assertEqual(tuple(len(face) for face in part.uvs),
                                 tuple(len(face) for face in first.uvs))

    def test_uv_generation_survives_supported_height_extremes(self):
        for height in (120, 240):
            with self.subTest(height=height):
                part = self._part(height=height)
                self.assertEqual(len(part.uvs), len(part.faces))
                self.assertTrue(all(face_uvs for face_uvs in part.uvs))


if __name__ == "__main__":
    unittest.main()
