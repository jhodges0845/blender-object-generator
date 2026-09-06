# SPDX-License-Identifier: GPL-3.0-or-later
"""Existing-character operations and read-only material/texture inspection."""

from dataclasses import replace
import unittest
from unittest.mock import patch

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from object_core import BodyType, HumanoidSpec, generate_mesh, generate_proportions
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
            self.assertFalse(inspect_character(self.root).has_animation)
            rig.pose.bones['head'].rotation_quaternion = (0.99, 0.1, 0, 0)
            rig.pose.bones['head'].keyframe_insert(data_path='rotation_quaternion', frame=10)
            self.assertTrue(inspect_character(self.root).has_animation)
        finally:
            humanoid_blender.unregister()

    def test_idle_moves_upper_body_loops_and_preserves_existing_action(self):
        from humanoid_blender.animation import add_idle
        rig = add_basic_rig(self.root, bpy.context)
        self.scene.render.fps = 30
        self.scene.render.fps_base = 1.001
        action, end = add_idle(self.root, self.scene)
        period = 4 * self.scene.render.fps / self.scene.render.fps_base
        for curve in action.fcurves:
            self.assertAlmostEqual(curve.keyframe_points[-1].co.x, 1 + period, places=4)
            self.assertAlmostEqual(curve.evaluate(12), curve.evaluate(12 + period), places=5)
        self.scene.frame_set(1)
        first = rig.pose.bones['head'].matrix.copy()
        foot = rig.pose.bones['foot.left'].matrix.copy()
        self.scene.frame_set(60)
        self.assertNotEqual(first, rig.pose.bones['head'].matrix)
        self.assertEqual(foot, rig.pose.bones['foot.left'].matrix)
        self.assertTrue(inspect_character(self.root).has_animation)
        actions = set(bpy.data.actions)
        with self.assertRaisesRegex(ValueError, 'Existing animation'):
            add_idle(self.root, self.scene)
        self.assertEqual(rig.animation_data.action, action)
        self.assertEqual(actions, set(bpy.data.actions))

    def test_idle_rejects_pose_and_rolls_back_creation_failure(self):
        from humanoid_blender.animation import add_idle
        rig = add_basic_rig(self.root, bpy.context)
        bone = rig.pose.bones['head']
        bone.rotation_quaternion = (0.99, 0.1, 0, 0)
        with self.assertRaisesRegex(ValueError, 'rest pose'):
            add_idle(self.root, self.scene)
        bone.rotation_quaternion = (1, 0, 0, 0)
        before = set(bpy.data.actions)
        with patch('mathutils.Quaternion', side_effect=RuntimeError('injected failure')):
            with self.assertRaisesRegex(RuntimeError, 'injected failure'):
                add_idle(self.root, self.scene)
        self.assertEqual(before, set(bpy.data.actions))
        self.assertIsNone(rig.animation_data)

    def test_visible_mesh_motion_and_preview_controls(self):
        import humanoid_blender
        humanoid_blender.register()
        try:
            settings = self.scene.humanoid_settings
            settings.target = self.root
            rig = add_basic_rig(self.root, bpy.context)
            rig.data.pose_position = 'REST'
            self.scene.use_preview_range = True
            self.scene.frame_preview_start = self.scene.frame_preview_end = 1
            self.assertEqual(bpy.ops.humanoid.generate_idle(), {'FINISHED'})
            self.assertFalse(self.scene.use_preview_range)
            self.assertEqual(rig.data.pose_position, 'POSE')

            def points(part):
                obj = next(o for o in self.root.children if o.get('part_name') == part)
                evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
                return [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]

            self.scene.frame_set(1)
            hand, foot = points('hand.left'), points('foot.left')
            self.assertEqual(bpy.ops.humanoid.preview_idle(), {'FINISHED'})
            scale = self.scene.unit_settings.scale_length
            self.assertGreater(max((a-b).length for a, b in zip(hand, points('hand.left'))) * scale, 0.02)
            self.assertLess(max((a-b).length for a, b in zip(foot, points('foot.left'))) * scale, 1e-5)
            settings.asset_use = 'ANIMATED'
            bpy.ops.humanoid.prepare_materials()
            bpy.ops.humanoid.validate_character()
            self.assertFalse(any(row.status == 'ERROR' for row in settings.validation_results))
            rig.data.pose_position = 'REST'
            bpy.ops.humanoid.validate_character()
            self.assertTrue(any(row.code == 'animation' and row.status == 'ERROR' for row in settings.validation_results))
            for curve in rig.animation_data.action.fcurves:
                curve.mute = True
            self.assertFalse(inspect_character(self.root).has_animation)
        finally:
            humanoid_blender.unregister()

    def test_box_uses_shared_generation_and_static_validation(self):
        import humanoid_blender
        humanoid_blender.register()
        try:
            settings = self.scene.humanoid_settings
            settings.object_type = 'box'
            settings.box_width_cm = 200
            self.assertEqual(bpy.ops.humanoid.generate_blockout(), {'FINISHED'})
            root = settings.target
            self.assertEqual(root['object_type'], 'box')
            self.assertEqual(len(root.children), 1)
            self.assertEqual(settings.asset_use, 'STATIC')
            self.assertAlmostEqual(root.children[0].dimensions.x, 2)
            bpy.ops.humanoid.prepare_materials()
            bpy.ops.humanoid.validate_character()
            self.assertFalse(any(row.status == 'ERROR' for row in settings.validation_results))
            with self.assertRaisesRegex(ValueError, 'static object'):
                add_basic_rig(root, bpy.context)
        finally:
            humanoid_blender.unregister()

    def test_validation_reports_missing_target_and_zero_influence(self):
        from humanoid_blender.animation import add_idle
        rig = add_basic_rig(self.root, bpy.context)
        action, _ = add_idle(self.root, self.scene)
        rig.animation_data.action_influence = 0
        self.assertTrue(any('influence' in e for e in inspect_character(self.root).animation_errors))
        rig.animation_data.action_influence = 1
        action.fcurves[0].data_path = 'pose.bones["missing"].rotation_quaternion'
        self.assertTrue(any('target' in e for e in inspect_character(self.root).animation_errors))
        action.fcurves[1].keyframe_points[0].co.y = float('nan')
        self.assertTrue(any('non-finite' in e for e in inspect_character(self.root).animation_errors))

    def test_legacy_humanoid_root_remains_supported(self):
        from humanoid_blender.workflow import find_character
        self.root['generator'] = 'humanoid_blockout'
        rig = add_basic_rig(self.root, bpy.context)
        self.assertEqual(find_character(rig), self.root)
