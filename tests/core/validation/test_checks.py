# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import replace
import unittest

from object_core.models.validation import AssetSnapshot
from object_core.validation import validate_asset


class ValidationTests(unittest.TestCase):
    def statuses(self, snapshot, **options):
        return {row.code: row.status for row in validate_asset(snapshot, **options)}

    def test_requirements_distinguish_static_rigged_and_animated(self):
        plain = AssetSnapshot(mesh_count=15)
        self.assertEqual(self.statuses(plain, asset_use="STATIC")["rig"], "PASS")
        self.assertEqual(self.statuses(plain)["rig"], "ERROR")
        rigged = replace(plain, has_rig=True)
        self.assertEqual(self.statuses(rigged)["rig"], "PASS")
        self.assertEqual(self.statuses(rigged, asset_use="ANIMATED")["animation"], "ERROR")
        self.assertEqual(self.statuses(replace(rigged, has_animation=True), asset_use="ANIMATED")["animation"], "PASS")

    def test_textures_are_optional_but_broken_references_are_errors(self):
        plain = AssetSnapshot(mesh_count=1, missing_uvs=("head",))
        self.assertEqual(self.statuses(plain)["textures"], "PASS")
        self.assertEqual(self.statuses(plain)["uvs"], "PASS")
        self.assertEqual(self.statuses(plain, require_textures=True)["textures"], "ERROR")
        self.assertEqual(self.statuses(plain, require_textures=True)["uvs"], "ERROR")
        broken = replace(plain, texture_count=1, missing_images=("missing.png",))
        self.assertEqual(self.statuses(broken)["textures"], "ERROR")
        self.assertEqual(self.statuses(broken)["uvs"], "ERROR")

    def test_missing_geometry_and_corrupt_weights_are_reported(self):
        self.assertEqual(self.statuses(AssetSnapshot())["geometry"], "ERROR")
        bad = AssetSnapshot(mesh_count=1, invalid_meshes=("head",), has_rig=True, rig_errors=("Unweighted vertices",))
        self.assertEqual(self.statuses(bad)["geometry"], "ERROR")
        self.assertEqual(self.statuses(bad)["rig"], "ERROR")

    def test_blockout_and_export_review_never_claim_production_readiness(self):
        snapshot = AssetSnapshot(mesh_count=15, has_rig=True, has_animation=True)
        results = self.statuses(snapshot, asset_use="ANIMATED")
        self.assertEqual(results["blockout"], "INFO")
        self.assertEqual(results["export_review"], "INFO")
        self.assertEqual(validate_asset(snapshot), validate_asset(snapshot))

    def test_invalid_requests_fail_clearly(self):
        with self.assertRaises(TypeError):
            validate_asset(None)
        with self.assertRaises(ValueError):
            validate_asset(AssetSnapshot(), asset_use="UNKNOWN")

    def test_missing_materials_require_preparation(self):
        self.assertEqual(self.statuses(AssetSnapshot(mesh_count=1, missing_materials=('mesh',)),
                                       asset_use='STATIC')['materials'], 'ERROR')
