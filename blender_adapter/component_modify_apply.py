# SPDX-License-Identifier: GPL-3.0-or-later
"""Host capability bridge for executable component operations in Modify."""

from dataclasses import replace

from .components import remove_component
from .core import AttachmentMode, ModificationRequest
from .skinned_components import remove_skinned_component

_TRANSPORT_ONLY_BLOCKER = "Component mutations are validated for transport but are not executable through Modify yet"
_REMOVE_ONLY_MIXED_BLOCKER = "Component removal must be applied separately from other Modify changes"
_BASE_WITH_COMPONENTS_BLOCKER = "Base geometry or rig regeneration with attached components is not executable through Modify yet"
_MULTI_REMOVE_BLOCKER = "Apply one component removal per Modify request so rollback boundaries remain explicit"
_PROVIDER_BLOCKER = "Component add/replace requires an executable component provider and is not available through Modify yet"


def _host_plan(core_plan, snapshot, request):
    """Refine portable planning with Blender capabilities without weakening core safety."""
    plan = core_plan(snapshot, request)
    blockers = list(plan.blockers)
    operations = plan.requested_component_operations

    if snapshot.components and plan.rebuild_components:
        blockers.append(_BASE_WITH_COMPONENTS_BLOCKER)

    if operations:
        only_remove = all(operation.operation == "remove" for operation in operations)
        has_other_changes = bool(
            plan.requested_parameter_changes
            or plan.requested_semantic_operations
            or plan.requested_animation_renames
        )
        if only_remove:
            blockers = [blocker for blocker in blockers if blocker != _TRANSPORT_ONLY_BLOCKER]
            if len(operations) != 1:
                blockers.append(_MULTI_REMOVE_BLOCKER)
            if has_other_changes:
                blockers.append(_REMOVE_ONLY_MIXED_BLOCKER)
        else:
            blockers = [blocker for blocker in blockers if blocker != _TRANSPORT_ONLY_BLOCKER]
            blockers.append(_PROVIDER_BLOCKER)

    return replace(plan, blockers=tuple(dict.fromkeys(blockers)))


def _remove_one(root, operation, snapshot):
    record = next(
        (component for component in snapshot.components if component.component_id == operation.component_id),
        None,
    )
    if record is None:
        raise ValueError("Component removal no longer matches the inspected asset: " + operation.component_id)
    if record.attachment_mode == AttachmentMode.SKINNED:
        remove_skinned_component(root, operation.component_id)
    else:
        remove_component(root, operation.component_id)


def install(modify_ui):
    """Install Blender-safe planning and apply support for component removal."""
    if getattr(modify_ui, "_asset_assistant_component_apply_installed", False):
        return

    core_plan = modify_ui.plan_modification
    original_apply = modify_ui._apply_external_request
    original_summary = modify_ui._request_summary

    def blender_plan(snapshot, request):
        return _host_plan(core_plan, snapshot, request)

    def component_aware_apply(context, root, request):
        snapshot = modify_ui.inspect_generated_asset(root)
        plan = blender_plan(snapshot, request)
        if plan.blockers:
            raise ValueError("Modify is blocked: " + "; ".join(plan.blockers))
        if plan.requested_component_operations:
            _remove_one(root, plan.requested_component_operations[0], snapshot)
            return modify_ui.inspect_generated_asset(root)
        return original_apply(context, root, request)

    def component_summary(plan):
        lines = original_summary(plan)
        if plan.requested_component_operations:
            if lines == ["No supported changes detected in request file."]:
                lines = []
            lines.append(
                "Component changes: "
                + ", ".join(
                    operation.operation + " " + operation.component_id
                    for operation in plan.requested_component_operations
                )
            )
        return lines

    modify_ui.plan_modification = blender_plan
    modify_ui._apply_external_request = component_aware_apply
    modify_ui._request_summary = component_summary
    modify_ui._asset_assistant_component_apply_installed = True


__all__ = ["install"]
