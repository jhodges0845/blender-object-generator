# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only preflight and explicit onboarding for artist-created assets."""

import bpy

from .workflow import is_external_asset, is_generated, is_managed_asset


_STATUS_KEY = "asset_assistant_inspection_status"
_NAME_KEY = "asset_assistant_inspection_name"
_SUMMARY_KEY = "asset_assistant_inspection_summary"
_METRICS_KEY = "asset_assistant_inspection_metrics"
_CAN_ADOPT_KEY = "asset_assistant_inspection_can_adopt"
_IMPORT_GROUP_KEY = "asset_assistant_import_group"
_IMPORT_ROOT_KEY = "asset_assistant_import_root"
_EXTERNAL_ASSET_KEY = "asset_assistant_external_asset"
_EXTERNAL_CAPABILITY_KEY = "asset_assistant_external_capability"

_ORIGINAL_DRAW_ARTIST_MODIFY = None


def _root_object(obj):
    root = obj
    while getattr(root, "parent", None) is not None:
        root = root.parent
    return root


def _walk_hierarchy(root):
    yield root
    for child in tuple(getattr(root, "children", ())):
        yield from _walk_hierarchy(child)


def _import_group(obj):
    if obj is None:
        return ""
    return str(obj.get(_IMPORT_GROUP_KEY, ""))


def _import_boundary(selected):
    """Return the stable imported asset root and all objects in its import group."""
    group = _import_group(selected)
    if not group:
        root = _root_object(selected)
        return root, list(_walk_hierarchy(root))

    objects = [obj for obj in bpy.data.objects if _import_group(obj) == group]
    if not objects:
        root = _root_object(selected)
        return root, list(_walk_hierarchy(root))
    root = next((obj for obj in objects if bool(obj.get(_IMPORT_ROOT_KEY, False))), None)
    if root is None:
        roots = [obj for obj in objects if getattr(obj, "parent", None) not in objects]
        root = roots[0] if roots else selected
    return root, objects


def _animation_count(obj):
    animation_data = getattr(obj, "animation_data", None)
    if animation_data is None:
        return 0
    count = 1 if getattr(animation_data, "action", None) is not None else 0
    count += len(tuple(getattr(animation_data, "nla_tracks", ())))
    return count


def inspect_selected_asset(selected):
    """Return a non-destructive structural preflight for the selected Blender object."""
    if selected is None:
        raise ValueError("Select an object to inspect first.")

    root, objects = _import_boundary(selected)
    meshes = [obj for obj in objects if getattr(obj, "type", None) == "MESH"]
    armatures = {id(obj): obj for obj in objects if getattr(obj, "type", None) == "ARMATURE"}

    for mesh in meshes:
        for modifier in tuple(getattr(mesh, "modifiers", ())):
            if getattr(modifier, "type", None) != "ARMATURE":
                continue
            rig = getattr(modifier, "object", None)
            if rig is not None:
                armatures[id(rig)] = rig

    material_ids = set()
    for mesh in meshes:
        for slot in tuple(getattr(mesh, "material_slots", ())):
            material = getattr(slot, "material", None)
            if material is not None:
                material_ids.add(id(material))

    animation_count = sum(_animation_count(obj) for obj in objects)
    for rig in armatures.values():
        if rig not in objects:
            animation_count += _animation_count(rig)

    metrics = {
        "meshes": len(meshes),
        "armatures": len(armatures),
        "materials": len(material_ids),
        "animations": animation_count,
    }

    notes = []
    if is_generated(root):
        status = "READY"
        notes.append("Recognized Asset Assistant generated metadata.")
        notes.append("This asset is ready for the generated-provider workflow.")
    elif is_external_asset(root):
        status = "EXTERNAL_READY"
        notes.append("Imported asset is enrolled with Asset Assistant.")
        notes.append("Artist geometry, rigs, materials, weights and animation curves remain artist-owned.")
        notes.append("Generated-provider shape parameters stay disabled for this asset.")
    elif not meshes:
        status = "NEEDS_SETUP"
        notes.append("No mesh geometry was found in the selected asset boundary.")
        notes.append("Choose a mesh or the root object of an artist-created asset.")
    else:
        status = "REVIEW"
        notes.append("Artist-created asset detected; no Asset Assistant ownership was added.")
        if _import_group(selected):
            notes.append("The complete imported file hierarchy is being inspected as one asset candidate.")
        if len(armatures) == 0:
            notes.append("No armature detected; this can be enrolled as a static asset.")
        elif len(armatures) == 1:
            notes.append("One armature detected; this can be enrolled with imported-rig capability.")
        else:
            notes.append("Multiple armatures detected; choose/clean the intended rig before enrollment.")
        notes.append("Inspection is read-only. Enrollment is always explicit.")

    return {
        "root": root,
        "name": getattr(root, "name", "Selected Asset"),
        "status": status,
        "metrics": metrics,
        "notes": tuple(notes),
        "can_adopt": bool(meshes) and len(armatures) <= 1 and not is_managed_asset(root),
    }


