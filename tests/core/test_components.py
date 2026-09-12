# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.components import (
    AttachmentMode,
    ComponentKind,
    ComponentRecord,
    PhysicsIntent,
    component_document,
    validate_component,
)


class ComponentContractTests(unittest.TestCase):
    def test_rigid_hair_component_serializes_without_host_details(self):
        record = ComponentRecord(
            component_id="hair.maxine.long",
            kind=ComponentKind.HAIR,
            provider_key="hair.long_layered",
            attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
            parameters=(("length", 0.8), ("density", 0.6)),
            physics=PhysicsIntent("secondary_motion", (("stiffness", 0.4),)),
        )

        self.assertIs(record, validate_component(record))
        document = component_document(record)
        self.assertEqual("hair", document["kind"])
        self.assertEqual("head", document["attachment_target"])
        self.assertEqual("secondary_motion", document["physics"]["mode"])
        self.assertNotIn("blender", str(document).lower())
        self.assertNotIn("godot", str(document).lower())

    def test_skinned_component_requires_rig_ownership(self):
        record = ComponentRecord(
            component_id="coat.01",
            kind=ComponentKind.CLOTHING,
            provider_key="coat.basic",
            attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED,
        )
        with self.assertRaisesRegex(ValueError, "skinned components"):
            validate_component(record)

    def test_component_and_physics_parameter_keys_must_be_unique(self):
        record = ComponentRecord(
            component_id="hat.01",
            kind=ComponentKind.ACCESSORY,
            provider_key="hat.basic",
            attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
            parameters=(("size", 1.0), ("size", 1.1)),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_component(record)

        record = ComponentRecord(
            component_id="hair.01",
            kind=ComponentKind.HAIR,
            provider_key="hair.basic",
            attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
            physics=PhysicsIntent("secondary_motion", (("drag", 0.1), ("drag", 0.2))),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_component(record)

    def test_component_identity_fields_must_be_nonempty(self):
        record = ComponentRecord(
            component_id="",
            kind=ComponentKind.ACCESSORY,
            provider_key="hat.basic",
            attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
        )
        with self.assertRaisesRegex(ValueError, "component_id"):
            validate_component(record)


if __name__ == "__main__":
    unittest.main()
