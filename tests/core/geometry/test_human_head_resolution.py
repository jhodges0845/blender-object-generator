# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.proportions.landmarks import generate_landmarks


class HumanHeadResolutionTests(unittest.TestCase):
    def test_head_has_multiple_profile_sections_between_chin_and_crown(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        points = generate_landmarks(proportions)
        part = generate_deformable_mesh(proportions).parts[0]
        chin_z = points["chin"][2]
        crown_z = points["crown"][2]

        head_levels = sorted({
            round(vertex[2], 6)
            for vertex in part.vertices
            if chin_z <= vertex[2] <= crown_z
        })
        self.assertGreaterEqual(len(head_levels), 9)

    def test_head_profile_tapers_from_mid_head_to_crown(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        points = generate_landmarks(proportions)
        part = generate_deformable_mesh(proportions).parts[0]
        chin_z = points["chin"][2]
        mid_z = chin_z + proportions.head_height_cm * 0.52
        crown_z = points["crown"][2]

        def width_at(level):
            vertices = [v for v in part.vertices if abs(v[2] - level) < 1e-6]
            self.assertGreaterEqual(len(vertices), 8)
            return max(v[0] for v in vertices) - min(v[0] for v in vertices)

        self.assertGreater(width_at(mid_z), width_at(crown_z))

    def test_new_head_profile_remains_symmetric(self):
        proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        part = generate_deformable_mesh(proportions).parts[0]
        minimum, maximum = generate_deformable_mesh(proportions).bounds_cm
        self.assertAlmostEqual(minimum[0], -maximum[0])
        self.assertAlmostEqual(max(vertex[2] for vertex in part.vertices), proportions.standing_height_cm)


if __name__ == "__main__":
    unittest.main()
