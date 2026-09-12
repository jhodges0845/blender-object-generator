# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    import bpy
except ModuleNotFoundError:
    bpy = None


@unittest.skipIf(bpy is None, "requires Blender; use scripts/test_blender.py")
class WorkflowSidebarTests(unittest.TestCase):
    def setUp(self):
        import blender_adapter as addon
        self.addon = addon
        addon.register()

    def tearDown(self):
        self.addon.unregister()

    def test_sidebar_uses_one_visible_asset_assistant_workspace(self):
        from blender_adapter import animation_names_ui, modify_ui, ui

        self.assertEqual("Asset Assistant", ui.HUMANOID_PT_panel.bl_label)
        self.assertEqual("Asset Assistant", ui.HUMANOID_PT_panel.bl_category)
        self.assertTrue(getattr(ui.HUMANOID_PT_panel.draw, "_asset_assistant_workspace", False))
        self.assertNotIn("DEFAULT_CLOSED", ui.HUMANOID_PT_panel.bl_options)

        legacy_panels = (
            modify_ui.ASSET_ASSISTANT_PT_modify,
            ui.HUMANOID_PT_rigging,
            ui.HUMANOID_PT_animations,
            ui.HUMANOID_PT_validation,
            ui.HUMANOID_PT_export,
            animation_names_ui.ASSET_ASSISTANT_PT_animation_names,
        )
        for panel in legacy_panels:
            self.assertEqual("Asset Assistant", panel.bl_category)
            self.assertFalse(panel.poll(bpy.context), panel.bl_idname + " should be hidden from the sidebar")

    def test_workspace_navigation_properties_are_registered(self):
        from blender_adapter import ui

        settings = bpy.context.scene.humanoid_settings
        self.assertEqual("CREATE", settings.asset_assistant_workspace)
        self.assertEqual("GENERATE", settings.asset_assistant_create_view)

        settings.asset_assistant_workspace = "ANIMATE"
        settings.asset_assistant_create_view = "MODIFY"
        self.assertEqual("ANIMATE", settings.asset_assistant_workspace)
        self.assertEqual("MODIFY", settings.asset_assistant_create_view)

    def test_repeated_registration_keeps_one_export_fastpath_layer(self):
        from blender_adapter import ui

        first_draw = ui.HUMANOID_PT_export.draw
        self.assertTrue(getattr(first_draw, "_asset_assistant_fastpath", False))

        self.addon.unregister()
        self.addon.register()

        second_draw = ui.HUMANOID_PT_export.draw
        self.assertTrue(getattr(second_draw, "_asset_assistant_fastpath", False))
        self.assertFalse(
            getattr(getattr(second_draw, "_asset_assistant_wrapped_draw", None), "_asset_assistant_fastpath", False),
            "Export fast path stacked on top of another fast path",
        )

    def test_supported_blender_metadata_matches_required_runtime(self):
        self.assertEqual((5, 2, 1), self.addon.bl_info["blender"])

    def test_component_hierarchy_keeps_existing_operator_contracts(self):
        from blender_adapter import workflow_ui

        class FakeRow:
            def __init__(self, calls):
                self.calls = calls
                self.enabled = True
                self.scale_y = 1.0

            def operator(self, operator_id, text="", icon="NONE"):
                self.calls.append((operator_id, text, icon, self.enabled))

        class FakeBox:
            def __init__(self, calls, labels):
                self.calls = calls
                self.labels = labels

            def box(self):
                return FakeBox(self.calls, self.labels)

            def row(self):
                return FakeRow(self.calls)

            def label(self, text="", **_kwargs):
                self.labels.append(text)

        class HairUi:
            pass

        class ClothingUi:
            @staticmethod
            def _supports_shirt(_target):
                return True

        class AccessoryUi:
            pass

        calls = []
        labels = []
        workflow_ui._draw_component_actions(
            FakeBox(calls, labels), object(), HairUi, ClothingUi, AccessoryUi)

        self.assertEqual(
            [operator_id for operator_id, _text, _icon, _enabled in calls],
            [
                "asset_assistant.generate_hair_shell",
                "asset_assistant.generate_basic_shirt",
                "asset_assistant.generate_ring_component",
                "asset_assistant.generate_self_rigged_accessory",
                "asset_assistant.adopt_selected_component",
            ],
        )
        self.assertTrue(all(enabled for _operator_id, _text, _icon, enabled in calls))
        self.assertIn("Adopted mesh geometry becomes Asset Assistant-managed.", labels)
        self.assertIn("Existing materials remain artist-owned.", labels)
        self.assertNotIn("Existing geometry and artist materials remain yours.", labels)

    def test_animation_adoption_remains_separate_and_preserves_operator_contract(self):
        from blender_adapter import workflow_ui

        class FakeObject:
            def __init__(self, object_type):
                self.type = object_type

        class FakeTarget:
            children = (FakeObject("ARMATURE"),)

        class FakeRow:
            def __init__(self, calls):
                self.calls = calls
                self.enabled = True
                self.scale_y = 1.0

            def operator(self, operator_id, text="", icon="NONE"):
                self.calls.append((operator_id, text, icon, self.enabled))

        class FakeBox:
            def __init__(self, calls, labels):
                self.calls = calls
                self.labels = labels

            def row(self):
                return FakeRow(self.calls)

            def label(self, text="", **_kwargs):
                self.labels.append(text)

        calls = []
        labels = []
        workflow_ui._draw_animation_adoption(FakeBox(calls, labels), FakeTarget())

        self.assertIn("Bring Your Own Animation", labels)
        self.assertEqual(
            [("asset_assistant.adopt_animation_action", "Adopt Existing Action", "ACTION", True)],
            calls,
        )


if __name__ == "__main__":
    unittest.main()
