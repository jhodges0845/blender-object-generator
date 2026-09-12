# SPDX-License-Identifier: GPL-3.0-or-later

import json
import unittest

from object_core.components import AttachmentMode, ComponentKind, ComponentRecord, RigBinding
from object_core.modification import AssetSnapshot, ComponentOperation, ModificationRequest, plan_modification
from object_core.modify_exchange import INSPECTION_SCHEMA, REQUEST_SCHEMA, inspection_json, request_from_json


class ComponentModifyExchangeTests(unittest.TestCase):
    def _component(self, component_id="coat.01", provider_key="clothing.coat"):
        return ComponentRecord(
            component_id=component_id,
            kind=ComponentKind.CLOTHING,
            provider_key=provider_key,
            attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED,
            rig_binding=RigBinding.PARENT,
            owns_geometry=True,
            owns_materials=True,
            owns_rig=False,
        )

    def _snapshot(self, components=()):
        return AssetSnapshot(
            asset_id="asset-123",
            provider_key="avian",
            provider_label="Avian",
            parameters=(("body_length_cm", 42.0), ("body_width_cm", 16.0),
                        ("body_height_cm", 20.0), ("wingspan_cm", 90.0),
                        ("tail_length_cm", 22.0)),
            components=components,
            owns_geometry=True,
        )

    def test_inspection_exports_attached_components_and_v3_template(self):
        record = self._component()
        document = json.loads(inspection_json(self._snapshot((record,))))

        self.assertEqual(INSPECTION_SCHEMA, document["schema"])
        self.assertEqual("asset-assistant.modify-inspection/v3", document["schema"])
        self.assertEqual("coat.01", document["asset"]["attached_components"][0]["component_id"])
        self.assertEqual("parent", document["asset"]["attached_components"][0]["rig_binding"])
        self.assertEqual(REQUEST_SCHEMA, document["request_template"]["schema"])
        self.assertEqual([], document["request_template"]["component_operations"])

    def test_remove_component_request_parses_but_planning_blocks_execution(self):
        record = self._component()
        snapshot = self._snapshot((record,))
        payload = json.dumps({
            "schema": REQUEST_SCHEMA,
            "asset_id": "asset-123",
            "provider_key": "avian",
            "component_operations": [{
                "operation": "remove",
                "component_id": "coat.01",
                "component": None,
            }],
        })

        request = request_from_json(payload, snapshot)
        self.assertEqual((ComponentOperation("remove", "coat.01", None),), request.component_operations)
        plan = plan_modification(snapshot, request)
        self.assertEqual("remove", plan.requested_component_operations[0].operation)
        self.assertFalse(plan.safe_to_apply)
        self.assertTrue(any("not executable through Modify yet" in item for item in plan.blockers))

    def test_replace_requires_matching_existing_component_and_metadata_identity(self):
        current = self._component()
        replacement = self._component(provider_key="clothing.coat.v2")
        snapshot = self._snapshot((current,))
        request = ModificationRequest(component_operations=(
            ComponentOperation("replace", "coat.01", replacement),
        ))
        plan = plan_modification(snapshot, request)
        self.assertEqual("clothing.coat.v2", plan.requested_component_operations[0].component.provider_key)

        wrong = self._component(component_id="other.01")
        with self.assertRaisesRegex(ValueError, "does not match component metadata"):
            plan_modification(snapshot, ModificationRequest(component_operations=(
                ComponentOperation("replace", "coat.01", wrong),
            )))

    def test_add_rejects_duplicate_component_id(self):
        record = self._component()
        snapshot = self._snapshot((record,))
        with self.assertRaisesRegex(ValueError, "already attached"):
            plan_modification(snapshot, ModificationRequest(component_operations=(
                ComponentOperation("add", "coat.01", record),
            )))

    def test_v2_request_remains_readable_without_component_operations(self):
        snapshot = self._snapshot()
        payload = json.dumps({
            "schema": "asset-assistant.modify-request/v2",
            "asset_id": "asset-123",
            "provider_key": "avian",
            "semantic_operations": [],
        })
        request = request_from_json(payload, snapshot)
        self.assertEqual((), request.component_operations)


if __name__ == "__main__":
    unittest.main()
