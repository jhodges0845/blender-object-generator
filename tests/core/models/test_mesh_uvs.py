# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core import MeshPart


class MeshUVContractTests(unittest.TestCase):
    def test_uvs_are_optional_for_existing_mesh_producers(self):
        part = MeshPart("triangle", ((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1, 2),))
        self.assertEqual(part.uvs, ())

    def test_uvs_preserve_one_coordinate_per_face_corner(self):
        part = MeshPart(
            "triangle",
            ((0, 0, 0), (1, 0, 0), (0, 1, 0)),
            ((0, 1, 2),),
            (((0, 0), (1, 0), (0, 1)),),
        )
        self.assertEqual(part.uvs, (((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)),))

    def test_uvs_reject_mismatched_or_invalid_data(self):
        vertices = ((0, 0, 0), (1, 0, 0), (0, 1, 0))
        faces = ((0, 1, 2),)
        with self.assertRaisesRegex(ValueError, "one entry per face"):
            MeshPart("triangle", vertices, faces, (((0, 0), (1, 0), (0, 1)), ((0, 0),) * 3))
        with self.assertRaisesRegex(ValueError, "corner count"):
            MeshPart("triangle", vertices, faces, (((0, 0), (1, 0)),))
        with self.assertRaisesRegex(ValueError, "two values"):
            MeshPart("triangle", vertices, faces, (((0, 0, 0), (1, 0), (0, 1)),))
        with self.assertRaisesRegex(ValueError, "finite"):
            MeshPart("triangle", vertices, faces, (((float("nan"), 0), (1, 0), (0, 1)),))
        with self.assertRaisesRegex(TypeError, "numbers"):
            MeshPart("triangle", vertices, faces, ((("0", 0), (1, 0), (0, 1)),))


if __name__ == "__main__":
    unittest.main()
