# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-side adapter contracts that can be tested in ordinary Python."""
import unittest
from types import SimpleNamespace
from pathlib import Path

from humanoid_blender.targets import GodotAdapter, asset_objects, get_adapter
from object_core.targets import GODOT


class TargetAdapterTests(unittest.TestCase):
    def test_registry_and_unimplemented_targets(self):
        self.assertIsInstance(get_adapter('godot'), GodotAdapter)
        with self.assertRaisesRegex(ValueError, 'unknown output target'):
            get_adapter('missing')
        for key in ('UNITY', 'UNREAL', 'PRINT_3D'):
            with self.assertRaisesRegex(ValueError, 'not implemented'):
                get_adapter(key)
        with self.assertRaises(TypeError):
            get_adapter(None)

    def test_metadata_and_explicit_static_profile(self):
        adapter = get_adapter('GODOT')
        self.assertIs(adapter.profile, GODOT)
        self.assertEqual(adapter.default_extension, '.glb')
        static = get_adapter('GODOT', asset_use='STATIC')
        self.assertFalse(static.profile.require_rig)
        self.assertFalse(static.profile.require_animation)
        self.assertEqual(GODOT.asset_use, 'ANIMATED')
        with self.assertRaises(ValueError):
            get_adapter('GODOT', asset_use='invalid')

    def test_options_scope_formats_and_rig_preservation(self):
        adapter = get_adapter('GODOT')
        options = adapter.export_options('asset')
        self.assertEqual(Path(options['filepath']).name, 'asset.glb')
        self.assertEqual(options['export_format'], 'GLB')
        self.assertTrue(options['use_selection'])
        self.assertTrue(options['export_skins'])
        self.assertTrue(options['export_animations'])
        self.assertFalse(options['export_apply'])
        self.assertEqual(options['export_materials'], 'EXPORT')
        self.assertEqual(adapter.export_options('asset.gltf')['export_format'], 'GLTF_SEPARATE')
        with self.assertRaisesRegex(ValueError, '.glb or .gltf'):
            adapter.export_options('asset.fbx')

    def test_recursive_scope_includes_mesh_roots(self):
        leaf = SimpleNamespace(children=[])
        root = SimpleNamespace(children=[SimpleNamespace(children=[leaf])])
        self.assertEqual(asset_objects(root), (root, root.children[0], leaf))
        self.assertEqual(asset_objects(leaf), (leaf,))
        self.assertEqual(asset_objects(None), ())
