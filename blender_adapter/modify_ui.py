# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing Modify workflow built on the portable inspect/plan/apply contract."""

import bpy

from .core import ModificationRequest, plan_modification
from .modification import apply_parameter_modification, inspect_generated_asset
from .workflow import find_character, provider_for


_SUMMARY_KEY = "asset_assistant_modify_summary"
_STATUS_KEY = "asset_assistant_modify_status"


def _character(context):
    settings = getattr(context.scene, "humanoid_settings", None) if context.scene else None
    root = settings.target if settings and settings.target else find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


def _field_name(ui, provider, field):
    return ui._field_name(provider, field)


def _sync_settings_from_asset(context, root):
    from . import ui

    settings = context.scene.humanoid_settings
    provider = provider_for(root)
    for field in provider.parameters:
        if field.key not in root:
            raise ValueError("Missing saved generation parameter: " + field.label)
        setattr(settings, _field_name(ui, provider, field), root[field.key])
    settings.target = root
    return provider


def _parameter_request(context, root):
    from . import ui

    settings = context.scene.humanoid_settings
    provider = provider_for(root)
    changes = []
    for field in provider.parameters:
        value = getattr(settings, _field_name(ui, provider, field))
        if field.key not in root or value != root[field.key]:
            changes.append((field.key, value))
    return ModificationRequest(parameter_changes=tuple(changes))


def _plan(context, root):
    snapshot = inspect_generated_asset(root)
    request = _parameter_request(context, root)
    return snapshot, plan_modification(snapshot, request)


def _store_report(scene, status, lines):
    scene[_STATUS_KEY] = status
    scene[_SUMMARY_KEY] = "\n".join(lines)


def _refresh_validation(context):
    from . import ui

    settings = context.scene.humanoid_settings
    settings.validation_results.clear()
    for issue in ui._export_issues(context):
        row = settings.validation_results.add()
        row.code, row.status, row.message = issue.code, issue.status, issue.message


class ASSET_ASSISTANT_OT_modify_inspect(bpy.types.Operator):
    bl_idname = "asset_assistant.modify_inspect"
    bl_label = "Inspect Asset"
    bl_description = "Read the selected generated asset into Modify without changing it"

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        root = _character(context)
        try:
            provider = _sync_settings_from_asset(context, root)
            snapshot = inspect_generated_asset(root)
        except (ValueError, TypeError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        lines = [provider.label + " inspected."]
        lines.extend(snapshot.warnings or ("No preservation warnings detected.",))
        _store_report(context.scene, "INSPECTED", lines)
        self.report({"INFO"}, provider.label + " loaded for Modify.")
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_modify_preview(bpy.types.Operator):
    bl_idname = "asset_assistant.modify_preview"
    bl_label = "Preview Changes"
    bl_description = "Plan changes and preservation impact without mutating the asset"

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        root = _character(context)
        try:
            snapshot, plan = _plan(context, root)
        except (ValueError, TypeError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        if not plan.requested_parameter_changes:
            lines = ["No provider parameter changes detected."]
            lines.extend(snapshot.warnings)
            _store_report(context.scene, "NO_CHANGES", lines)
            self.report({"INFO"}, "No parameter changes to apply.")
            return {"FINISHED"}

        changed = ", ".join(key for key, _ in plan.requested_parameter_changes)
        rebuild = ", ".join(plan.rebuild_components) or "none"
        lines = ["Changes: " + changed, "Rebuild: " + rebuild]
        if plan.blockers:
            lines.extend("Blocked: " + blocker for blocker in plan.blockers)
            _store_report(context.scene, "BLOCKED", lines)
            self.report({"WARNING"}, "Modify plan is blocked; review preservation warnings.")
        else:
            lines.append("Safe to apply with current ownership checks.")
            _store_report(context.scene, "READY", lines)
            self.report({"INFO"}, "Modify plan is ready for review and apply.")
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_modify_apply(bpy.types.Operator):
    bl_idname = "asset_assistant.modify_apply"
    bl_label = "Apply Changes"
    bl_description = "Re-inspect, re-plan, and transactionally apply supported parameter changes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        root = _character(context)
        try:
            _, plan = _plan(context, root)
            if not plan.requested_parameter_changes:
                raise ValueError("No provider parameter changes to apply.")
            if plan.blockers:
                raise ValueError("Modify is blocked: " + "; ".join(plan.blockers))
            result = apply_parameter_modification(root, plan)
            _sync_settings_from_asset(context, root)
            _refresh_validation(context)
        except (ValueError, TypeError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        lines = ["Changes applied successfully.", "Validation refreshed after Modify."]
        lines.extend(result.warnings)
        _store_report(context.scene, "APPLIED", lines)
        self.report({"INFO"}, "Changes applied and validation refreshed.")
        return {"FINISHED"}


class ASSET_ASSISTANT_PT_modify(bpy.types.Panel):
    bl_label = "Modify"
    bl_idname = "ASSET_ASSISTANT_PT_modify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Modify"

    def draw(self, context):
        from . import ui

        layout = self.layout
        if context.mode != "OBJECT":
            op = layout.operator("object.mode_set", text="Return to Object Mode")
            op.mode = "OBJECT"
            return
        settings = context.scene.humanoid_settings
        layout.prop(settings, "target")
        root = _character(context)
        if root is None:
            layout.label(text="Choose an Asset Assistant asset.")
            return
        try:
            provider = provider_for(root)
        except (ValueError, TypeError, AttributeError) as error:
            layout.label(text=str(error), icon="ERROR")
            return

        header = layout.box()
        header.label(text="Current Asset: " + root.name)
        header.label(text="Provider: " + provider.label)
        header.operator("asset_assistant.modify_inspect", text="Inspect / Load Current Values", icon="VIEWZOOM")

        params = layout.box()
        params.label(text="Supported Parameters")
        for field in provider.parameters:
            params.prop(settings, _field_name(ui, provider, field))

        actions = layout.box()
        actions.operator("asset_assistant.modify_preview", text="Preview Changes", icon="PREVIEW_RANGE")
        actions.operator("asset_assistant.modify_apply", text="Apply Changes", icon="CHECKMARK")
        actions.label(text="Apply re-checks ownership before changing anything.")
        if getattr(provider, "supports_idle", False) or getattr(provider, "supports_locomotion", False):
            actions.label(text="Animation export names remain editable in Animations.")

        status = context.scene.get(_STATUS_KEY)
        summary = context.scene.get(_SUMMARY_KEY, "")
        if status or summary:
            report = layout.box()
            report.label(text="Modify Review" + (" — " + status.replace("_", " ").title() if status else ""))
            for line in str(summary).splitlines():
                report.label(text=line, icon="ERROR" if line.startswith("Blocked:") else "NONE")


_CLASSES = (
    ASSET_ASSISTANT_OT_modify_inspect,
    ASSET_ASSISTANT_OT_modify_preview,
    ASSET_ASSISTANT_OT_modify_apply,
    ASSET_ASSISTANT_PT_modify,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
