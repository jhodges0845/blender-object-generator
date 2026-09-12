# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.components import component_records
from blender_adapter.skinned_components import attach_skinned_component, inspect_skinned_component
from object_core.components import AttachmentMode, ComponentKind, ComponentRecord, RigBinding
from object_core.models import BoneWeight, SkinWeights
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderSkinnedComponentTests(unittest.TestCase):
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
        mesh = provider.mesh(values)
        root = create_character(
            mesh,
            name="Human",
            scene=bpy.context.scene,
            skeleton=provider.skeleton(values),
            skin_weights=provider.skin_weights(mesh, values),
        )
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def _proof_mesh(self):
        provider = get_provider("box")
        values = {field.key: field.default for field in provider.parameters}
        return provider.mesh(values)

    def _weights(self, mesh, bone_name="torso"):
        return tuple(
            SkinWeights(
                part.name,
                tuple(((BoneWeight(bone_name, 1.0),)) for _vertex in part.vertices),
            )
            for part in mesh.parts
        )

    def _record(self):
        return ComponentRecord(
            component_id="proof-skinned-001",
            kind=ComponentKind.CLOTHING,
            provider_key="clothing.proof",
            attachment_target="body",
            attachment_mode=AttachmentMode.SKINNED,
            rig_binding=RigBinding.PARENT,
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
        )

    def test_skinned_component_binds_to_parent_rig_and_is_inspectable(self):
        root = self._generated_human()
        mesh = self._proof_mesh()
        record = self._record()
        armature = next(child for child in root.children if child.type == "ARMATURE")

        component_root = attach_skinned_component(
            root,
            mesh,
            self._weights(mesh),
            record,
            name="Proof Clothing",
        )

        self.assertEqual(root, component_root.parent)
        self.assertEqual(record, inspect_skinned_component(root, record.component_id))
        self.assertEqual((record,), component_records(root))
        for obj in (child for child in component_root.children if child.type == "MESH"):
            modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
            self.assertEqual(1, len(modifiers))
            self.assertEqual(armature, modifiers[0].object)
            self.assertIsNotNone(obj.vertex_groups.get("torso"))

    def test_modifier_retargeting_is_detected(self):
        root = self._generated_human()
        mesh = self._proof_mesh()
        record = self._record()
        component_root = attach_skinned_component(root, mesh, self._weights(mesh), record)
        component_mesh = next(child for child in component_root.children if child.type == "MESH")
        modifier = next(modifier for modifier in component_mesh.modifiers if modifier.type == "ARMATURE")
        modifier.object = None

        with self.assertRaisesRegex(ValueError, "armature modifier"):
            inspect_skinned_component(root, record.component_id)

    def test_weight_tampering_is_detected(self):
        root = self._generated_human()
        mesh = self._proof_mesh()
        record = self._record()
        component_root = attach_skinned_component(root, mesh, self._weights(mesh), record)
        component_mesh = next(child for child in component_root.children if child.type == "MESH")
        group = component_mesh.vertex_groups["torso"]
        group.add([0], 0.5, "REPLACE")

        with self.assertRaisesRegex(ValueError, "vertex weights"):
            inspect_skinned_component(root, record.component_id)

    def test_unknown_parent_bone_rejects_transaction_without_registry_change(self):
        root = self._generated_human()
        mesh = self._proof_mesh()
        record = self._record()

        with self.assertRaisesRegex(ValueError, "bone not present"):
            attach_skinned_component(root, mesh, self._weights(mesh, "missing.bone"), record)

        self.assertEqual((), component_records(root))
        self.assertFalse(any(
            obj.get("asset_assistant_component_id") == record.component_id
            for obj in bpy.data.objects
        ))


if __name__ == "__main__":
    unittest.main()
