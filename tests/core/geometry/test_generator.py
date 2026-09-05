from collections import Counter
from dataclasses import replace
from math import isfinite
import unittest

from humanoid_core import BodyType, HumanoidSpec, generate_mesh, generate_proportions


def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])


class MeshGeneratorTests(unittest.TestCase):
    def test_supported_grid_geometry(self):
        for height in (120, 180, 240):
            for weight in (30, 95, 300):
                for preset in BodyType:
                    with self.subTest(height=height, weight=weight, preset=preset):
                        mesh = generate_mesh(generate_proportions(HumanoidSpec(height, weight, preset)))
                        minimum, maximum = mesh.bounds_cm
                        self.assertAlmostEqual(minimum[2], 0)
                        self.assertAlmostEqual(maximum[2], height)
                        self.assertAlmostEqual(minimum[0], -maximum[0])
                        for part in mesh.parts:
                            self.check_closed_outward_part(part)

    def check_closed_outward_part(self, part):
        edges = Counter()
        volume_times_six = 0.0
        used = set()
        for vertex in part.vertices:
            self.assertTrue(all(isfinite(value) for value in vertex))
        for face in part.faces:
            self.assertEqual(len(set(face)), len(face))
            self.assertTrue(all(0 <= index < len(part.vertices) for index in face))
            used.update(face)
            for a, b in zip(face, face[1:] + face[:1]):
                edges[a, b] += 1
            origin = part.vertices[face[0]]
            for i in range(1, len(face) - 1):
                b, c = part.vertices[face[i]], part.vertices[face[i + 1]]
                ab = tuple(b[j] - origin[j] for j in range(3))
                ac = tuple(c[j] - origin[j] for j in range(3))
                normal = cross(ab, ac)
                self.assertGreater(sum(value * value for value in normal), 1e-12)
                volume_times_six += sum(origin[j] * cross(b, c)[j] for j in range(3))
        self.assertEqual(used, set(range(len(part.vertices))))
        for (a, b), count in edges.items():
            self.assertEqual(count, 1)
            self.assertEqual(edges[b, a], 1)
        self.assertGreater(volume_times_six, 0, part.name)

    def test_named_parts_and_mirror_symmetry(self):
        mesh = generate_mesh(generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE)))
        parts = {part.name: part for part in mesh.parts}
        paired = ("upper_arm", "forearm", "hand", "upper_leg", "lower_leg", "foot")
        expected = {"head", "neck", "torso"} | {
            f"{name}.{side}" for name in paired for side in ("left", "right")
        }
        self.assertEqual(set(parts), expected)
        def points(part, mirror=False):
            return {tuple(round(value, 8) for value in ((-x if mirror else x), y, z))
                    for x, y, z in part.vertices}
        for name in paired:
            self.assertEqual(points(parts[name + ".left"], True), points(parts[name + ".right"]))
        for name in ("head", "neck", "torso"):
            self.assertEqual(points(parts[name], True), points(parts[name]))

    def test_body_shape_changes_mesh_without_changing_topology(self):
        spec = HumanoidSpec(180, 95, BodyType.SLIM)
        slim = generate_mesh(generate_proportions(spec))
        obese = generate_mesh(generate_proportions(replace(spec, body_type=BodyType.OBESE)))
        self.assertNotEqual(slim.parts[0].vertices, obese.parts[0].vertices)
        for a, b in zip(slim.parts, obese.parts):
            self.assertEqual(a.name, b.name)
            self.assertEqual(a.faces, b.faces)
            self.assertEqual(len(a.vertices), len(b.vertices))

    def test_segment_lengths_and_a_pose(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_mesh(p)
        expected_lengths = {"upper_arm": p.upper_arm_length_cm, "forearm": p.forearm_length_cm,
                            "hand": p.hand_length_cm, "upper_leg": p.upper_leg_length_cm,
                            "lower_leg": p.lower_leg_length_cm}
        for part in mesh.parts:
            name = part.name.split(".")[0]
            if name not in expected_lengths:
                continue
            half = len(part.vertices) // 2
            centers = [tuple(sum(v[axis] for v in ring) / len(ring) for axis in range(3))
                       for ring in (part.vertices[:half], part.vertices[half:])]
            delta = tuple(b - a for a, b in zip(*centers))
            length = sum(value ** 2 for value in delta) ** 0.5
            self.assertAlmostEqual(length, expected_lengths[name])
            if name in ("upper_arm", "forearm", "hand"):
                self.assertLess(delta[2], 0)
                self.assertAlmostEqual(abs(delta[0]) / length, 0.5)

    def test_uniform_scaling(self):
        small = generate_mesh(generate_proportions(HumanoidSpec(160, 60, BodyType.MUSCULAR)))
        large = generate_mesh(generate_proportions(HumanoidSpec(200, 60 * 1.25**3, BodyType.MUSCULAR)))
        for a, b in zip(small.parts, large.parts):
            for va, vb in zip(a.vertices, b.vertices):
                for ca, cb in zip(va, vb):
                    self.assertAlmostEqual(cb, ca * 1.25)

    def test_deterministic_without_changing_proportions(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        before = replace(p)
        self.assertEqual(generate_mesh(p), generate_mesh(p))
        self.assertEqual(before, p)

    def test_requires_proportions(self):
        with self.assertRaisesRegex(TypeError, "HumanoidProportions"):
            generate_mesh(HumanoidSpec(180, 95, BodyType.AVERAGE))
