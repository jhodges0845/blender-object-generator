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

    def test_weights_only_blend_across_connected_joints(self):
        mesh, skeleton = self._fixture()
        weights = generate_skin_weights(mesh, skeleton)[0]
        bones = {bone.name: bone for bone in skeleton.bones}
        children = {}
        for bone in skeleton.bones:
            children.setdefault(bone.parent, set()).add(bone.name)

        for influences in weights.vertices:
            names = {item.bone_name for item in influences}
            for name in names:
                connected = {name, bones[name].parent} | children.get(name, set())
                self.assertTrue(
                    names <= connected,
                    "unconnected influences found: {}".format(sorted(names)),
                )

    def test_max_influences_is_validated(self):
        mesh, skeleton = self._fixture()
        with self.assertRaisesRegex(ValueError, "at least 1"):
            generate_skin_weights(mesh, skeleton, max_influences=0)
        with self.assertRaises(TypeError):
            generate_skin_weights(mesh, skeleton, max_influences=True)


if __name__ == "__main__":
    unittest.main()
