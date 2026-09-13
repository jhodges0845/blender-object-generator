# SPDX-License-Identifier: GPL-3.0-or-later
"""Editable Asset Assistant working-state save and reopen workflow."""

from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .asset_structure import logical_asset
from .component_modify_exchange import enrich_snapshot
from .modification import inspect_generated_asset
from .workflow import is_external_asset, is_generated, is_managed_asset


_CHECKPOINT_KIND_KEY = "asset_assistant_working_state_kind"
_CHECKPOINT_VERSION_KEY = "asset_assistant_working_state_version"
_CHECKPOINT_STATUS_KEY = "asset_assistant_working_state_status"
_CHECKPOINT_MESSAGE_KEY = "asset_assistant_working_state_message"
_CHECKPOINT_KIND = "asset-assistant-editable-checkpoint"
_CHECKPOINT_VERSION = 1
_OPEN_EXPECTS_CHECKPOINT = False


def _checkpoint_destination(filepath):
    """Return normalized .blend path and its current filesystem existence.

    The file browser may keep operator properties between invocations, so checkpoint
    save must derive overwrite state from disk instead of trusting remembered UI state.
    """
    path = Path(filepath)
    if path.suffix.lower() != ".blend":
        path = path.with_suffix(".blend")
    return str(path), path.exists()


def _reset_checkpoint_save_dialog(operator, filepath):
    """Reset transient file-browser state for a fresh checkpoint save invocation."""
    normalized, exists = _checkpoint_destination(filepath)
    operator.filepath = normalized
    operator.check_existing = exists
    return normalized


def _restore_scene_value(scene, key, previous):
    existed, value = previous
    if existed:
        scene[key] = value
    elif key in scene:
        del scene[key]


def _validate_external_working_asset(root):
    """Validate adopted artist data without treating it as generated-provider state."""
    structure = logical_asset(root)
    if structure["root"] is not root:
        raise ValueError("Imported Asset Assistant target no longer resolves to its enrolled logical root.")
    if not structure["meshes"]:
        raise ValueError("Imported Asset Assistant target no longer contains mesh geometry.")
    if len(structure["rigs"]) > 1:
        raise ValueError("Imported Asset Assistant target now contains multiple base armatures.")

    capability = str(root.get("asset_assistant_external_capability", "STATIC"))
    if capability not in {"STATIC", "RIGGED", "ANIMATED"}:
        raise ValueError("Imported Asset Assistant target has invalid capability metadata.")
    if capability in {"RIGGED", "ANIMATED"} and len(structure["rigs"]) != 1:
        raise ValueError("Imported rigged Asset Assistant target is missing its base armature.")
    if capability == "ANIMATED" and structure["animation_count"] < 1:
        raise ValueError("Imported animated Asset Assistant target no longer exposes animation data.")

    return {
        "kind": "external",
        "root": root,
        "capability": capability,
        "meshes": len(structure["meshes"]),
        "rigs": len(structure["rigs"]),
        "animations": structure["animation_count"],
    }


def validate_working_state(scene):
    """Validate generated and explicitly adopted Asset Assistant state before editable save."""
    roots = tuple(obj for obj in scene.objects if is_managed_asset(obj))
    if not roots:
        raise ValueError("Editable checkpoint requires at least one recognizable Asset Assistant base asset.")

    snapshots = []
    for root in roots:
        if is_generated(root):
            # Generated assets retain strict provider, component, and animation
            # ownership validation before a checkpoint can be written.
            snapshots.append(enrich_snapshot(root, inspect_generated_asset(root)))
        elif is_external_asset(root):
            # Adopted artist assets have no generated provider contract. Validate
            # their normalized boundary/capability without claiming artist data.
            snapshots.append(_validate_external_working_asset(root))

    scene[_CHECKPOINT_STATUS_KEY] = "READY"
    scene[_CHECKPOINT_MESSAGE_KEY] = (
        str(len(snapshots)) + " Asset Assistant asset(s) validated for editable save."
    )
    return tuple(snapshots)


def save_editable_checkpoint(filepath, save_operator, scene=None):
    """Validate and write an editable Blender copy without changing the active working file."""
    filepath, _exists = _checkpoint_destination(filepath)
    path = Path(filepath)

    if scene is not None:
        validate_working_state(scene)

    previous_kind = previous_version = None
    if scene is not None:
        previous_kind = (_CHECKPOINT_KIND_KEY in scene, scene.get(_CHECKPOINT_KIND_KEY))
        previous_version = (_CHECKPOINT_VERSION_KEY in scene, scene.get(_CHECKPOINT_VERSION_KEY))
        scene[_CHECKPOINT_KIND_KEY] = _CHECKPOINT_KIND
        scene[_CHECKPOINT_VERSION_KEY] = _CHECKPOINT_VERSION

    try:
        result = save_operator(filepath=str(path), copy=True)
    finally:
        if scene is not None:
            _restore_scene_value(scene, _CHECKPOINT_KIND_KEY, previous_kind)
            _restore_scene_value(scene, _CHECKPOINT_VERSION_KEY, previous_version)

    if "FINISHED" not in result:
        raise RuntimeError("Blender did not finish saving the editable checkpoint.")
    return str(path)


