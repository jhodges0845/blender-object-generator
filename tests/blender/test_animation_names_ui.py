# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None

from blender_adapter.adapter import create_character
from blender_adapter.animation import add_idle
from blender_adapter.animation_lifecycle import register_animation_action
from blender_adapter.animation_names_ui import _remove_action, _remove_button_text
from blender_adapter.animation_records import has_animation_record
from object_core.animations import AnimationSource
from object_core.objects import get_provider


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class AnimationNamesUiTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        self.before = {name: set(getattr(bpy.data, name)) for name in
                       ("objects", "meshes", "armatures", "collections", "materials", "images", "actions")}

    def tearDown(self):
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        for name, original in self.before.items():
            data = getattr(bpy.data, name)
            for item in set(data) - original:
                data.remove(item, do_unlink=True)

    def _rigged_human(self):
        provider = get_provider("human_experimental")
        values = {field.key: field.default for field in provider.parameters}
        mesh = provider.mesh(values)
        root = create_character(
            mesh,
            name="AnimationUiHuman",
            scene=bpy.context.scene,
            skeleton=provider.skeleton(values),
            skin_weights=provider.skin_weights(mesh, values),
        )
        root["object_type"] = provider.key
        for key, value in values.items():
            root[key] = value
        rig = next(child for child in root.children if child.type == "ARMATURE")
        return root, rig

    def test_generated_clip_delete_removes_owned_action(self):
        root, _ = self._rigged_human()
        action, _ = add_idle(root, bpy.context.scene)
        name = action.name

        self.assertEqual("Delete Clip", _remove_button_text(action))
        message = _remove_action(root, action)

        self.assertIn("Deleted Asset Assistant-owned clip", message)
        self.assertNotIn(name, bpy.data.actions)

    def test_artist_clip_remove_preserves_action_and_curves(self):
        root, rig = self._rigged_human()
        generated, _ = add_idle(root, bpy.context.scene)
        artist = generated.copy()
        artist.name = "Artist Imported Idle"
        for key in tuple(artist.keys()):
            if str(key).startswith("asset_assistant_"):
                del artist[key]
        if rig.animation_data and rig.animation_data.action == generated:
            rig.animation_data.action = None
        bpy.data.actions.remove(generated)

        record = register_animation_action(
            root,
            artist,
            source=AnimationSource.IMPORTED,
            export_name="ImportedIdle",
            fps=24.0,
        )
        frame_range = tuple(artist.frame_range)
        name = artist.name

        self.assertEqual("Remove from Asset Assistant", _remove_button_text(artist))
        message = _remove_action(root, artist, record.animation_id)

        self.assertIn("artist curves were preserved", message)
        self.assertIs(bpy.data.actions.get(name), artist)
        self.assertEqual(frame_range, tuple(artist.frame_range))
        self.assertFalse(has_animation_record(artist))


if __name__ == "__main__":
    unittest.main()
