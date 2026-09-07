# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import replace
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh


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
        # The unified mesh should be substantially denser than the 72-vertex
        # torso because all four supported limb chains are now stitched in.
        self.assertGreater(len(part.vertices), 300)

    def test_feet_remain_integrated_and_above_ground(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        part = generate_deformable_mesh(p).parts[0]
        minimum_y = min(vertex[1] for vertex in part.vertices)
        maximum_y = max(vertex[1] for vertex in part.vertices)
        minimum_z = min(vertex[2] for vertex in part.vertices)
        self.assertLess(minimum_y, 0)
        self.assertGreater(maximum_y, p.foot_length_cm * 0.5)
        self.assertAlmostEqual(minimum_z, 0)

    def test_deterministic_and_requires_proportions(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        self.assertEqual(generate_deformable_mesh(p), generate_deformable_mesh(p))
        with self.assertRaisesRegex(TypeError, "HumanoidProportions"):
            generate_deformable_mesh(HumanoidSpec(180, 95, BodyType.AVERAGE))


if __name__ == "__main__":
    unittest.main()
