# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from object_core.models.validation import AssetSnapshot
from object_core.targets import GODOT, PRINT_3D, UNITY, UNREAL, get_target, validate_for_target


class OutputTargetTests(unittest.TestCase):
    def statuses(self, snapshot, target):
        return {row.code: row.status for row in validate_for_target(snapshot, target)}

    def test_known_targets_have_expected_export_formats(self):
        self.assertEqual(GODOT.preferred_formats, ("GLB", "GLTF"))
        self.assertEqual(UNITY.preferred_formats, ("FBX",))
        self.assertEqual(UNREAL.preferred_formats, ("FBX",))
        self.assertEqual(PRINT_3D.preferred_formats, ("3MF", "STL"))
        self.assertIs(get_target("godot"), GODOT)

    def test_game_targets_require_rig_and_animation(self):
        plain = AssetSnapshot(mesh_count=1)
        for target in (GODOT, UNITY, UNREAL):
            statuses = self.statuses(plain, target)
            self.assertEqual(statuses["rig"], "ERROR")
            self.assertEqual(statuses["animation"], "ERROR")

        animated = AssetSnapshot(mesh_count=1, has_rig=True, has_animation=True)
        for target in (GODOT, UNITY, UNREAL):
            statuses = self.statuses(animated, target)
            self.assertEqual(statuses["rig"], "PASS")
            self.assertEqual(statuses["animation"], "PASS")

    def test_print_target_is_static_and_warns_about_runtime_data(self):
        printable = AssetSnapshot(mesh_count=1, has_rig=True, has_animation=True)
        statuses = self.statuses(printable, PRINT_3D)
        self.assertEqual(statuses["rig"], "PASS")
        self.assertEqual(statuses["animation"], "PASS")
        self.assertEqual(statuses["target_geometry"], "PASS")
        self.assertEqual(statuses["target_rig"], "WARN")
        self.assertEqual(statuses["target_animation"], "WARN")

    def test_invalid_print_geometry_fails_target_check(self):
        snapshot = AssetSnapshot(mesh_count=1, invalid_meshes=("body",))
        self.assertEqual(self.statuses(snapshot, PRINT_3D)["target_geometry"], "ERROR")

    def test_invalid_target_requests_fail_clearly(self):
        with self.assertRaises(ValueError):
            get_target("unknown")
        with self.assertRaises(TypeError):
            validate_for_target(AssetSnapshot(), object())


if __name__ == "__main__":
    unittest.main()
