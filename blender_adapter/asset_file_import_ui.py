# SPDX-License-Identifier: GPL-3.0-or-later
"""Preflight and import existing asset files without silently claiming ownership."""

from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper


_FILEPATH_KEY = "asset_assistant_file_preflight_path"
_STATUS_KEY = "asset_assistant_file_preflight_status"
_SUMMARY_KEY = "asset_assistant_file_preflight_summary"
_CANDIDATE_KEY = "asset_assistant_file_preflight_candidate"
_CANDIDATES_KEY = "asset_assistant_file_preflight_candidates"

_SUPPORTED_EXTENSIONS = {".blend", ".glb", ".gltf", ".fbx"}


def _blend_preflight(filepath):
    with bpy.data.libraries.load(filepath, link=False) as (data_from, _data_to):
        collections = tuple(name for name in data_from.collections if name)
        scenes = tuple(name for name in data_from.scenes if name)
        objects = tuple(name for name in data_from.objects if name)
        meshes = tuple(name for name in data_from.meshes if name)
        armatures = tuple(name for name in data_from.armatures if name)
        actions = tuple(name for name in data_from.actions if name)
        cameras = tuple(name for name in data_from.cameras if name)
        lights = tuple(name for name in data_from.lights if name)

    project_signals = len(scenes) > 1 or bool(cameras) or bool(lights)
    if len(collections) == 1 and not project_signals:
        status = "ASSET_CANDIDATE"
        candidate = collections[0]
        headline = "One reusable collection candidate found."
    elif len(collections) > 1:
        status = "MULTIPLE_CANDIDATES"
        candidate = ""
        headline = f"{len(collections)} collection candidates found; choose the asset you want to import."
    elif meshes or armatures:
        status = "ASSET_CANDIDATE"
        candidate = ""
        headline = "Reusable object data found without a collection wrapper."
    else:
        status = "PROJECT_LIKELY" if project_signals else "NO_ASSET_FOUND"
        candidate = ""
        headline = "No clear reusable asset candidate was found."

    notes = [
        headline,
        f"{len(objects)} objects  •  {len(meshes)} meshes  •  {len(armatures)} rigs  •  {len(actions)} actions",
    ]
    if project_signals:
        notes.append("Scene/camera/light content suggests this file may contain project-level content too.")
    notes.append("Nothing has been appended to the current Blender scene yet.")
    return {
        "status": status,
        "candidate": candidate,
        "candidates": collections,
        "notes": tuple(notes),
    }


def preflight_asset_file(filepath):
    """Inspect enough file metadata to decide whether importing is sensible."""
    path = Path(filepath)
    if not path.exists():
        raise ValueError("Asset file does not exist: " + str(path))
    extension = path.suffix.lower()
    if extension not in _SUPPORTED_EXTENSIONS:
        raise ValueError("Supported asset files are .blend, .glb, .gltf, and .fbx.")

    if extension == ".blend":
        report = _blend_preflight(str(path))
    else:
        report = {
            "status": "EXTERNAL_ASSET",
            "candidate": path.stem,
            "candidates": (),
            "notes": (
                extension[1:].upper() + " exchange asset detected.",
                "Mesh, rig, material, and animation structure will be inspected after import.",
                "Import does not add Asset Assistant ownership metadata.",
            ),
        }
    report["filepath"] = str(path)
    report["extension"] = extension
    return report


def _store_report(scene, report):
    scene[_FILEPATH_KEY] = report["filepath"]
    scene[_STATUS_KEY] = report["status"]
    scene[_CANDIDATE_KEY] = report.get("candidate", "")
    scene[_CANDIDATES_KEY] = "\n".join(report.get("candidates", ()))
    scene[_SUMMARY_KEY] = "\n".join(report["notes"])


def _stored_candidates(scene):
    return tuple(name for name in str(scene.get(_CANDIDATES_KEY, "")).splitlines() if name)


