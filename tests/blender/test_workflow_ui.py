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

    def test_workflow_panels_share_one_ordered_asset_assistant_category(self):
        from blender_adapter import animation_names_ui, modify_ui, ui

        panels = (
            (ui.HUMANOID_PT_panel, "Create", 0),
            (modify_ui.ASSET_ASSISTANT_PT_modify, "Modify", 1),
            (ui.HUMANOID_PT_rigging, "Rig", 2),
            (ui.HUMANOID_PT_animations, "Animate", 3),
            (ui.HUMANOID_PT_validation, "Validate", 4),
            (ui.HUMANOID_PT_export, "Export", 5),
        )
        for panel, label, order in panels:
            self.assertEqual("Asset Assistant", panel.bl_category)
            self.assertEqual(label, panel.bl_label)
            self.assertEqual(order, panel.bl_order)

        names = animation_names_ui.ASSET_ASSISTANT_PT_animation_names
        self.assertEqual("Asset Assistant", names.bl_category)
        self.assertEqual("HUMANOID_PT_animations", names.bl_parent_id)

    def test_only_create_starts_expanded(self):
        from blender_adapter import modify_ui, ui

        self.assertNotIn("DEFAULT_CLOSED", ui.HUMANOID_PT_panel.bl_options)
        for panel in (
            modify_ui.ASSET_ASSISTANT_PT_modify,
            ui.HUMANOID_PT_rigging,
            ui.HUMANOID_PT_animations,
            ui.HUMANOID_PT_validation,
            ui.HUMANOID_PT_export,
        ):
            self.assertIn("DEFAULT_CLOSED", panel.bl_options)

    def test_component_hierarchy_keeps_existing_operator_contracts(self):
        from blender_adapter import workflow_ui

        class FakeRow:
            def __init__(self, calls):
                self.calls = calls
                self.enabled = True

            def operator(self, operator_id, text="", icon="NONE"):
                self.calls.append((operator_id, text, icon, self.enabled))

        class FakeBox:
            def __init__(self, calls):
                self.calls = calls

            def box(self):
                return FakeBox(self.calls)

            def row(self):
                return FakeRow(self.calls)

            def label(self, **_kwargs):
                return None

        class HairUi:
            pass

        class ClothingUi:
            @staticmethod
            def _supports_shirt(_target):
                return True

        class AccessoryUi:
            pass

        calls = []
        workflow_ui._draw_component_actions(
            FakeBox(calls), object(), HairUi, ClothingUi, AccessoryUi)

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


if __name__ == "__main__":
    unittest.main()
