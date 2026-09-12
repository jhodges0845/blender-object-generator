# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from object_core.modification import (
    AnimationSnapshot,
    AssetSnapshot,
    ModificationRequest,
    plan_modification,
)


class ModificationPlanningTests(unittest.TestCase):
    def _avian_snapshot(self, **overrides):
        values = {
            "asset_id": "asset-1",
            "provider_key": "avian",
            "provider_label": "Avian",
            "parameters": (
                ("body_length_cm", 42.0),
                ("body_width_cm", 16.0),
                ("body_height_cm", 20.0),
                ("wingspan_cm", 90.0),
                ("tail_length_cm", 22.0),
            ),
            "animations": (
                AnimationSnapshot("idle-1", "Idle"),
                AnimationSnapshot("walk-1", "Walk"),
                AnimationSnapshot("flight-1", "Flight"),
            ),
            "owns_geometry": True,
            "owns_rig": True,
            "owns_materials": True,
            "owns_animations": True,
        }
        values.update(overrides)
        return AssetSnapshot(**values)

    def test_omitted_values_are_preserved_and_no_rebuild_is_requested(self):
        plan = plan_modification(self._avian_snapshot(), ModificationRequest())

        self.assertTrue(plan.safe_to_apply)
        self.assertEqual((), plan.requested_parameter_changes)
        self.assertEqual((), plan.requested_animation_renames)
        self.assertEqual((), plan.rebuild_components)

    def test_parameter_change_requests_conservative_generated_rebuild(self):
        plan = plan_modification(
            self._avian_snapshot(),
            ModificationRequest(parameter_changes=(("wingspan_cm", 110),)),
        )

        self.assertTrue(plan.safe_to_apply)
        self.assertEqual((("wingspan_cm", 110.0),), plan.requested_parameter_changes)
        self.assertEqual(
            ("geometry", "rig", "materials", "animations"),
            plan.rebuild_components,
        )

    def test_animation_export_rename_is_metadata_only(self):
        plan = plan_modification(
            self._avian_snapshot(),
            ModificationRequest(animation_export_names=(("walk-1", "Bird Walk"),)),
        )

        self.assertTrue(plan.safe_to_apply)
        self.assertEqual((("walk-1", "Bird Walk"),), plan.requested_animation_renames)
        self.assertEqual((), plan.rebuild_components)

    def test_unchanged_request_values_are_removed_from_plan(self):
        plan = plan_modification(
            self._avian_snapshot(),
            ModificationRequest(
                parameter_changes=(("wingspan_cm", 90),),
                animation_export_names=(("walk-1", "Walk"),),
            ),
        )

        self.assertTrue(plan.safe_to_apply)
        self.assertEqual((), plan.requested_parameter_changes)
        self.assertEqual((), plan.requested_animation_renames)
        self.assertEqual((), plan.rebuild_components)

    def test_invalid_parameter_is_rejected_before_mutation_plan(self):
        with self.assertRaisesRegex(ValueError, "outside its supported range"):
            plan_modification(
                self._avian_snapshot(),
                ModificationRequest(parameter_changes=(("wingspan_cm", 9999),)),
            )

    def test_unknown_parameter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported parameter"):
            plan_modification(
                self._avian_snapshot(),
                ModificationRequest(parameter_changes=(("beak_magic", 3),)),
            )

    def test_unowned_generated_component_blocks_destructive_change(self):
        plan = plan_modification(
            self._avian_snapshot(owns_rig=False),
            ModificationRequest(parameter_changes=(("body_length_cm", 48),)),
        )

        self.assertFalse(plan.safe_to_apply)
        self.assertIn("Cannot safely replace unowned or ambiguous rig", plan.blockers)

    def test_unowned_animation_blocks_export_rename(self):
        plan = plan_modification(
            self._avian_snapshot(owns_animations=False),
            ModificationRequest(animation_export_names=(("idle-1", "Rest"),)),
        )

        self.assertFalse(plan.safe_to_apply)
        self.assertIn("Cannot safely rename unowned or ambiguous animations", plan.blockers)

    def test_duplicate_requested_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate parameter change key"):
            plan_modification(
                self._avian_snapshot(),
                ModificationRequest(
                    parameter_changes=(("wingspan_cm", 100), ("wingspan_cm", 110)),
                ),
            )

    def test_snapshot_provider_must_match_registry(self):
        with self.assertRaisesRegex(ValueError, "provider label"):
            plan_modification(
                self._avian_snapshot(provider_label="Bird"),
                ModificationRequest(),
            )


if __name__ == "__main__":
    unittest.main()
