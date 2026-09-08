# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import replace
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.proportions.landmarks import generate_landmarks


class DeformableHumanGeometryTests(unittest.TestCase):
    def test_shoulders_and_hips_are_one_surface(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(p)
        self.assertEqual(len(mesh.parts), 1)
        self.assertEqual(mesh.parts[0].name, "human")
        self.assertGreater(mesh.vertex_count, 0)
        self.assertGreater(mesh.face_count, 0)

    def test_height_and_symmetry_are_preserved(self):
        for height in (120, 180, 240):
            with self.subTest(height=height):
                p = generate_proportions(HumanoidSpec(height, 95, BodyType.AVERAGE))
                mesh = generate_deformable_mesh(p)
                minimum, maximum = mesh.bounds_cm
                self.assertAlmostEqual(minimum[2], 0)
                self.assertAlmostEqual(maximum[2], height)
                self.assertAlmostEqual(minimum[0], -maximum[0])

    def test_body_type_changes_shape_without_changing_topology(self):
        spec = HumanoidSpec(180, 95, BodyType.SLIM)
        slim = generate_deformable_mesh(generate_proportions(spec))
        obese = generate_deformable_mesh(
            generate_proportions(replace(spec, body_type=BodyType.OBESE))
        )
        self.assertNotEqual(slim.parts[0].vertices, obese.parts[0].vertices)
        self.assertEqual(slim.parts[0].faces, obese.parts[0].faces)
        self.assertEqual(len(slim.parts[0].vertices), len(obese.parts[0].vertices))

    def test_unified_surface_retains_joint_support_geometry(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        part = generate_deformable_mesh(p).parts[0]
        self.assertGreater(len(part.vertices), 400)

    def test_hands_have_palm_volume_and_tapered_fingertips(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        points = generate_landmarks(p)
        part = generate_deformable_mesh(p).parts[0]
        wrist = points["wrist.left"]
        fingertips = points["fingertips.left"]
        hand_axis = tuple(fingertips[i] - wrist[i] for i in range(3))
        hand_length_sq = sum(value * value for value in hand_axis)

        def along_hand(vertex):
            offset = tuple(vertex[i] - wrist[i] for i in range(3))
            return sum(offset[i] * hand_axis[i] for i in range(3)) / hand_length_sq

        def radial_distance(vertex, amount):
            center = tuple(wrist[i] + hand_axis[i] * amount for i in range(3))
            return sum((vertex[i] - center[i]) ** 2 for i in range(3)) ** 0.5

        palm_vertices = [v for v in part.vertices if abs(along_hand(v) - 0.42) < 1e-6]
        tip_vertices = [v for v in part.vertices if abs(along_hand(v) - 1.0) < 1e-6]
        self.assertGreaterEqual(len(palm_vertices), 8)
        self.assertGreaterEqual(len(tip_vertices), 8)

        palm_radius = max(radial_distance(v, 0.42) for v in palm_vertices)
        tip_radius = max(radial_distance(v, 1.0) for v in tip_vertices)
        self.assertGreater(palm_radius, tip_radius)

    def test_feet_have_heel_ball_and_tapered_toe_sections(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        points = generate_landmarks(p)
        part = generate_deformable_mesh(p).parts[0]
        ankle_x = points["ankle.left"][0]
        ball_y = p.foot_length_cm * 0.56
        toe_y = p.foot_length_cm * 0.82

        ball_vertices = [
            v for v in part.vertices
            if abs(v[1] - ball_y) < 1e-6 and v[0] > 0
        ]
        toe_vertices = [
            v for v in part.vertices
            if abs(v[1] - toe_y) < 1e-6 and v[0] > 0
        ]
        self.assertGreaterEqual(len(ball_vertices), 4)
        self.assertGreaterEqual(len(toe_vertices), 4)
        self.assertTrue(any(abs(v[0] - ankle_x) > 1e-3 for v in ball_vertices))

        ball_width = max(v[0] for v in ball_vertices) - min(v[0] for v in ball_vertices)
        toe_width = max(v[0] for v in toe_vertices) - min(v[0] for v in toe_vertices)
        ball_height = max(v[2] for v in ball_vertices) - min(v[2] for v in ball_vertices)
        toe_height = max(v[2] for v in toe_vertices) - min(v[2] for v in toe_vertices)
        self.assertGreater(ball_width, toe_width)
        self.assertGreater(ball_height, toe_height)

    def test_feet_remain_integrated_and_above_ground(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        part = generate_deformable_mesh(p).parts[0]
        minimum_y = min(vertex[1] for vertex in part.vertices)
        maximum_y = max(vertex[1] for vertex in part.vertices)
        minimum_z = min(vertex[2] for vertex in part.vertices)
        self.assertLess(minimum_y, 0)
        self.assertGreater(maximum_y, p.foot_length_cm * 0.75)
        self.assertAlmostEqual(minimum_z, 0)

    def test_deterministic_and_requires_proportions(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        self.assertEqual(generate_deformable_mesh(p), generate_deformable_mesh(p))
        with self.assertRaisesRegex(TypeError, "HumanoidProportions"):
            generate_deformable_mesh(HumanoidSpec(180, 95, BodyType.AVERAGE))


if __name__ == "__main__":
    unittest.main()