def _metric_text(metrics):
    return (
        f"{metrics['meshes']} Mesh"
        + ("es" if metrics["meshes"] != 1 else "")
        + f"  •  {metrics['armatures']} Rig"
        + ("s" if metrics["armatures"] != 1 else "")
        + f"  •  {metrics['materials']} Material"
        + ("s" if metrics["materials"] != 1 else "")
        + f"  •  {metrics['animations']} Clip"
        + ("s" if metrics["animations"] != 1 else "")
    )


def store_inspection_report(scene, report):
    scene[_STATUS_KEY] = report["status"]
    scene[_NAME_KEY] = report["name"]
    scene[_METRICS_KEY] = _metric_text(report["metrics"])
    scene[_SUMMARY_KEY] = "\n".join(report["notes"])
    scene[_CAN_ADOPT_KEY] = bool(report.get("can_adopt", False))


_store_report = store_inspection_report


def adopt_external_asset(context, selected):
    """Explicitly enroll one inspected external base asset without claiming artist data."""
    report = inspect_selected_asset(selected)
    if report["status"] in {"READY", "EXTERNAL_READY"}:
        return report["root"]
    if not report.get("can_adopt"):
        if report["metrics"]["armatures"] > 1:
            raise ValueError("External base-asset enrollment currently supports at most one armature.")
        raise ValueError("This selection is not ready to enroll as an Asset Assistant base asset.")

    root = report["root"]
    metrics = report["metrics"]
    capability = "ANIMATED" if metrics["animations"] else ("RIGGED" if metrics["armatures"] else "STATIC")
    root[_EXTERNAL_ASSET_KEY] = True
    root["asset_assistant_source"] = "ADOPTED"
    root[_EXTERNAL_CAPABILITY_KEY] = capability

    settings = context.scene.humanoid_settings
    settings.target = root
    settings.asset_use = capability
    refreshed = inspect_selected_asset(root)
    store_inspection_report(context.scene, refreshed)
    return root


def draw_inspection_report(layout, scene):
    status = scene.get(_STATUS_KEY)
    if not status:
        return

    labels = {
        "READY": ("ASSET ASSISTANT READY", "CHECKMARK"),
        "EXTERNAL_READY": ("IMPORTED ASSET READY", "CHECKMARK"),
        "REVIEW": ("INSPECTION COMPLETE", "INFO"),
        "NEEDS_SETUP": ("NEEDS SETUP", "ERROR"),
    }
    title, icon = labels.get(status, ("INSPECTION", "INFO"))
    report = layout.box()
    header = report.row(align=True)
    header.label(text=title, icon=icon)
    name = scene.get(_NAME_KEY, "")
    if name:
        header.label(text=name)
    metrics = scene.get(_METRICS_KEY, "")
    if metrics:
        report.label(text=metrics)
    for line in str(scene.get(_SUMMARY_KEY, "")).splitlines():
        report.label(text=line)
    if status == "REVIEW":
        action = report.row()
        action.scale_y = 1.35
        action.enabled = bool(scene.get(_CAN_ADOPT_KEY, False))
        action.operator("asset_assistant.adopt_external_asset", text="Use with Asset Assistant", icon="IMPORT")
        if not action.enabled:
            report.label(text="Resolve the inspection blocker before enrollment.", icon="INFO")


