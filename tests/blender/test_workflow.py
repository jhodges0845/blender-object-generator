# SPDX-License-Identifier: GPL-3.0-or-later
"""Existing-character operations and read-only material/texture inspection."""

from dataclasses import replace
import unittest
from unittest.mock import patch

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from humanoid_core import BodyType, HumanoidSpec, generate_mesh, generate_proportions
from humanoid_blender.adapter import create_character
from humanoid_blender.validation import inspect_character
from humanoid_blender.workflow import add_basic_rig


@unittest.skipIf(bpy is None, "requires Blender")
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ("objects", "meshes", "armatures", "collections", "materials", "images", "actions")}
        self.scene = bpy.data.scenes.new("WorkflowTest")
        bpy.context.window.scene = self.scene
        spec = HumanoidSpec(180, 95, BodyType.AVERAGE)
        self.root = create_character(generate_mesh(generate_proportions(spec)), scene=self.scene)
        self.root["height_cm"], self.root["weight_kg"], self.root["body_type"] = 180, 95, "average"

    def tearDown(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.window.scene = self.previous_scene
        bpy.data.scenes.remove(self.scene)
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)

    def test_rig_existing_character_keeps_mesh_and_cannot_duplicate_rig(self):
        before = {obj.data for obj in self.root.children}
        self.root.location = (2, 3, 4)
        self.scene.unit_settings.scale_length = 0.01
        rig = add_basic_rig(self.root, bpy.context)
        self.assertEqual({obj.data for obj in self.root.children if obj.type == "MESH"}, before)
        self.assertAlmostEqual(rig.data.bones['head'].tail_local.z, 1.8, places=5)
        with self.assertRaisesRegex(ValueError, "already"):
            add_basic_rig(self.root, bpy.context)

    def test_weight_failure_restores_existing_character(self):
        import humanoid_blender.rigging as rigging
        original = rigging._assign_weights
        count = [0]

        def fail_second(*args):
            count[0] += 1
            if count[0] == 2:
                raise RuntimeError("weight failure")
            return original(*args)

        with patch.object(rigging, "_assign_weights", side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, "weight failure"):
                add_basic_rig(self.root, bpy.context)
        self.assertEqual(len(self.root.children), 15)
        self.assertTrue(all(not obj.modifiers and not obj.vertex_groups for obj in self.root.children))
        self.assertEqual(self.root["stage"], "blockout")

    def test_readonly_material_uv_and_texture_checks(self):
        initial = inspect_character(self.root)
        self.assertEqual(initial.mesh_count, 15)
        self.assertFalse(initial.invalid_meshes)
        self.assertEqual(len(initial.missing_materials), 15)
        material = bpy.data.materials.new("ValidationMaterial")
        material.use_nodes = True
        for obj in self.root.children:
            obj.data.materials.append(material)
            obj.data.uv_layers.new()
        texture = material.node_tree.nodes.new("ShaderNodeTexImage")
        shader = material.node_tree.nodes.get("Principled BSDF")
        material.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
        self.assertTrue(inspect_character(self.root).missing_images)
        image = bpy.data.images.new("TextureCheck", width=8, height=8)
        texture.image = image
        generated = inspect_character(self.root)
        self.assertEqual(generated.texture_count, 1)
        self.assertFalse(generated.missing_materials)
        self.assertFalse(generated.missing_uvs)
        self.assertTrue(generated.texture_warnings)
        image.pixels[0] = 1.0
        image.update()
        image.pack()
        packed = inspect_character(self.root)
        self.assertFalse(packed.missing_images)
        self.assertFalse(packed.texture_warnings)
        missing = bpy.data.images.new("MissingExternal", width=8, height=8)
        missing.source = 'FILE'
        missing.filepath = '//definitely-not-present/texture.png'
        texture.image = missing
        broken = inspect_character(self.root)
        self.assertTrue(broken.missing_images)
        self.assertEqual(broken, inspect_character(self.root))
        self.assertEqual(texture.image, missing)

    def test_pose_button_and_animated_validation_requirement(self):
        import humanoid_blender
        humanoid_blender.register()
        try:
            settings = self.scene.humanoid_settings
            settings.target = self.root
            self.assertEqual(bpy.ops.humanoid.add_basic_rig(), {'FINISHED'})
            rig = bpy.context.object
            self.assertFalse(inspect_character(self.root).rig_errors)
            self.assertEqual(bpy.ops.humanoid.enter_pose_mode(), {'FINISHED'})
            self.assertEqual(bpy.context.mode, 'POSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            settings.asset_use = 'ANIMATED'
            bpy.ops.humanoid.validate_character()
            self.assertTrue(any(row.code == 'animation' and row.status == 'ERROR' for row in settings.validation_results))
            rig.pose.bones['head'].keyframe_insert(data_path='rotation_quaternion', frame=1)
            self.assertTrue(inspect_character(self.root).has_animation)
        finally:
            humanoid_blender.unregister()