def validate_checkpoint_scene(scene):
    """Validate one reopened Asset Assistant checkpoint and restore its selected target when safe."""
    if scene.get(_CHECKPOINT_KIND_KEY) != _CHECKPOINT_KIND:
        raise ValueError("This .blend file is not marked as an Asset Assistant editable checkpoint.")
    if scene.get(_CHECKPOINT_VERSION_KEY) != _CHECKPOINT_VERSION:
        raise ValueError("This Asset Assistant checkpoint version is not supported by this add-on build.")

    snapshots = validate_working_state(scene)
    roots = tuple(obj for obj in scene.objects if is_managed_asset(obj))

    settings = getattr(scene, "humanoid_settings", None)
    if settings is not None:
        target = getattr(settings, "target", None)
        if target not in roots:
            settings.target = roots[0] if len(roots) == 1 else None

    scene[_CHECKPOINT_STATUS_KEY] = "READY"
    scene[_CHECKPOINT_MESSAGE_KEY] = (
        str(len(snapshots)) + " Asset Assistant asset(s) restored and validated."
    )
    return tuple(snapshots)


def _record_checkpoint_error(scene, error):
    scene[_CHECKPOINT_STATUS_KEY] = "ERROR"
    scene[_CHECKPOINT_MESSAGE_KEY] = str(error)


@persistent
def _validate_reopened_checkpoint(_unused):
    """Validate any marked checkpoint after load, including native Blender File/Open."""
    global _OPEN_EXPECTS_CHECKPOINT
    expected = _OPEN_EXPECTS_CHECKPOINT
    _OPEN_EXPECTS_CHECKPOINT = False

    marked = tuple(
        scene for scene in bpy.data.scenes
        if scene.get(_CHECKPOINT_KIND_KEY) == _CHECKPOINT_KIND
    )
    if marked:
        for scene in marked:
            try:
                validate_checkpoint_scene(scene)
            except (ValueError, TypeError, RuntimeError, AttributeError) as error:
                _record_checkpoint_error(scene, error)
        return

    if expected:
        error = ValueError("This .blend file is not marked as an Asset Assistant editable checkpoint.")
        for scene in bpy.data.scenes:
            _record_checkpoint_error(scene, error)


def open_editable_checkpoint(filepath, open_operator):
    """Open a complete Blender checkpoint; Blender replaces the current file/session state."""
    path = Path(filepath)
    if path.suffix.lower() != ".blend":
        raise ValueError("Editable checkpoints must be Blender .blend files.")
    if not path.exists():
        raise ValueError("Editable checkpoint file does not exist: " + str(path))
    result = open_operator(filepath=str(path))
    if "FINISHED" not in result:
        raise RuntimeError("Blender did not finish opening the editable checkpoint.")
    return str(path)


class ASSET_ASSISTANT_OT_save_editable_checkpoint(bpy.types.Operator, ExportHelper):
    bl_idname = "asset_assistant.save_editable_checkpoint"
    bl_label = "Validate + Save Editable Checkpoint"
    bl_description = (
        "Validate Asset Assistant ownership/continuity, then save a complete editable .blend copy "
        "without changing the current working file"
    )
    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})
    # ExportHelper's overwrite flag is an operator property and can otherwise be
    # restored from a previous invocation. SKIP_SAVE makes each dialog start from
    # the current filesystem state instead of a remembered overwrite decision.
    check_existing: bpy.props.BoolProperty(
        name="Check Existing",
        default=True,
        options={"HIDDEN", "SKIP_SAVE"},
    )

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def check(self, _context):
        normalized, exists = _checkpoint_destination(self.filepath)
        changed = self.filepath != normalized or self.check_existing != exists
        self.filepath = normalized
        self.check_existing = exists
        return changed

    def invoke(self, context, event):
        current = Path(bpy.data.filepath).stem if bpy.data.filepath else "asset-assistant-working-asset"
        _reset_checkpoint_save_dialog(self, current + ".checkpoint.blend")
        for key in (_CHECKPOINT_STATUS_KEY, _CHECKPOINT_MESSAGE_KEY):
            if key in context.scene:
                del context.scene[key]
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        # Refresh one final time at execution so a file deleted while the dialog was
        # open does not leave a stale overwrite state behind.
        self.filepath, self.check_existing = _checkpoint_destination(self.filepath)
        try:
            filepath = save_editable_checkpoint(self.filepath, bpy.ops.wm.save_as_mainfile, context.scene)
        except (RuntimeError, OSError, ValueError, TypeError, AttributeError) as error:
            _record_checkpoint_error(context.scene, error)
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, "Validated and saved editable checkpoint: " + filepath)
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_open_editable_checkpoint(bpy.types.Operator, ImportHelper):
    bl_idname = "asset_assistant.open_editable_checkpoint"
    bl_label = "Open Editable Checkpoint"
    bl_description = "Open a saved Asset Assistant .blend checkpoint instead of generating a new base asset"
    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def execute(self, context):
        global _OPEN_EXPECTS_CHECKPOINT
        _OPEN_EXPECTS_CHECKPOINT = True
        try:
            open_editable_checkpoint(self.filepath, bpy.ops.wm.open_mainfile)
        except (RuntimeError, OSError, ValueError) as error:
            _OPEN_EXPECTS_CHECKPOINT = False
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return {"FINISHED"}


_CLASSES = (
    ASSET_ASSISTANT_OT_save_editable_checkpoint,
    ASSET_ASSISTANT_OT_open_editable_checkpoint,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    if _validate_reopened_checkpoint not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_validate_reopened_checkpoint)


def unregister():
    if _validate_reopened_checkpoint in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_validate_reopened_checkpoint)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "ASSET_ASSISTANT_OT_save_editable_checkpoint",
    "ASSET_ASSISTANT_OT_open_editable_checkpoint",
    "save_editable_checkpoint",
    "open_editable_checkpoint",
    "validate_checkpoint_scene",
    "validate_working_state",
    "register",
    "unregister",
]
