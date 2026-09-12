# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
import unittest
from pathlib import Path

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.working_asset_ui import (
    open_editable_checkpoint,
    save_editable_checkpoint,
    validate_checkpoint_scene,
)
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class EditableCheckpointTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        scene = bpy.context.scene
        for key in (
            "asset_assistant_working_state_kind",
            "asset_assistant_working_state_version",
            "asset_assistant_working_state_status",
            "asset_assistant_working_state_message",
        ):
            if key in scene:
                del scene[key]
        scene.humanoid_settings.target = None

    def _human(self):
        provider = get_provider("human_experimental")
        values = {field.key: field.default for field in provider.parameters}
        root = create_character(provider.mesh(values), name=provider.label, scene=bpy.context.scene)
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        return root

    def test_checkpoint_forces_blend_extension_and_saves_copy(self):
        calls = []

        def fake_save(**kwargs):
            calls.append(kwargs)
            return {"FINISHED"}

        filepath = save_editable_checkpoint("/tmp/hero.checkpoint", fake_save)

        self.assertEqual("/tmp/hero.blend", filepath)
        self.assertEqual([{"filepath": "/tmp/hero.blend", "copy": True}], calls)

    def test_checkpoint_marks_saved_copy_but_restores_current_scene(self):
        scene = bpy.context.scene
        observed = []

        def fake_save(**kwargs):
            observed.append((
                scene.get("asset_assistant_working_state_kind"),
                scene.get("asset_assistant_working_state_version"),
            ))
            return {"FINISHED"}

        save_editable_checkpoint("/tmp/hero.blend", fake_save, scene)

        self.assertEqual([("asset-assistant-editable-checkpoint", 1)], observed)
        self.assertNotIn("asset_assistant_working_state_kind", scene)
        self.assertNotIn("asset_assistant_working_state_version", scene)

    def test_checkpoint_rejects_incomplete_blender_save(self):
        with self.assertRaisesRegex(RuntimeError, "did not finish"):
            save_editable_checkpoint("/tmp/hero.blend", lambda **kwargs: {"CANCELLED"})

    def test_open_requires_blend_file_and_uses_open_mainfile_contract(self):
        calls = []
        with tempfile.NamedTemporaryFile(suffix=".blend") as checkpoint:
            filepath = open_editable_checkpoint(
                checkpoint.name,
                lambda **kwargs: calls.append(kwargs) or {"FINISHED"},
            )
        self.assertTrue(filepath.endswith(".blend"))
        self.assertEqual([{"filepath": filepath}], calls)

    def test_reopened_checkpoint_revalidates_asset_and_restores_single_target(self):
        scene = bpy.context.scene
        root = self._human()
        scene["asset_assistant_working_state_kind"] = "asset-assistant-editable-checkpoint"
        scene["asset_assistant_working_state_version"] = 1

        snapshots = validate_checkpoint_scene(scene)

        self.assertEqual(1, len(snapshots))
        self.assertEqual(root.get("asset_assistant_asset_id"), snapshots[0].asset_id)
        self.assertEqual(root, scene.humanoid_settings.target)
        self.assertEqual("READY", scene["asset_assistant_working_state_status"])

    def test_reopen_validation_rejects_unmarked_blend_scene(self):
        with self.assertRaisesRegex(ValueError, "not marked"):
            validate_checkpoint_scene(bpy.context.scene)


if __name__ == "__main__":
    unittest.main()
