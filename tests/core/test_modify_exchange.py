# SPDX-License-Identifier: GPL-3.0-or-later

import json
import unittest

from object_core.modification import AnimationSnapshot, AssetSnapshot, plan_modification
from object_core.modify_exchange import INSPECTION_SCHEMA, REQUEST_SCHEMA, inspection_json, request_from_json


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
            has_rig=True, has_materials=True, has_animations=True,
            owns_geometry=True, owns_rig=True, owns_materials=True, owns_animations=True,
        )

    def test_inspection_export_contains_semantic_targets_and_return_template(self):
        document = json.loads(inspection_json(self._snapshot()))
        self.assertEqual(INSPECTION_SCHEMA, document["schema"])
        self.assertEqual("asset-123", document["asset"]["asset_id"])
        target_keys = {target["key"] for target in document["asset"]["semantic_targets"]}
        self.assertIn("beak", target_keys)
        self.assertIn("wing.left", target_keys)
        template = document["request_template"]
        self.assertEqual(REQUEST_SCHEMA, template["schema"])
        self.assertEqual([], template["semantic_operations"])

    def test_returned_parameter_request_still_plans_normally(self):
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "asset-123",
            "provider_key": "avian",
            "parameter_changes": {"wingspan_cm": 120},
            "animation_export_names": {"Walk": "Ground Walk"},
            "semantic_operations": [],
        })
        snapshot = self._snapshot()
        plan = plan_modification(snapshot, request_from_json(payload, snapshot))
        self.assertEqual((("wingspan_cm", 120.0),), plan.requested_parameter_changes)
        self.assertEqual((("Walk", "Ground Walk"),), plan.requested_animation_renames)
        self.assertEqual((), plan.requested_semantic_operations)
        self.assertTrue(plan.safe_to_apply)

    def test_semantic_request_is_provider_validated_and_safely_blocked_until_apply_exists(self):
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "asset-123",
            "provider_key": "avian",
            "parameter_changes": {},
            "animation_export_names": {},
            "semantic_operations": [
                {"operation": "shape", "target": "beak", "arguments": {"profile": "hooked", "amount": 0.8}},
                {"operation": "scale", "target": "chest", "arguments": {"xyz": [1.15, 1.0, 1.1]}},
            ],
        })
        snapshot = self._snapshot()
        plan = plan_modification(snapshot, request_from_json(payload, snapshot))
        self.assertEqual(("beak", "chest"), tuple(op.target for op in plan.requested_semantic_operations))
        self.assertFalse(plan.safe_to_apply)
        self.assertTrue(any("semantic apply layer" in blocker for blocker in plan.blockers))

    def test_unknown_semantic_target_is_rejected(self):
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "asset-123",
            "provider_key": "avian",
            "semantic_operations": [{"operation": "shape", "target": "magic.feathers", "arguments": {}}],
        })
        snapshot = self._snapshot()
        with self.assertRaisesRegex(ValueError, "Unsupported semantic target"):
            plan_modification(snapshot, request_from_json(payload, snapshot))

    def test_request_for_different_asset_is_rejected(self):
        payload = json.dumps({"schema": REQUEST_SCHEMA, "asset_id": "other-asset", "provider_key": "avian"})
        with self.assertRaisesRegex(ValueError, "different Asset Assistant asset"):
            request_from_json(payload, self._snapshot())

    def test_legacy_v1_request_remains_accepted(self):
        payload = json.dumps({
            "schema": "asset-assistant.modify-request/v1",
            "asset_id": "asset-123",
            "provider_key": "avian",
            "parameter_changes": {"tail_length_cm": 30},
        })
        request = request_from_json(payload, self._snapshot())
        self.assertEqual((), request.semantic_operations)


if __name__ == "__main__":
    unittest.main()