def choose_blend_candidate(scene, collection_name):
    """Select one inspected .blend collection without importing it yet."""
    candidates = _stored_candidates(scene)
    if not collection_name or collection_name not in candidates:
        raise ValueError("Choose one of the collection candidates found during file inspection.")
    scene[_CANDIDATE_KEY] = collection_name
    scene[_STATUS_KEY] = "ASSET_CANDIDATE"
    scene[_SUMMARY_KEY] = (
        "Selected collection: " + collection_name + "\n"
        "Ready to import this collection only.\n"
        "Nothing has been appended to the current Blender scene yet."
    )
    return collection_name


def _clear_selection(context):
    for obj in tuple(context.selected_objects):
        obj.select_set(False)


def _activate_imported_object(context, objects):
    roots = [obj for obj in objects if getattr(obj, "parent", None) not in objects]
    candidates = roots or list(objects)
    if not candidates:
        return None
    armatures = [obj for obj in candidates if getattr(obj, "type", None) == "ARMATURE"]
    meshes = [obj for obj in candidates if getattr(obj, "type", None) == "MESH"]
    active = armatures[0] if len(armatures) == 1 else (meshes[0] if meshes else candidates[0])
    _clear_selection(context)
    active.select_set(True)
    context.view_layer.objects.active = active
    return active


def _import_external(filepath, extension, context):
    before = set(bpy.data.objects)
    if extension in {".glb", ".gltf"}:
        result = bpy.ops.import_scene.gltf(filepath=filepath)
    elif extension == ".fbx":
        if hasattr(bpy.ops.wm, "fbx_import"):
            result = bpy.ops.wm.fbx_import(filepath=filepath)
        else:
            result = bpy.ops.import_scene.fbx(filepath=filepath)
    else:
        raise ValueError("Unsupported external asset format: " + extension)
    if "FINISHED" not in result:
        raise RuntimeError("Blender did not finish importing the selected asset.")
    imported = tuple(obj for obj in bpy.data.objects if obj not in before)
    if not imported:
        raise RuntimeError("The file imported without creating any Blender objects.")
    return _activate_imported_object(context, imported)


def _import_blend_collection(filepath, collection_name, context):
    if not collection_name:
        raise ValueError("Choose a collection asset candidate first.")
    with bpy.data.libraries.load(filepath, link=False) as (_data_from, data_to):
        data_to.collections = [collection_name]
    collection = data_to.collections[0] if data_to.collections else None
    if collection is None:
        raise RuntimeError("Blender could not append the selected collection.")
    context.scene.collection.children.link(collection)
    return _activate_imported_object(context, tuple(collection.all_objects))


def import_preflight_asset(scene, context):
    filepath = str(scene.get(_FILEPATH_KEY, ""))
    status = str(scene.get(_STATUS_KEY, ""))
    candidate = str(scene.get(_CANDIDATE_KEY, ""))
    if not filepath or not status:
        raise ValueError("Inspect an asset file first.")
    extension = Path(filepath).suffix.lower()
    if extension == ".blend":
        if status != "ASSET_CANDIDATE" or not candidate:
            raise ValueError("Choose a specific .blend collection before importing.")
        return _import_blend_collection(filepath, candidate, context)
    if status != "EXTERNAL_ASSET":
        raise ValueError("This file is not ready to import as an asset.")
    return _import_external(filepath, extension, context)


