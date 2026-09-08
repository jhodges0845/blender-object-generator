# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import FrozenInstanceError
import unittest

from object_core.models import ImageTextureSpec, MaterialSpec


class MaterialSpecTests(unittest.TestCase):
    def test_accepts_portable_pbr_values_texture_and_is_immutable(self):
        texture = ImageTextureSpec(
            "Base Texture", 1, 1, (0.5, 0.4, 0.3, 1.0)
        )
        material = MaterialSpec(
            "Base", ("human",), (0.5, 0.4, 0.3, 1.0), 0.0, 0.7, texture
        )
        self.assertEqual(material.part_names, ("human",))
        self.assertEqual(material.base_color, (0.5, 0.4, 0.3, 1.0))
        self.assertIs(material.base_color_texture, texture)
        with self.assertRaises(FrozenInstanceError):
            material.name = "Changed"

    def test_image_texture_validates_dimensions_pixels_and_is_immutable(self):
        pixels = [0.2, 0.3, 0.4, 1.0]
        texture = ImageTextureSpec("Texture", 1, 1, pixels)
        pixels[0] = 1.0
        self.assertEqual(texture.pixels, (0.2, 0.3, 0.4, 1.0))
        with self.assertRaises(FrozenInstanceError):
            texture.width = 2
        with self.assertRaises(ValueError):
            ImageTextureSpec("", 1, 1, (0.2, 0.3, 0.4, 1.0))
        with self.assertRaises(ValueError):
            ImageTextureSpec("Texture", 0, 1, ())
        with self.assertRaises(TypeError):
            ImageTextureSpec("Texture", True, 1, (0.2, 0.3, 0.4, 1.0))
        with self.assertRaises(ValueError):
            ImageTextureSpec("Texture", 1, 1, (0.2, 0.3, 0.4))
        with self.assertRaises(ValueError):
            ImageTextureSpec("Texture", 1, 1, (0.2, 0.3, float("nan"), 1.0))

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
        with self.assertRaises(TypeError):
            MaterialSpec("Base", ("human",), (0.5, 0.4, 0.3, 1.0), base_color_texture="texture.png")


if __name__ == "__main__":
    unittest.main()
