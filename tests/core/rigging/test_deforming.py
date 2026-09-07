# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.rigging import generate_deforming_skeleton, generate_skin_weights


class DeformingRigTests(unittest.TestCase):
    def _fixture(self):
        p = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
        mesh = generate_deformable_mesh(p)
        skeleton = generate_deforming_skeleton(p)
        return mesh, skeleton

    def test_deforming_skeleton_has_no_rigid_part_bindings(self):
        _, skeleton = self._fixture()
        self.assertEqual(len(skeleton.bones), 16)
        self.assertTrue(all(bone.part_name is None for bone in skeleton.bones))
        self.assertEqual(skeleton.bones[0].name, "root")

    def test_unified_human_receives_normalized_vertex_weights(self):
        mesh, skeleton = self._fixture()
        weights = generate_skin_weights(mesh, skeleton)
        self.assertEqual(len(weights), 1)
        self.assertEqual(weights[0].part_name, "human")
        self.assertEqual(len(weights[0].vertices), len(mesh.parts[0].vertices))
        for influences in weights[0].vertices:
            self.assertGreaterEqual(len(influences), 1)
            self.assertLessEqual(len(influences), 4)
            self.assertAlmostEqual(sum(item.weight for item in influences), 1.0)

    def test_skin_weights_are_deterministic(self):
        mesh, skeleton = self._fixture()
        self.assertEqual(
            generate_skin_weights(mesh, skeleton),
            generate_skin_weights(mesh, skeleton),
        )

    def test_limb_vertices_do_not_cross_influence_sides(self):
        mesh, skeleton = self._fixture()
        weights = generate_skin_weights(mesh, skeleton)[0]
        for vertex, influences in zip(mesh.parts[0].vertices, weights.vertices):
            forbidden = ".right" if vertex[0] > 1e-6 else ".left" if vertex[0] < -1e-6 else None
            if forbidden:
                self.assertTrue(all(not item.bone_name.endswith(forbidden) for item in influences))

    def test_weights_only_blend_within_one_joint_neighborhood(self):
        mesh, skeleton = self._fixture()
        weights = generate_skin_weights(mesh, skeleton)[0]
        children = {}
        for bone in skeleton.bones:
            children.setdefault(bone.parent, set()).add(bone.name)

        neighborhoods = []
        for bone in skeleton.bones:
            if bone.name == "root":
                continue
            neighborhood = {bone.name}
            if bone.parent and bone.parent != "root":
                neighborhood.add(bone.parent)
            neighborhood.update(children.get(bone.name, set()))
            neighborhoods.append(neighborhood)
        neighborhoods.extend((
            {"torso", "upper_leg.left", "lower_leg.left"},
            {"torso", "upper_leg.right", "lower_leg.right"},
        ))

        for influences in weights.vertices:
            names = {item.bone_name for item in influences}
            self.assertTrue(
                any(names <= neighborhood for neighborhood in neighborhoods),
                "unconnected influences found: {}".format(sorted(names)),
            )

    def test_each_hip_has_torso_upper_leg_blending(self):
        mesh, skeleton = self._fixture()
        weights = generate_skin_weights(mesh, skeleton)[0]
        for side, sign in (("left", 1), ("right", -1)):
            upper_leg = "upper_leg." + side
            blended = []
            for vertex, influences in zip(mesh.parts[0].vertices, weights.vertices):
                names = {item.bone_name for item in influences}
                if sign * vertex[0] > 1e-6 and {"torso", upper_leg} <= names:
                    blended.append((vertex, names))
            self.assertTrue(blended, "{} hip has no torso/upper-leg blend".format(side))
            forbidden = "upper_leg.right" if side == "left" else "upper_leg.left"
            self.assertTrue(all(forbidden not in names for _vertex, names in blended))

    def test_max_influences_is_validated(self):
        mesh, skeleton = self._fixture()
        with self.assertRaisesRegex(ValueError, "at least 1"):
            generate_skin_weights(mesh, skeleton, max_influences=0)
        with self.assertRaises(TypeError):
            generate_skin_weights(mesh, skeleton, max_influences=True)


if __name__ == "__main__":
    unittest.main()
