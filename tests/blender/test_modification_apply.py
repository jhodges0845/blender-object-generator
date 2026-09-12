# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.animation import add_idle, add_locomotion
from blender_adapter.modification import apply_metadata_modification, inspect_generated_asset
from blender_adapter.workflow import add_basic_rig
from object_core.modification import ModificationRequest, plan_modification
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class BlenderModificationApplyTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for collection in tuple(bpy.data.collections):
            if collection.users == 0:
                bpy.data.collections.remove(collection)

    def _animated_avian(self, include_walk=False):
        provider = get_provider("avian")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name=provider.label, scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        bpy.context.view_layer.objects.active = root
        root.select_set(True)
        add_basic_rig(root, bpy.context)
        add_idle(root, bpy.context.scene)
        if include_walk:
            add_locomotion(root, bpy.context.scene)
        return root

    def test_metadata_only_plan_renames_generated_animation(self):
        root = self._animated_avian()
        snapshot = inspect_generated_asset(root)
        plan = plan_modification(
            snapshot,
            ModificationRequest(animation_export_names=(("Idle", "Rest"),)),
        )

        result = apply_metadata_modification(root, plan)

        self.assertTrue(plan.safe_to_apply)
        self.assertEqual((), plan.rebuild_components)
        self.assertEqual(("Rest",), tuple(clip.export_name for clip in result.animations))
        self.assertEqual("Rest", inspect_generated_asset(root).animations[0].export_name)

    def test_duplicate_final_export_name_is_rejected_without_partial_mutation(self):
        root = self._animated_avian(include_walk=True)
        before = inspect_generated_asset(root)
        plan = plan_modification(
            before,
            ModificationRequest(animation_export_names=(("Idle", "Walk"),)),
        )

        with self.assertRaisesRegex(ValueError, "must remain unique"):
            apply_metadata_modification(root, plan)

        after = inspect_generated_asset(root)
        self.assertEqual(
            tuple((clip.clip_id, clip.export_name) for clip in before.animations),
            tuple((clip.clip_id, clip.export_name) for clip in after.animations),
        )

    def test_metadata_apply_rejects_parameter_rebuild_plan(self):
        root = self._animated_avian()
        snapshot = inspect_generated_asset(root)
        plan = plan_modification(
            snapshot,
            ModificationRequest(parameter_changes=(("tail_length_cm", 28),)),
        )

        with self.assertRaisesRegex(ValueError, "metadata-only"):
            apply_metadata_modification(root, plan)

        self.assertEqual(snapshot.parameter_values(), inspect_generated_asset(root).parameter_values())


if __name__ == "__main__":
    unittest.main()
