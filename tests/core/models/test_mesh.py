# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import FrozenInstanceError, replace
import unittest

from object_core import ObjectMesh, MeshPart


class MeshContractTests(unittest.TestCase):
    def setUp(self):
        self.part = MeshPart("triangle", ((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1, 2),))

    def test_rejects_invalid_coordinates(self):
        for value in (float("nan"), float("inf"), 10**1000):
            with self.assertRaisesRegex(ValueError, "finite"):
                replace(self.part, vertices=((value, 0, 0),) + self.part.vertices[1:])
        for value in (True, "1", None):
            with self.assertRaisesRegex(TypeError, "numbers"):
                replace(self.part, vertices=((value, 0, 0),) + self.part.vertices[1:])
        with self.assertRaisesRegex(ValueError, "three"):
            replace(self.part, vertices=((0, 0),))

    def test_rejects_invalid_faces(self):
        for face in ((0, 1), (0, 1, 1), (-1, 1, 2), (0, 1, 3)):
            with self.subTest(face=face), self.assertRaises(ValueError):
                replace(self.part, faces=(face,))
        for face in ((False, 1, 2), (0.0, 1, 2)):
            with self.assertRaises(TypeError):
                replace(self.part, faces=(face,))

    def test_rejects_empty_data_and_duplicate_names(self):
        for change in ({"vertices": ()}, {"faces": ()}, {"name": " "}):
            with self.assertRaises(ValueError):
                replace(self.part, **change)
        with self.assertRaises(ValueError):
            ObjectMesh(())
        with self.assertRaisesRegex(ValueError, "unique"):
            ObjectMesh((self.part, self.part))
        with self.assertRaises(TypeError):
            ObjectMesh((None,))

    def test_copies_mutable_input_and_is_immutable(self):
        vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
        faces = [[0, 1, 2]]
        part = MeshPart("triangle", vertices, faces)
        parts = [part]
        mesh = ObjectMesh(parts)
        vertices[0][0] = 99
        faces[0][0] = 99
        parts.clear()
        self.assertEqual(mesh.parts, (self.part,))
        with self.assertRaises(FrozenInstanceError):
            part.name = "changed"

    def test_counts_and_bounds(self):
        mesh = ObjectMesh((self.part,))
        self.assertEqual(mesh.vertex_count, 3)
        self.assertEqual(mesh.face_count, 1)
        self.assertEqual(mesh.bounds_cm, ((0, 0, 0), (1, 1, 0)))
