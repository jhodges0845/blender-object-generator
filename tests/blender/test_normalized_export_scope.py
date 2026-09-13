import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.targets import asset_objects, base_asset_rig


@unittest.skipIf(bpy is None, 'requires Blender; use scripts/test_blender.py')
class NormalizedExportScopeTests(unittest.TestCase):
    def setUp(self):
        self.before_objects = set(bpy.data.objects)
        self.before_meshes = set(bpy.data.meshes)
        self.before_armatures = set(bpy.data.armatures)

    def tearDown(self):
        for obj in set(bpy.data.objects) - self.before_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in set(bpy.data.meshes) - self.before_meshes:
            bpy.data.meshes.remove(mesh)
        for armature in set(bpy.data.armatures) - self.before_armatures:
            bpy.data.armatures.remove(armature)

    def test_import_group_exports_sibling_mesh_and_rig_as_one_asset(self):
        group = 'fbx-export-scope'
        root = bpy.data.objects.new('ImportedRoot', None)
        root['asset_assistant_import_group'] = group
        root['asset_assistant_import_root'] = True
        bpy.context.scene.collection.objects.link(root)

        mesh_data = bpy.data.meshes.new('ImportedBodyMesh')
        mesh = bpy.data.objects.new('ImportedBody', mesh_data)
        mesh['asset_assistant_import_group'] = group
        bpy.context.scene.collection.objects.link(mesh)

        armature_data = bpy.data.armatures.new('ImportedRigData')
        rig = bpy.data.objects.new('ImportedRig', armature_data)
        rig['asset_assistant_import_group'] = group
        bpy.context.scene.collection.objects.link(rig)

        modifier = mesh.modifiers.new('ImportedSkin', 'ARMATURE')
        modifier.object = rig

        unrelated = bpy.data.objects.new('Unrelated', None)
        bpy.context.scene.collection.objects.link(unrelated)

        objects = asset_objects(root)

        self.assertEqual(set(objects), {root, mesh, rig})
        self.assertNotIn(unrelated, objects)
        self.assertIs(base_asset_rig(root), rig)

    def test_selected_import_child_resolves_the_same_export_boundary(self):
        group = 'glb-export-scope'
        root = bpy.data.objects.new('GLBRoot', None)
        root['asset_assistant_import_group'] = group
        root['asset_assistant_import_root'] = True
        bpy.context.scene.collection.objects.link(root)

        mesh_data = bpy.data.meshes.new('GLBBodyMesh')
        mesh = bpy.data.objects.new('GLBBody', mesh_data)
        mesh['asset_assistant_import_group'] = group
        bpy.context.scene.collection.objects.link(mesh)

        armature_data = bpy.data.armatures.new('GLBRigData')
        rig = bpy.data.objects.new('GLBRig', armature_data)
        rig['asset_assistant_import_group'] = group
        bpy.context.scene.collection.objects.link(rig)

        self.assertEqual(set(asset_objects(mesh)), {root, mesh, rig})
        self.assertIs(base_asset_rig(mesh), rig)
