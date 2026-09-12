# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy  # noqa: F401
except ModuleNotFoundError:
    bpy = None

from blender_adapter.working_asset_ui import save_editable_checkpoint


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class EditableCheckpointTests(unittest.TestCase):
    def test_checkpoint_forces_blend_extension_and_saves_copy(self):
        calls = []

        def fake_save(**kwargs):
            calls.append(kwargs)
            return {"FINISHED"}

        filepath = save_editable_checkpoint("/tmp/hero.checkpoint", fake_save)

        self.assertEqual("/tmp/hero.blend", filepath)
        self.assertEqual([{"filepath": "/tmp/hero.blend", "copy": True}], calls)

    def test_checkpoint_rejects_incomplete_blender_save(self):
        with self.assertRaisesRegex(RuntimeError, "did not finish"):
            save_editable_checkpoint("/tmp/hero.blend", lambda **kwargs: {"CANCELLED"})


if __name__ == "__main__":
    unittest.main()
