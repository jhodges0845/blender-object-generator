# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import replace
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh


class DeformableHumanGeometryTests(unittest.TestCase):
    def test_foundation_reduces_rigid_part_seams(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(p)
        self.assertEqual(
            {part.name for part in mesh.parts},
            {"body", "arm.left", "arm.right", "leg.left", "leg.right", "foot.left", "foot.right"},
        )
        # Human 1.0 starts by replacing torso/neck/head and segmented limbs
        # with continuous quad chains while the rigid generator stays intact.
        self.assertEqual(len(mesh.parts), 7)
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
        for a, b in zip(slim.parts, obese.parts):
            self.assertEqual(a.name, b.name)
            self.assertEqual(a.faces, b.faces)
            self.assertEqual(len(a.vertices), len(b.vertices))

    def test_joint_chains_have_internal_deformation_loops(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        parts = {part.name: part for part in generate_deformable_mesh(p).parts}
        # Eight vertices per ring: shoulder/elbow/wrist/hand and hip/knee/ankle.
        self.assertEqual(len(parts["arm.left"].vertices), 32)
        self.assertEqual(len(parts["leg.left"].vertices), 24)
        self.assertEqual(len(parts["body"].vertices), 72)

    def test_deterministic_and_requires_proportions(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        self.assertEqual(generate_deformable_mesh(p), generate_deformable_mesh(p))
        with self.assertRaisesRegex(TypeError, "HumanoidProportions"):
            generate_deformable_mesh(HumanoidSpec(180, 95, BodyType.AVERAGE))


if __name__ == "__main__":
    unittest.main()
