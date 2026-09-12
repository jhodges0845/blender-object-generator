# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.components import (
    AttachmentMode,
    ComponentBehavior,
    ComponentKind,
    ComponentRecord,
    PhysicsIntent,
    RigBinding,
    component_document,
    component_from_document,
    effective_behavior,
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
        self.assertEqual("none", document["rig_binding"])
        self.assertIsNone(document["behavior"])
        self.assertEqual(ComponentBehavior.RIGID, effective_behavior(record))
        self.assertEqual("secondary_motion", document["physics"]["mode"])
        self.assertNotIn("blender", str(document).lower())
        self.assertNotIn("godot", str(document).lower())
        self.assertEqual(record, component_from_document(document))

    def test_skinned_component_can_bind_to_parent_rig_without_owning_it(self):
        record = ComponentRecord(
            component_id="coat.01", kind=ComponentKind.CLOTHING,
            provider_key="coat.basic", attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED, owns_rig=False,
            rig_binding=RigBinding.PARENT,
        )
        self.assertIs(record, validate_component(record))
        document = component_document(record)
        self.assertEqual("parent", document["rig_binding"])
        self.assertIsNone(document["behavior"])
        self.assertEqual(ComponentBehavior.PARENT_SKINNED, effective_behavior(record))
        self.assertFalse(document["ownership"]["rig"])
        self.assertEqual(record, component_from_document(document))

    def test_self_rigged_gauntlet_is_separate_from_component_kind(self):
        record = ComponentRecord(
            component_id="gauntlet.01", kind=ComponentKind.ACCESSORY,
            provider_key="accessory.gauntlet", attachment_target="hand.R",
            attachment_mode=AttachmentMode.SKINNED, owns_rig=True,
            rig_binding=RigBinding.OWNED, behavior=ComponentBehavior.SELF_RIGGED,
        )
        self.assertIs(record, validate_component(record))
        self.assertEqual(ComponentBehavior.SELF_RIGGED, effective_behavior(record))
        self.assertEqual("self_rigged", component_document(record)["behavior"])

    def test_static_ring_requires_no_rig(self):
        record = ComponentRecord(
            component_id="ring.01", kind=ComponentKind.ACCESSORY,
            provider_key="accessory.ring", attachment_target="finger.R",
            attachment_mode=AttachmentMode.RIGID, behavior=ComponentBehavior.STATIC,
        )
        self.assertIs(record, validate_component(record))
        self.assertEqual("static", component_document(record)["behavior"])

    def test_physics_assisted_hair_requires_explicit_physics_intent(self):
        record = ComponentRecord(
            component_id="hair.02", kind=ComponentKind.HAIR,
            provider_key="hair.long", attachment_target="head",
            attachment_mode=AttachmentMode.SKINNED, rig_binding=RigBinding.PARENT,
            behavior=ComponentBehavior.PHYSICS_ASSISTED,
        )
        with self.assertRaisesRegex(ValueError, "physics intent"):
            validate_component(record)

    def test_physics_assisted_behavior_can_layer_over_parent_skinning(self):
        record = ComponentRecord(
            component_id="hair.03", kind=ComponentKind.HAIR,
            provider_key="hair.long", attachment_target="head",
            attachment_mode=AttachmentMode.SKINNED, rig_binding=RigBinding.PARENT,
            behavior=ComponentBehavior.PHYSICS_ASSISTED,
            physics=PhysicsIntent("secondary_motion", (("quality", "low"),)),
        )
        self.assertIs(record, validate_component(record))
        self.assertEqual("physics_assisted", component_document(record)["behavior"])

    def test_owned_rig_binding_requires_rig_ownership(self):
        record = ComponentRecord(
            component_id="cape.01", kind=ComponentKind.CLOTHING,
            provider_key="cape.rigged", attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED, owns_rig=False,
            rig_binding=RigBinding.OWNED,
        )
        with self.assertRaisesRegex(ValueError, "owned-rig"):
            validate_component(record)

    def test_skinned_component_requires_explicit_rig_binding(self):
        record = ComponentRecord(
            component_id="coat.02", kind=ComponentKind.CLOTHING,
            provider_key="coat.basic", attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED,
        )
        with self.assertRaisesRegex(ValueError, "skinned components"):
            validate_component(record)

    def test_legacy_skinned_document_infers_owned_rig_binding(self):
        document = {
            "component_id": "legacy.coat", "kind": "clothing",
            "provider_key": "coat.legacy", "attachment_target": "body",
            "attachment_mode": "skinned", "parameters": {}, "physics": None,
            "ownership": {"geometry": True, "materials": True, "rig": True},
        }
        record = component_from_document(document)
        self.assertEqual(RigBinding.OWNED, record.rig_binding)
        self.assertIsNone(record.behavior)
        self.assertEqual(ComponentBehavior.SELF_RIGGED, effective_behavior(record))
        self.assertTrue(record.owns_rig)

    def test_component_and_physics_parameter_keys_must_be_unique(self):
        record = ComponentRecord(
            component_id="hat.01", kind=ComponentKind.ACCESSORY,
            provider_key="hat.basic", attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
            parameters=(("size", 1.0), ("size", 1.1)),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_component(record)
        record = ComponentRecord(
            component_id="hair.01", kind=ComponentKind.HAIR,
            provider_key="hair.basic", attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
            physics=PhysicsIntent("secondary_motion", (("drag", 0.1), ("drag", 0.2))),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_component(record)

    def test_component_identity_fields_must_be_nonempty(self):
        record = ComponentRecord(
            component_id="", kind=ComponentKind.ACCESSORY,
            provider_key="hat.basic", attachment_target="head",
            attachment_mode=AttachmentMode.RIGID,
        )
        with self.assertRaisesRegex(ValueError, "component_id"):
            validate_component(record)


if __name__ == "__main__":
    unittest.main()
