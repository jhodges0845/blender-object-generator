# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_asset
from blender_adapter.materials import material_issues, prepare_materials
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class QuadrupedGeneratedMaterialTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

    def _quadruped(self):
        provider = get_provider("quadruped")
        values = {field.key: field.default for field in provider.parameters}
        root = create_asset(provider.mesh(values), name="MaterialQuadruped")
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root, provider, values

    def test_prepare_uses_portable_quadruped_coat_and_texture(self):
        root, provider, values = self._quadruped()
        created = prepare_materials(root)
        mesh = next(obj for obj in root.children if obj.type == "MESH")
        expected = provider.materials(values)[0]
        self.assertIsNotNone(created)
        self.assertEqual(len(mesh.material_slots), 1)
        material = mesh.material_slots[0].material
        self.assertEqual(material.name, expected.name)
        shader = material.node_tree.nodes.get("Principled BSDF")
        self.assertAlmostEqual(shader.inputs["Metallic"].default_value, 0.0)
        self.assertAlmostEqual(shader.inputs["Roughness"].default_value, expected.roughness)
        self.assertTrue(shader.inputs["Base Color"].is_linked)
        texture = shader.inputs["Base Color"].links[0].from_node
        self.assertEqual(texture.type, "TEX_IMAGE")
        self.assertEqual(tuple(texture.image.size), (2, 2))
        self.assertTrue(texture.image.packed_file or getattr(texture.image, "packed_files", ()))
        self.assertTrue(mesh.data.uv_layers.get("UVMap"))
        self.assertFalse(material_issues((mesh,)))

    def test_prepare_preserves_existing_artist_material(self):
        root, _provider, _values = self._quadruped()
        mesh = next(obj for obj in root.children if obj.type == "MESH")
        artist = bpy.data.materials.new("Artist Quadruped Coat")
        mesh.data.materials.append(artist)
        for face in mesh.data.polygons:
            face.material_index = 0
        self.assertIsNone(prepare_materials(root))
        self.assertIs(mesh.material_slots[0].material, artist)


if __name__ == "__main__":
    unittest.main()
