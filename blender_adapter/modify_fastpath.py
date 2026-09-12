# SPDX-License-Identifier: GPL-3.0-or-later
"""Small runtime fast paths for imported Modify without weakening validation."""


def install(modify_ui):
    """Reuse an already-current imported-request snapshot at the helper boundary."""

    def apply_external_request(context, root, request, *, snapshot=None):
        snapshot = snapshot if snapshot is not None else modify_ui.inspect_generated_asset(root)
        plan = modify_ui.plan_modification(snapshot, request)
        if plan.blockers:
            raise ValueError("Modify is blocked: " + "; ".join(plan.blockers))
        if not (
            plan.requested_parameter_changes
            or plan.requested_semantic_operations
            or plan.requested_animation_renames
        ):
            raise ValueError("Imported request contains no changes to apply.")

        if plan.requested_parameter_changes:
            parameter_request = modify_ui.ModificationRequest(
                parameter_changes=plan.requested_parameter_changes,
            )
            parameter_plan = modify_ui.plan_modification(snapshot, parameter_request)
            snapshot = modify_ui.apply_parameter_modification(root, parameter_plan)

        if plan.requested_semantic_operations:
            semantic_request = modify_ui.ModificationRequest(
                semantic_operations=plan.requested_semantic_operations,
            )
            semantic_plan = modify_ui.plan_modification(snapshot, semantic_request)
            snapshot = modify_ui.apply_semantic_modification(root, semantic_plan)

        if plan.requested_animation_renames:
            rename_request = modify_ui.ModificationRequest(
                animation_export_names=plan.requested_animation_renames,
            )
            rename_plan = modify_ui.plan_modification(snapshot, rename_request)
            snapshot = modify_ui.apply_metadata_modification(root, rename_plan)

        return snapshot

    def apply_imported_execute(self, context):
        root = modify_ui._character(context)
        try:
            snapshot = modify_ui.inspect_generated_asset(root)
            request = modify_ui.request_from_json(
                context.scene[modify_ui._IMPORTED_REQUEST_KEY],
                snapshot,
            )
            result = apply_external_request(
                context,
                root,
                request,
                snapshot=snapshot,
            )
            modify_ui._sync_settings_from_asset(context, root)
            modify_ui._refresh_validation(context)
        except (ValueError, TypeError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        lines = ["Imported changes applied successfully.", "Validation refreshed after Modify."]
        if result.semantic_operations:
            lines.append(str(len(result.semantic_operations)) + " semantic patch operation(s) active.")
        lines.extend(result.warnings)
        modify_ui._store_report(context.scene, "IMPORTED_APPLIED", lines)
        self.report({"INFO"}, "Imported changes applied and validation refreshed.")
        return {"FINISHED"}

    modify_ui._apply_external_request = apply_external_request
    modify_ui.ASSET_ASSISTANT_OT_modify_apply_imported.execute = apply_imported_execute
