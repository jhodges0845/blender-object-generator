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
            (ui.HUMANOID_PT_panel, "Generate", 0),
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


if __name__ == "__main__":
    unittest.main()
