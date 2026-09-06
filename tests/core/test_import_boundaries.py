# SPDX-License-Identifier: GPL-3.0-or-later
"""Ensure importing the core and adapter entry point does not load Blender APIs."""

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
import humanoid_core
import humanoid_blender
import humanoid_blender.adapter
mesh = humanoid_core.generate_mesh(humanoid_core.generate_proportions(
    humanoid_core.HumanoidSpec(180, 95, humanoid_core.BodyType.AVERAGE)))
assert len(mesh.parts) == 15
"""
        result = subprocess.run([sys.executable, "-c", code],
                                cwd=str(Path(__file__).resolve().parents[2]),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
