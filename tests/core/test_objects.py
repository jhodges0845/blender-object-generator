# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from object_core.objects import OBJECT_TYPES, get_provider
from object_core.models.mesh import ObjectMesh


class ObjectProviderTests(unittest.TestCase):
    def test_providers_share_mesh_contract_and_publish_capabilities(self):
        for provider in OBJECT_TYPES.values():
            values = {field.key: field.default for field in provider.parameters}
            mesh = provider.mesh(values)
            self.assertIsInstance(mesh, ObjectMesh)
            self.assertEqual(mesh, provider.mesh(values))
        box = get_provider('box')
        self.assertFalse(box.supports_rig)
        self.assertFalse(box.supports_idle)
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            get_provider('unknown')

    def test_box_rejects_invalid_dimensions(self):
        for value in (0, float('nan'), True, '100'):
            with self.assertRaises((TypeError, ValueError)):
                get_provider('box').mesh(dict(width_cm=value, depth_cm=100, height_cm=100))
