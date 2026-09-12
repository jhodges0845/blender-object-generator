# SPDX-License-Identifier: GPL-3.0-or-later
"""Representative Avian engine-export coverage."""

import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.animation import add_flight, add_idle, add_locomotion, activate_generated_action
from blender_adapter.materials import prepare_materials
from blender_adapter.targets import get_adapter
from blender_adapter.workflow import add_basic_rig
from object_core.objects import get_provider


def read_glb(path):
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data)
    assert magic == b'glTF' and version == 2 and length == len(data)
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    return json.loads(data[20:20 + size].decode('utf8'))


@unittest.skipIf(bpy is None, 'requires Blender; use scripts/test_blender.py')
class AvianExportTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ('objects', 'meshes', 'armatures', 'collections', 'materials', 'images', 'actions')}
        self.scene = bpy.data.scenes.new('AvianExportTest')
        bpy.context.window.scene = self.scene
        provider = get_provider('avian')
        values = {field.key: field.default for field in provider.parameters}
        self.root = create_character(provider.mesh(values), name='AnimatedAvian', scene=self.scene)
        self.root['object_type'] = provider.key
        for key, value in values.items():
            self.root[key] = value
        self.rig = add_basic_rig(self.root, bpy.context)
        prepare_materials(self.root)
        add_idle(self.root, self.scene)
        add_locomotion(self.root, self.scene, duration=1.2)
        add_flight(self.root, self.scene, duration=0.9)
        self.active = activate_generated_action(self.root, 'Idle')
        self.temp = TemporaryDirectory()

    def tearDown(self):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)
        self.temp.cleanup()

    def test_godot_glb_contains_avian_idle_walk_and_flight(self):
        adapter = get_adapter('GODOT', asset_use='ANIMATED')
        result = adapter.export(self.root, bpy.context, Path(self.temp.name) / 'avian.glb')

        self.assertTrue(result.success, result.issues)
        document = read_glb(result.filepath)
        animations = document.get('animations', [])
        self.assertEqual({animation.get('name') for animation in animations}, {'Idle', 'Walk', 'Flight'})
        self.assertTrue(document.get('skins'))
        self.assertTrue(document.get('meshes'))
        self.assertIs(self.rig.animation_data.action, self.active)
        self.assertEqual(len(self.rig.animation_data.nla_tracks), 0)

    def test_unity_fbx_contains_avian_clip_names_and_skinning(self):
        adapter = get_adapter('UNITY', asset_use='ANIMATED')
        result = adapter.export(self.root, bpy.context, Path(self.temp.name) / 'avian.fbx')

        self.assertTrue(result.success, result.issues)
        payload = Path(result.filepath).read_bytes()
        self.assertIn(b'Idle', payload)
        self.assertIn(b'Walk', payload)
        self.assertIn(b'Flight', payload)
        self.assertIn(b'Deformer', payload)
        self.assertIn(b'Cluster', payload)
        self.assertIs(self.rig.animation_data.action, self.active)
        self.assertEqual(len(self.rig.animation_data.nla_tracks), 0)


if __name__ == '__main__':
    unittest.main()
