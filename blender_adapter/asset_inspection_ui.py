# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only preflight for artist-created or Asset Assistant assets."""

import bpy

from .workflow import is_generated


_STATUS_KEY = "asset_assistant_inspection_status"
_NAME_KEY = "asset_assistant_inspection_name"
_SUMMARY_KEY = "asset_assistant_inspection_summary"
_METRICS_KEY = "asset_assistant_inspection_metrics"


def _root_object(obj):
    root = obj
    while getattr(root, "parent", None) is not None:
        root = root.parent
    return root


def _walk_hierarchy(root):
    yield root
    for child in tuple(getattr(root, "children", ())):
        yield from _walk_hierarchy(child)


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

    root = _root_object(selected)
    objects = list(_walk_hierarchy(root))
    meshes = [obj for obj in objects if getattr(obj, "type", None) == "MESH"]
    armatures = {id(obj): obj for obj in objects if getattr(obj, "type", None) == "ARMATURE"}

    # Artist meshes are often parented directly to an armature, but an Armature
    # modifier may also reference a rig outside the selected object's hierarchy.
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

    generated = is_generated(root)
    metrics = {
        "meshes": len(meshes),
        "armatures": len(armatures),
        "materials": len(material_ids),
        "animations": animation_count,
    }

    notes = []
    if generated:
        status = "READY"
        notes.append("Recognized Asset Assistant metadata.")
        notes.append("This asset is ready for the existing Asset Assistant workflow.")
    elif not meshes:
        status = "NEEDS_SETUP"
        notes.append("No mesh geometry was found in the selected hierarchy.")
        notes.append("Choose a mesh or the root object of an artist-created asset.")
    else:
        status = "REVIEW"
        notes.append("Artist-created asset detected; no Asset Assistant ownership was added.")
        if len(armatures) == 0:
            notes.append("No armature detected; this can still be a static asset.")
        elif len(armatures) == 1:
            notes.append("One armature detected; rig structure can be reviewed before adoption.")
        else:
            notes.append("Multiple armatures detected; choose the intended rig before adoption.")
        notes.append("Inspection is read-only. Adoption remains optional.")

    return {
        "root": root,
        "name": getattr(root, "name", "Selected Asset"),
        "status": status,
        "metrics": metrics,
        "notes": tuple(notes),
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


def _store_report(scene, report):
    scene[_STATUS_KEY] = report["status"]
    scene[_NAME_KEY] = report["name"]
    scene[_METRICS_KEY] = _metric_text(report["metrics"])
    scene[_SUMMARY_KEY] = "\n".join(report["notes"])


def draw_inspection_report(layout, scene):
    status = scene.get(_STATUS_KEY)
    if not status:
        return

    labels = {
        "READY": ("ASSET ASSISTANT READY", "CHECKMARK"),
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


class ASSET_ASSISTANT_OT_inspect_selected_asset(bpy.types.Operator):
    """Inspect selected geometry without claiming or modifying it."""

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
        _store_report(context.scene, report)
        self.report({"INFO"}, "Inspection complete. No changes were made.")
        return {"FINISHED"}


_CLASSES = (ASSET_ASSISTANT_OT_inspect_selected_asset,)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "inspect_selected_asset",
    "draw_inspection_report",
    "register",
    "unregister",
]
