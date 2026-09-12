# SPDX-License-Identifier: GPL-3.0-or-later
"""Editable Asset Assistant working-state save and reopen workflow."""

from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .component_modify_exchange import enrich_snapshot
from .modification import inspect_generated_asset
from .workflow import is_generated


_CHECKPOINT_KIND_KEY = "asset_assistant_working_state_kind"
_CHECKPOINT_VERSION_KEY = "asset_assistant_working_state_version"
_CHECKPOINT_STATUS_KEY = "asset_assistant_working_state_status"
_CHECKPOINT_MESSAGE_KEY = "asset_assistant_working_state_message"
_CHECKPOINT_KIND = "asset-assistant-editable-checkpoint"
_CHECKPOINT_VERSION = 1
_OPEN_EXPECTS_CHECKPOINT = False


def _restore_scene_value(scene, key, previous):
    existed, value = previous
    if existed:
        scene[key] = value
    elif key in scene:
        del scene[key]


def save_editable_checkpoint(filepath, save_operator, scene=None):
    """Write an editable Blender copy without changing the active working file."""
    path = Path(filepath)
    if path.suffix.lower() != ".blend":
        path = path.with_suffix(".blend")

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

    roots = tuple(obj for obj in scene.objects if is_generated(obj))
    if not roots:
        raise ValueError("Editable checkpoint contains no recognizable Asset Assistant base assets.")

    snapshots = []
    for root in roots:
        snapshot = inspect_generated_asset(root)
        snapshots.append(enrich_snapshot(root, snapshot))

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

    # When the Asset Assistant Open operator explicitly promised a checkpoint,
    # keep the previous error behavior for an unmarked .blend. Native Blender
    # loads of ordinary files remain untouched.
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
    bl_label = "Save Editable Checkpoint"
    bl_description = (
        "Save a complete editable .blend copy without changing the current working file; "
        "game and print exports remain separate"
    )
    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def invoke(self, context, event):
        current = Path(bpy.data.filepath).stem if bpy.data.filepath else "asset-assistant-working-asset"
        self.filepath = current + ".checkpoint.blend"
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        try:
            filepath = save_editable_checkpoint(self.filepath, bpy.ops.wm.save_as_mainfile, context.scene)
        except (RuntimeError, OSError, ValueError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, "Editable checkpoint saved: " + filepath)
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
    "register",
    "unregister",
]
