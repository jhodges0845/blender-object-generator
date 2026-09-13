# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.components import _armature, attach_rigid_component, component_records, inspect_component
from blender_adapter.core import (
    AttachmentMode,
    ComponentBehavior,
    ComponentKind,
    ComponentRecord,
    RigBinding,
    ring_mesh,
)
from blender_adapter.external_inspection import BLOCKED, inspect_external_object
from blender_adapter.imported_components import adopt_rigid_component
from blender_adapter.working_asset_ui import validate_working_state


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class ImportedAssetComponentTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.before_objects = set(bpy.data.objects)
        self.before_meshes = set(bpy.data.meshes)
        self.before_collections = set(bpy.data.collections)
        self.before_armatures = set(bpy.data.armatures)
        self.scene = bpy.data.scenes.new("ImportedAssetComponentTest")
        bpy.context.window.scene = self.scene

    def tearDown(self):
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for obj in set(bpy.data.objects) - self.before_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in set(bpy.data.meshes) - self.before_meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        for armature in set(bpy.data.armatures) - self.before_armatures:
            if armature.users == 0:
                bpy.data.armatures.remove(armature)
        for collection in set(bpy.data.collections) - self.before_collections:
            if collection.users == 0:
                bpy.data.collections.remove(collection)

    def _imported_asset(self, *, with_rig=False):
        group = "imported-component-test"
        collection = bpy.data.collections.new("ImportedAsset")
        self.scene.collection.children.link(collection)
        root = bpy.data.objects.new("ImportedRoot", None)
        collection.objects.link(root)
        root["asset_assistant_import_group"] = group
        root["asset_assistant_import_root"] = True
        root["asset_assistant_external_asset"] = True
        root["asset_assistant_source"] = "ADOPTED"
        root["asset_assistant_asset_id"] = "external-asset-id"
        root["coordinate_scale"] = 0.01
        root["asset_assistant_external_capability"] = "RIGGED" if with_rig else "STATIC"

        mesh_data = bpy.data.meshes.new("ImportedBody")
        mesh_data.from_pydata(
            [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)],
            [],
            [(0, 1, 2, 3)],
        )
        mesh = bpy.data.objects.new("ImportedBody", mesh_data)
        collection.objects.link(mesh)
        mesh["asset_assistant_import_group"] = group

        rig = None
        if with_rig:
            armature_data = bpy.data.armatures.new("ImportedRig")
            rig = bpy.data.objects.new("ImportedRig", armature_data)
            collection.objects.link(rig)
            rig["asset_assistant_import_group"] = group
        return root, mesh, rig

    def test_component_registry_and_checkpoint_work_on_imported_root(self):
        root, _mesh, rig = self._imported_asset(with_rig=True)
        self.assertIs(_armature(root), rig)

        record = ComponentRecord(
            component_id="external-ring",
            kind=ComponentKind.ACCESSORY,
            provider_key="primitive.ring",
            attachment_target="asset_root",
            attachment_mode=AttachmentMode.RIGID,
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
            rig_binding=RigBinding.NONE,
            behavior=ComponentBehavior.RIGID,
        )
        component_root = attach_rigid_component(root, ring_mesh(3.0, 0.45), record, name="Imported Ring")

        self.assertIs(component_root.parent, root)
        self.assertEqual((record,), component_records(root))
        self.assertEqual(record, inspect_component(root, record.component_id))
        snapshots = validate_working_state(self.scene)
        self.assertEqual(1, len(snapshots))
        self.assertEqual(1, snapshots[0]["components"])

    def test_imported_base_mesh_cannot_be_reclassified_as_component(self):
        root, mesh, _rig = self._imported_asset()
        inspection = inspect_external_object(root, mesh)
        self.assertEqual(BLOCKED, inspection.status)
        self.assertTrue(any("base-asset geometry" in reason for reason in inspection.reasons))

        record = ComponentRecord(
            component_id="do-not-claim-body",
            kind=ComponentKind.ACCESSORY,
            provider_key="artist_authored",
            attachment_target="asset_root",
            attachment_mode=AttachmentMode.RIGID,
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
            rig_binding=RigBinding.NONE,
            behavior=ComponentBehavior.RIGID,
        )

        with self.assertRaisesRegex(ValueError, "already part of an Asset Assistant asset"):
            adopt_rigid_component(root, mesh, record, name="Wrong Component")


if __name__ == "__main__":
    unittest.main()
