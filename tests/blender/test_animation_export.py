# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify explicit generated-clip selection controls animated GLB export."""

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
from blender_adapter.animation import add_idle, add_locomotion, activate_generated_action
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
class AnimationExportTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ('objects', 'meshes', 'armatures', 'collections', 'materials', 'images', 'actions')}
        self.scene = bpy.data.scenes.new('AnimationExportTest')
        bpy.context.window.scene = self.scene
        provider = get_provider('human_experimental')
        values = {field.key: field.default for field in provider.parameters}
        self.root = create_character(provider.mesh(values), name='AnimatedHuman', scene=self.scene)
        self.root['object_type'] = provider.key
        for key, value in values.items():
            self.root[key] = value
        self.rig = add_basic_rig(self.root, bpy.context)
        prepare_materials(self.root)
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

    def test_only_active_generated_clip_is_exported_to_glb(self):
        add_idle(self.root, self.scene)
        add_locomotion(self.root, self.scene)
        adapter = get_adapter('GODOT', asset_use='ANIMATED')

        activate_generated_action(self.root, 'Idle')
        idle_path = Path(self.temp.name) / 'idle.glb'
        idle_result = adapter.export(self.root, bpy.context, idle_path)
        self.assertTrue(idle_result.success, idle_result.issues)
        idle_document = read_glb(idle_result.filepath)
        self.assertEqual(len(idle_document.get('animations', [])), 1)
        self.assertIn('Idle', idle_document['animations'][0].get('name', ''))

        activate_generated_action(self.root, 'Walk')
        walk_path = Path(self.temp.name) / 'walk.glb'
        walk_result = adapter.export(self.root, bpy.context, walk_path)
        self.assertTrue(walk_result.success, walk_result.issues)
        walk_document = read_glb(walk_result.filepath)
        self.assertEqual(len(walk_document.get('animations', [])), 1)
        self.assertIn('Walk', walk_document['animations'][0].get('name', ''))


if __name__ == '__main__':
    unittest.main()
