# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.animation import add_idle
from blender_adapter.modification import inspect_generated_asset
from blender_adapter.workflow import add_basic_rig
from object_core.modification import ModificationRequest, plan_modification
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderModificationInspectionTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for collection in tuple(bpy.data.collections):
            if collection.users == 0:
                bpy.data.collections.remove(collection)

    def _avian(self):
        provider = get_provider("avian")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name=provider.label, scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root, provider, values

    def test_pristine_generated_geometry_is_inspected_without_scene_mutation(self):
        root, provider, values = self._avian()
        before = root["asset_assistant_asset_id"]

        snapshot = inspect_generated_asset(root)

        self.assertEqual(before, root["asset_assistant_asset_id"])
        self.assertEqual(provider.key, snapshot.provider_key)
        self.assertEqual(provider.label, snapshot.provider_label)
        self.assertEqual(values, snapshot.parameter_values())
        self.assertTrue(snapshot.owns_geometry)
        self.assertFalse(snapshot.has_rig)
        self.assertFalse(snapshot.has_materials)
        self.assertFalse(snapshot.has_animations)
        self.assertEqual((), snapshot.animations)

    def test_mesh_edit_is_reported_as_ambiguous_for_destructive_modify(self):
        root, _, _ = self._avian()
        mesh = next(obj for obj in root.children if obj.type == "MESH")
        mesh.data.vertices[0].co.x += 0.25

        snapshot = inspect_generated_asset(root)
        plan = plan_modification(
            snapshot,
            ModificationRequest(parameter_changes=(("wingspan_cm", 110),)),
        )

        self.assertFalse(snapshot.owns_geometry)
        self.assertTrue(any("vertices were edited" in warning for warning in snapshot.warnings))
        self.assertFalse(plan.safe_to_apply)
        self.assertIn("Cannot safely replace unowned or ambiguous geometry", plan.blockers)

    def test_existing_rig_and_generated_animation_are_present_in_plan(self):
        root, _, _ = self._avian()
        bpy.context.view_layer.objects.active = root
        root.select_set(True)
        add_basic_rig(root, bpy.context)
        add_idle(root, bpy.context.scene)

        snapshot = inspect_generated_asset(root)
        plan = plan_modification(
            snapshot,
            ModificationRequest(parameter_changes=(("tail_length_cm", 28),)),
        )

        self.assertTrue(snapshot.has_rig)
        self.assertTrue(snapshot.owns_rig)
        self.assertTrue(snapshot.has_animations)
        self.assertTrue(snapshot.owns_animations)
        self.assertEqual(("Idle",), tuple(clip.clip_id for clip in snapshot.animations))
        self.assertEqual(("geometry", "rig", "animations"), plan.rebuild_components)


if __name__ == "__main__":
    unittest.main()