def draw_file_preflight_report(layout, scene):
    status = scene.get(_STATUS_KEY)
    if not status:
        return
    labels = {
        "ASSET_CANDIDATE": ("ASSET CANDIDATE", "CHECKMARK"),
        "EXTERNAL_ASSET": ("EXTERNAL ASSET", "CHECKMARK"),
        "MULTIPLE_CANDIDATES": ("CHOOSE AN ASSET", "INFO"),
        "PROJECT_LIKELY": ("LIKELY BLENDER PROJECT", "INFO"),
        "NO_ASSET_FOUND": ("NO CLEAR ASSET FOUND", "ERROR"),
    }
    title, icon = labels.get(status, ("FILE INSPECTION", "INFO"))
    box = layout.box()
    box.label(text=title, icon=icon)
    filepath = scene.get(_FILEPATH_KEY, "")
    if filepath:
        box.label(text=Path(filepath).name)
    for line in str(scene.get(_SUMMARY_KEY, "")).splitlines():
        box.label(text=line)

    if status == "MULTIPLE_CANDIDATES":
        candidates = _stored_candidates(scene)
        if candidates:
            box.separator(factor=0.35)
            box.label(text="COLLECTIONS", icon="OUTLINER_COLLECTION")
            for name in candidates:
                row = box.row()
                row.scale_y = 1.15
                op = row.operator(
                    "asset_assistant.choose_blend_candidate",
                    text=name,
                    icon="OUTLINER_COLLECTION",
                )
                op.collection_name = name
        return

    can_import = (
        status == "EXTERNAL_ASSET"
        or (status == "ASSET_CANDIDATE" and bool(scene.get(_CANDIDATE_KEY, "")))
    )
    row = box.row()
    row.scale_y = 1.25
    row.enabled = can_import
    row.operator("asset_assistant.import_preflight_asset", text="Import This Asset", icon="IMPORT")
    if status == "ASSET_CANDIDATE" and not can_import:
        box.label(text="This file has reusable data but no collection wrapper to append safely.")
    elif not can_import:
        box.label(text="No importable asset candidate is available yet.")


class ASSET_ASSISTANT_OT_preflight_asset_file(bpy.types.Operator, ImportHelper):
    bl_idname = "asset_assistant.preflight_asset_file"
    bl_label = "Inspect Asset File"
    bl_description = "Inspect a .blend, GLB, glTF, or FBX file before bringing it into this scene"
    filename_ext = ""
    filter_glob: bpy.props.StringProperty(
        default="*.blend;*.glb;*.gltf;*.fbx",
        options={"HIDDEN"},
    )

    def execute(self, context):
        try:
            report = preflight_asset_file(self.filepath)
        except (ValueError, RuntimeError, OSError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        _store_report(context.scene, report)
        self.report({"INFO"}, "File inspected. Nothing was imported yet.")
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_choose_blend_candidate(bpy.types.Operator):
    bl_idname = "asset_assistant.choose_blend_candidate"
    bl_label = "Choose Asset Collection"
    bl_description = "Choose this collection as the asset to import; nothing is imported yet"

    collection_name: bpy.props.StringProperty(name="Collection")

    def execute(self, context):
        try:
            choose_blend_candidate(context.scene, self.collection_name)
        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, "Asset collection selected. Review it, then import when ready.")
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_import_preflight_asset(bpy.types.Operator):
    bl_idname = "asset_assistant.import_preflight_asset"
    bl_label = "Import This Asset"
    bl_description = "Import the inspected candidate without adding Asset Assistant ownership metadata"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def execute(self, context):
        try:
            active = import_preflight_asset(context.scene, context)
        except (ValueError, RuntimeError, OSError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        if active is not None:
            try:
                from .asset_inspection_ui import inspect_selected_asset, _store_report
                _store_report(context.scene, inspect_selected_asset(active))
            except (ValueError, TypeError, AttributeError):
                pass
        self.report({"INFO"}, "Asset imported. No Asset Assistant ownership was added.")
        return {"FINISHED"}


_CLASSES = (
    ASSET_ASSISTANT_OT_preflight_asset_file,
    ASSET_ASSISTANT_OT_choose_blend_candidate,
    ASSET_ASSISTANT_OT_import_preflight_asset,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "preflight_asset_file",
    "choose_blend_candidate",
    "import_preflight_asset",
    "draw_file_preflight_report",
    "register",
    "unregister",
]
