# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.components import (
    AttachmentMode,
    ComponentKind,
    ComponentRecord,
    PhysicsIntent,
    component_document,
    component_from_document,
)


class ComponentPersistenceTests(unittest.TestCase):
    def test_component_document_round_trip_preserves_physics_and_ownership(self):
        record = ComponentRecord(
            component_id="cape-001",
            kind=ComponentKind.ACCESSORY,
            provider_key="proof_accessory",
            attachment_target="asset_root",
            attachment_mode=AttachmentMode.RIGID,
            parameters=(("size", 1.25),),
            physics=PhysicsIntent("secondary_motion", (("strength", 0.4),)),
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
        )

        restored = component_from_document(component_document(record))

        self.assertEqual(record, restored)

    def test_component_parser_rejects_unknown_kind(self):
        document = component_document(ComponentRecord(
            component_id="item-001",
            kind=ComponentKind.ACCESSORY,
            provider_key="proof_accessory",
            attachment_target="asset_root",
            attachment_mode=AttachmentMode.RIGID,
        ))
        document["kind"] = "vehicle"

        with self.assertRaisesRegex(ValueError, "unsupported component kind"):
            component_from_document(document)


if __name__ == "__main__":
    unittest.main()