class ASSET_ASSISTANT_OT_inspect_selected_asset(bpy.types.Operator):
    bl_idname = "asset_assistant.inspect_selected_asset"
    bl_label = "Inspect Selected Asset"
    bl_description = "Read mesh, rig, material and animation structure without changing the selected asset"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and context.active_object is not None

    def execute(self, context):
        try:
            report = inspect_selected_asset(context.active_object)
        except (ValueError, TypeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        store_inspection_report(context.scene, report)
        self.report({"INFO"}, "Inspection complete. No changes were made.")
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_adopt_external_asset(bpy.types.Operator):
    bl_idname = "asset_assistant.adopt_external_asset"
    bl_label = "Use with Asset Assistant"
    bl_description = "Enroll this imported asset as the current workflow target while preserving artist-owned data"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and context.active_object is not None

    def execute(self, context):
        try:
            root = adopt_external_asset(context, context.active_object)
        except (ValueError, TypeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, root.name + " is now the current imported Asset Assistant asset.")
        return {"FINISHED"}


def _draw_external_modify(panel, context, ui, modify_ui):
    root = modify_ui._character(context)
    if root is None or not is_external_asset(root):
        return False
    layout = panel.layout
    card = layout.box()
    card.label(text="IMPORTED ASSET", icon="IMPORT")
    card.label(text=root.name)
    capability = str(root.get(_EXTERNAL_CAPABILITY_KEY, "STATIC")).title()
    card.label(text="Capability: " + capability)
    card.label(text="Artist-owned geometry and rig data are preserved.")
    card.label(text="Generated-provider shape controls do not apply to imported geometry.")
    inspect_row = card.row(); inspect_row.scale_y = 1.2
    inspect_row.operator("asset_assistant.inspect_selected_asset", text="Refresh Inspection", icon="VIEWZOOM")
    guidance = layout.box()
    guidance.label(text="SAFE IMPORTED-ASSET WORKFLOW", icon="INFO")
    guidance.label(text="Use Components, Animate and Export where validation permits.")
    guidance.label(text="Provider-specific regeneration stays disabled to avoid destructive guesses.")
    return True


def install(ui, workflow_ui=None, modify_ui=None):
    """Install external-asset target polling before Blender registers settings."""
    annotations = ui.HUMANOID_PG_settings.__annotations__
    annotations["target"] = ui.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        poll=lambda _settings, obj: is_managed_asset(obj),
        update=ui._clear_report,
    )

    if workflow_ui is not None and modify_ui is not None:
        global _ORIGINAL_DRAW_ARTIST_MODIFY
        if _ORIGINAL_DRAW_ARTIST_MODIFY is None:
            _ORIGINAL_DRAW_ARTIST_MODIFY = workflow_ui._draw_artist_modify

            def draw_artist_modify(panel, context, current_ui, current_modify_ui):
                if _draw_external_modify(panel, context, current_ui, current_modify_ui):
                    return
                return _ORIGINAL_DRAW_ARTIST_MODIFY(panel, context, current_ui, current_modify_ui)

            workflow_ui._draw_artist_modify = draw_artist_modify


_CLASSES = (
    ASSET_ASSISTANT_OT_inspect_selected_asset,
    ASSET_ASSISTANT_OT_adopt_external_asset,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "inspect_selected_asset",
    "store_inspection_report",
    "adopt_external_asset",
    "draw_inspection_report",
    "install",
    "register",
    "unregister",
]
