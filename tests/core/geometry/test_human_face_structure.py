# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.proportions.landmarks import generate_landmarks


class HumanFaceStructureTests(unittest.TestCase):
    def setUp(self):
        self.proportions = generate_proportions(
            HumanoidSpec(180, 95, BodyType.AVERAGE)
        )
        self.part = generate_deformable_mesh(self.proportions).parts[0]
        points = generate_landmarks(self.proportions)
        self.chin_z = points["chin"][2]

    def _front_y_near(self, level, tolerance=0.015):
        target_z = self.chin_z + self.proportions.head_height_cm * level
        vertices = [
            vertex for vertex in self.part.vertices
            if abs(vertex[2] - target_z) <= self.proportions.head_height_cm * tolerance
        ]
        self.assertTrue(vertices, "expected a generated head ring near requested level")
        return max(vertex[1] for vertex in vertices)

    def test_nose_projects_forward_of_eye_plane(self):
        nose = self._front_y_near(0.38)
        eyes = self._front_y_near(0.52)
        self.assertGreater(nose, eyes)

    def test_brow_projects_forward_of_eye_plane(self):
        eyes = self._front_y_near(0.52)
        brow = self._front_y_near(0.66)
        self.assertGreater(brow, eyes)

    def test_lower_face_and_forehead_remain_distinct(self):
        chin = self._front_y_near(0.12)
        forehead = self._front_y_near(0.80)
        nose = self._front_y_near(0.38)
        self.assertGreater(nose, chin)
        self.assertGreater(nose, forehead)

    def test_face_structure_preserves_left_right_symmetry(self):
        vertices = self.part.vertices
        for x, y, z in vertices:
            mirror = (-x, y, z)
            self.assertTrue(
                any(
                    abs(other[0] - mirror[0]) < 1e-7
                    and abs(other[1] - mirror[1]) < 1e-7
                    and abs(other[2] - mirror[2]) < 1e-7
                    for other in vertices
                )
            )

    def test_face_structure_preserves_standing_height_and_ground(self):
        minimum, maximum = generate_deformable_mesh(self.proportions).bounds_cm
        self.assertAlmostEqual(minimum[2], 0.0)
        self.assertAlmostEqual(maximum[2], 180.0)


if __name__ == "__main__":
    unittest.main()
