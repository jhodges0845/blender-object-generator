# SPDX-License-Identifier: GPL-3.0-or-later
"""Ensure importing the core and adapter entry points does not load Blender APIs."""

from pathlib import Path
import subprocess
import sys
import unittest


class ImportBoundaryTests(unittest.TestCase):
    def test_normal_python_imports_without_bpy(self):
        if "bpy" in sys.modules:
            self.skipTest("standalone Python subprocess check")
        code = """
import sys
class RejectBlender:
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('bpy', 'mathutils', 'bmesh'):
            raise AssertionError('Unexpected host dependency: ' + fullname)
sys.meta_path.insert(0, RejectBlender())
import object_core
import blender_adapter
import blender_adapter.adapter
import blender_adapter.targets
import humanoid_blender
import humanoid_blender.adapter
import humanoid_blender.targets
assert blender_adapter.targets.get_adapter("GODOT").target_key == "GODOT"
assert humanoid_blender.targets.get_adapter("GODOT").target_key == "GODOT"
mesh = object_core.generate_mesh(object_core.generate_proportions(
    object_core.HumanoidSpec(180, 95, object_core.BodyType.AVERAGE)))
assert len(mesh.parts) == 15
"""
        result = subprocess.run([sys.executable, "-c", code],
                                cwd=str(Path(__file__).resolve().parents[2]),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
