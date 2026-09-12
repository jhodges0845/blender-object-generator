# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.components import attach_rigid_component, component_records, inspect_component
from object_core.components import AttachmentMode, ComponentKind, ComponentRecord
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderComponentPersistenceTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for collection in tuple(bpy.data.collections):
            if collection.users == 0:
                bpy.data.collections.remove(collection)

    def _generated_human(self):
        provider = get_provider("human_experimental")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name="Human", scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def _proof_mesh(self):
        provider = get_provider("box")
        values = {field.key: field.default for field in provider.parameters}
        return provider.mesh(values)

    def _record(self):
        return ComponentRecord(
            component_id="proof-accessory-001",
            kind=ComponentKind.ACCESSORY,
            provider_key="box-proof",
            attachment_target="asset_root",
            attachment_mode=AttachmentMode.RIGID,
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
        )

    def test_rigid_accessory_is_persisted_and_inspectable(self):
        root = self._generated_human()
        record = self._record()

        component_root = attach_rigid_component(root, self._proof_mesh(), record, name="Proof Accessory")

        self.assertEqual(root, component_root.parent)
        self.assertEqual(record, inspect_component(root, record.component_id))
        self.assertEqual((record,), component_records(root))
        self.assertTrue(any(child.type == "MESH" for child in component_root.children))

    def test_duplicate_component_id_is_rejected_without_extra_children(self):
        root = self._generated_human()
        record = self._record()
        attach_rigid_component(root, self._proof_mesh(), record, name="Proof Accessory")
        child_count = len(root.children)

        with self.assertRaisesRegex(ValueError, "already attached"):
            attach_rigid_component(root, self._proof_mesh(), record, name="Duplicate")

        self.assertEqual(child_count, len(root.children))
        self.assertEqual((record,), component_records(root))

    def test_tampered_component_metadata_is_detected(self):
        root = self._generated_human()
        record = self._record()
        component_root = attach_rigid_component(root, self._proof_mesh(), record, name="Proof Accessory")
        component_root["asset_assistant_component_record"] = "{}"

        with self.assertRaisesRegex(ValueError, "metadata is invalid"):
            inspect_component(root, record.component_id)


if __name__ == "__main__":
    unittest.main()
