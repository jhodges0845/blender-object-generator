# SPDX-License-Identifier: GPL-3.0-or-later

import json
import unittest

from object_core.modification import AnimationSnapshot, AssetSnapshot, plan_modification
from object_core.modify_exchange import (
    INSPECTION_SCHEMA,
    REQUEST_SCHEMA,
    inspection_json,
    request_from_json,
)


class ModifyExchangeTests(unittest.TestCase):
    def _snapshot(self):
        return AssetSnapshot(
            asset_id="asset-123",
            provider_key="avian",
            provider_label="Avian",
            parameters=(("body_length_cm", 42.0), ("body_width_cm", 16.0),
                        ("body_height_cm", 20.0), ("wingspan_cm", 90.0),
                        ("tail_length_cm", 22.0)),
            animations=(AnimationSnapshot("Walk", "Walk"),),
            has_rig=True,
            has_materials=True,
            has_animations=True,
            owns_geometry=True,
            owns_rig=True,
            owns_materials=True,
            owns_animations=True,
        )

    def test_inspection_export_contains_snapshot_and_return_template(self):
        document = json.loads(inspection_json(self._snapshot()))
        self.assertEqual(INSPECTION_SCHEMA, document["schema"])
        self.assertEqual("asset-123", document["asset"]["asset_id"])
        self.assertEqual(90.0, document["asset"]["parameters"]["wingspan_cm"])
        template = document["request_template"]
        self.assertEqual(REQUEST_SCHEMA, template["schema"])
        self.assertEqual("asset-123", template["asset_id"])
        self.assertEqual({}, template["parameter_changes"])

    def test_returned_request_binds_to_asset_and_plans_normally(self):
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "asset-123",
            "provider_key": "avian",
            "parameter_changes": {"wingspan_cm": 120},
            "animation_export_names": {"Walk": "Ground Walk"},
            "notes": "Prepared externally",
        })
        snapshot = self._snapshot()
        request = request_from_json(payload, snapshot)
        plan = plan_modification(snapshot, request)
        self.assertEqual((("wingspan_cm", 120.0),), plan.requested_parameter_changes)
        self.assertEqual((("Walk", "Ground Walk"),), plan.requested_animation_renames)
        self.assertTrue(plan.safe_to_apply)

    def test_request_for_different_asset_is_rejected(self):
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "other-asset",
            "provider_key": "avian",
            "parameter_changes": {},
            "animation_export_names": {},
        })
        with self.assertRaisesRegex(ValueError, "different Asset Assistant asset"):
            request_from_json(payload, self._snapshot())

    def test_unknown_schema_is_rejected(self):
        payload = json.dumps({
            "schema": "something-else/v1",
            "asset_id": "asset-123",
            "provider_key": "avian",
        })
        with self.assertRaisesRegex(ValueError, "Unsupported Modify request schema"):
            request_from_json(payload, self._snapshot())


if __name__ == "__main__":
    unittest.main()
