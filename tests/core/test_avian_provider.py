# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.models import ObjectMesh
from object_core.objects import get_provider


class AvianProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_provider("avian")
        self.defaults = {field.key: field.default for field in self.provider.parameters}

    def test_avian_identity_and_deforming_foundation_capabilities(self):
        self.assertEqual(self.provider.key, "avian")
        self.assertEqual(self.provider.label, "Avian")
        self.assertTrue(self.provider.supports_rig)
        self.assertFalse(self.provider.supports_idle)
        self.assertFalse(self.provider.supports_locomotion)
        self.assertFalse(self.provider.supports_run)
        self.assertTrue(self.provider.uses_skin_weights)
        self.assertTrue(self.provider.supports_materials)

    def test_default_avian_surface_is_connected_deterministic_and_editable(self):
        mesh = self.provider.mesh(self.defaults)
        self.assertIsInstance(mesh, ObjectMesh)
        self.assertEqual(mesh, self.provider.mesh(self.defaults))
        self.assertEqual(tuple(part.name for part in mesh.parts), ("avian",))
        self.assertGreater(mesh.vertex_count, 80)
        self.assertGreater(mesh.face_count, 70)
        part = mesh.parts[0]
        referenced = {index for face in part.faces for index in face}
        self.assertEqual(referenced, set(range(len(part.vertices))))

    def test_avian_surface_has_deterministic_unit_uvs(self):
        part = self.provider.mesh(self.defaults).parts[0]
        self.assertEqual(len(part.face_uvs), len(part.faces))
        for face, uvs in zip(part.faces, part.face_uvs):
            self.assertEqual(len(uvs), len(face))
            for u, v in uvs:
                self.assertGreaterEqual(u, 0.0)
                self.assertLessEqual(u, 1.0)
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.0)

    def test_avian_material_intent_is_portable_and_deterministic(self):
        materials = self.provider.materials(self.defaults)
        self.assertEqual(materials, self.provider.materials(self.defaults))
        self.assertEqual(len(materials), 1)
        material = materials[0]
        self.assertEqual(material.name, "Avian Base Plumage")
        self.assertEqual(material.parts, ("avian",))
        self.assertEqual(material.metallic, 0.0)
        self.assertGreater(material.roughness, 0.6)
        self.assertIsNotNone(material.base_color_texture)
        self.assertEqual(material.base_color_texture.name, "Avian Plumage Texture")
        self.assertEqual((material.base_color_texture.width, material.base_color_texture.height), (2, 2))

    def test_wingspan_parameter_controls_lateral_extent(self):
        narrow = self.provider.mesh(dict(self.defaults, wingspan_cm=50))
        wide = self.provider.mesh(dict(self.defaults, wingspan_cm=180))
        narrow_width = narrow.bounds_cm[1][0] - narrow.bounds_cm[0][0]
        wide_width = wide.bounds_cm[1][0] - wide.bounds_cm[0][0]
        self.assertGreater(wide_width, narrow_width)
        self.assertGreater(wide_width, 170)
        self.assertLess(narrow_width, 70)

    def test_body_and_tail_dimensions_control_expected_axes(self):
        short_body = self.provider.mesh(dict(self.defaults, body_length_cm=25))
        long_body = self.provider.mesh(dict(self.defaults, body_length_cm=90))
        short_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=6))
        long_tail = self.provider.mesh(dict(self.defaults, tail_length_cm=70))
        low = self.provider.mesh(dict(self.defaults, body_height_cm=8))
        tall = self.provider.mesh(dict(self.defaults, body_height_cm=50))

        self.assertGreater(long_body.bounds_cm[1][1], short_body.bounds_cm[1][1])
        self.assertLess(long_tail.bounds_cm[0][1], short_tail.bounds_cm[0][1])
        self.assertGreater(tall.bounds_cm[1][2], low.bounds_cm[1][2])

    def test_skeleton_contains_spine_wings_and_tail_chain(self):
        skeleton = self.provider.skeleton(self.defaults)
        names = {bone.name for bone in skeleton.bones}
        self.assertTrue({"root", "spine", "neck", "head", "wing.upper.left", "wing.lower.left",
                         "wing.upper.right", "wing.lower.right", "tail.1", "tail.2"}.issubset(names))
        self.assertEqual(next(b for b in skeleton.bones if b.name == "wing.lower.left").parent,
                         "wing.upper.left")
        self.assertEqual(next(b for b in skeleton.bones if b.name == "tail.2").parent, "tail.1")
        self.assertEqual(skeleton, self.provider.skeleton(self.defaults))

    def test_skin_weights_cover_surface_are_normalized_and_side_local(self):
        mesh = self.provider.mesh(self.defaults)
        weights = self.provider.skin_weights(mesh, self.defaults)
        self.assertEqual(tuple(weight.part_name for weight in weights), ("avian",))
        self.assertEqual(len(weights[0].vertices), len(mesh.parts[0].vertices))
        for vertex, influences in zip(mesh.parts[0].vertices, weights[0].vertices):
            self.assertAlmostEqual(sum(influence.weight for influence in influences), 1.0)
            self.assertLessEqual(len(influences), 4)
            opposite = ".right" if vertex[0] < 0 else ".left"
            self.assertFalse(any(influence.bone_name.endswith(opposite) for influence in influences))

    def test_invalid_parameters_are_rejected(self):
        for field in self.provider.parameters:
            for value in (True, "bad", float("nan"), field.minimum - 1, field.maximum + 1):
                values = dict(self.defaults)
                values[field.key] = value
                with self.subTest(parameter=field.key, value=value):
                    with self.assertRaises((TypeError, ValueError)):
                        self.provider.mesh(values)

    def test_wingspan_must_exceed_body_width(self):
        values = dict(self.defaults, body_width_cm=30, wingspan_cm=20)
        with self.assertRaisesRegex(ValueError, "Wingspan"):
            self.provider.mesh(values)


if __name__ == "__main__":
    unittest.main()
