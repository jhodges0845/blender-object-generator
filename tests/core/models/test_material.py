# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import FrozenInstanceError
import unittest

from object_core.models import MaterialSpec


class MaterialSpecTests(unittest.TestCase):
    def test_accepts_portable_pbr_values_and_is_immutable(self):
        material = MaterialSpec("Base", ("human",), (0.5, 0.4, 0.3, 1.0), 0.0, 0.7)
        self.assertEqual(material.part_names, ("human",))
        self.assertEqual(material.base_color, (0.5, 0.4, 0.3, 1.0))
        with self.assertRaises(FrozenInstanceError):
            material.name = "Changed"

    def test_rejects_invalid_names_parts_and_values(self):
        with self.assertRaises(ValueError):
            MaterialSpec("", ("human",), (0.5, 0.4, 0.3, 1.0))
        with self.assertRaises(ValueError):
            MaterialSpec("Base", (), (0.5, 0.4, 0.3, 1.0))
        with self.assertRaises(ValueError):
            MaterialSpec("Base", ("human", "human"), (0.5, 0.4, 0.3, 1.0))
        with self.assertRaises(ValueError):
            MaterialSpec("Base", ("human",), (0.5, 0.4, 0.3))
        for value in (-0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MaterialSpec("Base", ("human",), (value, 0.4, 0.3, 1.0))
        with self.assertRaises(TypeError):
            MaterialSpec("Base", ("human",), (True, 0.4, 0.3, 1.0))


if __name__ == "__main__":
    unittest.main()
