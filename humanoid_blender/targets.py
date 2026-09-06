# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender output adapters; metadata and options are usable without bpy."""

from dataclasses import dataclass, replace
from math import isfinite
from pathlib import Path
from typing import Tuple

from .core import ValidationIssue, get_target, validate_for_target
from .validation import inspect_objects


@dataclass(frozen=True)
class ExportResult:
    success: bool
    filepath: str
    issues: Tuple[ValidationIssue, ...] = ()


def asset_objects(root):
    """Include the root and all descendants, never unrelated selected objects."""
    if root is None:
        return ()
    result = [root]
    for obj in result:
        result.extend(obj.children)
    return tuple(result)


def _export_gltf(options):
    import bpy
    return bpy.ops.export_scene.gltf(**options)


class BlenderOutputAdapter:
    target_key = None

    def validate(self, root, context):
        raise NotImplementedError

    def prepare(self, root, context):
        """Read-only preflight; required edits are left to the caller."""
        return self.validate(root, context)

    def export(self, root, context, filepath):
        raise NotImplementedError


class GodotAdapter(BlenderOutputAdapter):
    target_key = "GODOT"
    default_extension = ".glb"
    extensions = (".glb", ".gltf")

    def __init__(self, *, asset_use=None):
        self.profile = get_target(self.target_key)
        if asset_use is not None:
            if asset_use not in ("STATIC", "RIGGED", "ANIMATED"):
                raise ValueError("asset_use must be STATIC, RIGGED, or ANIMATED")
            self.profile = replace(self.profile, asset_use=asset_use,
                                   require_rig=asset_use != "STATIC",
                                   require_animation=asset_use == "ANIMATED")

    def export_options(self, filepath):
        path = Path(filepath)
        if not path.suffix:
            path = path.with_suffix(self.default_extension)
        if path.suffix.lower() not in self.extensions:
            raise ValueError("Godot export requires .glb or .gltf")
        path = path.with_suffix(path.suffix.lower()).resolve()
        return dict(filepath=str(path), check_existing=False,
                    export_format="GLB" if path.suffix.lower() == ".glb" else "GLTF_SEPARATE",
                    use_selection=True, export_yup=True, export_apply=False,
                    export_skins=True, export_animations=True, export_materials="EXPORT",
                    export_frame_range=False, export_force_sampling=True,
                    export_nla_strips=True, export_texcoords=True, export_normals=True)

    def validate(self, root, context):
        context.view_layer.update()
        objects = asset_objects(root)
        issues = []

        def add(code, status, message):
            issues.append(ValidationIssue(code, status, message))

        if context.mode != "OBJECT":
            add("blender_mode", "ERROR", "Switch to Object Mode before export.")
        for obj in objects:
            if obj.type not in ("EMPTY", "MESH", "ARMATURE"):
                add("export_type", "ERROR", obj.name + ": unsupported export object type " + obj.type)
            if obj.name not in context.view_layer.objects or not obj.visible_get() or obj.hide_select:
                add("export_scope", "ERROR", obj.name + ": must be visible and selectable in the active view layer.")
            matrix = obj.matrix_world
            if any(not isfinite(v) for row in matrix for v in row) or abs(matrix.determinant()) < 1e-12:
                add("export_transform", "ERROR", obj.name + ": non-finite or singular transform; repair before export.")
            elif matrix.determinant() < 0:
                add("export_transform", "WARN", obj.name + ": mirrored transform; review normals and skinning.")
            for modifier in obj.modifiers:
                if modifier.type == "ARMATURE" and modifier.object and modifier.object not in objects:
                    add("export_scope", "ERROR", obj.name + ": armature is outside the asset hierarchy.")
            animation = obj.animation_data
            if animation:
                for track in animation.nla_tracks:
                    strips = [strip for strip in track.strips if strip.action and not strip.mute]
                    if track.mute or track.is_solo or len(strips) > 1:
                        add("export_nla", "ERROR", obj.name + ": muted, solo, or multi-strip NLA tracks require manual preparation for glTF export.")
            if obj.constraints:
                add("export_constraints", "WARN", obj.name + ": constraints need exported playback review.")
        if context.scene.unit_settings.scale_length != 1.0:
            add("export_units", "ERROR", "Export currently requires scene unit scale 1.0; review asset dimensions before changing units. No automatic rescaling is performed.")
        try:
            issues[:0] = validate_for_target(inspect_objects(objects), self.profile)
        except (AttributeError, ValueError, RuntimeError) as exc:
            add("export_inspection", "ERROR", "Could not inspect this Blender asset: " + str(exc))
        return tuple(issues)

    def export(self, root, context, filepath):
        try:
            options = self.export_options(filepath)
        except (ValueError, TypeError) as exc:
            return ExportResult(False, str(filepath), (ValidationIssue("export_path", "ERROR", str(exc)),))
        path = Path(options["filepath"])
        issues = self.prepare(root, context)
        if any(issue.status == "ERROR" for issue in issues):
            return ExportResult(False, str(path), issues)
        if not path.parent.is_dir() or path.exists():
            return ExportResult(False, str(path), issues + (ValidationIssue(
                "export_path", "ERROR", "Choose a new output path in an existing directory."),))
        if path.suffix.lower() == ".gltf" and any(path.parent.iterdir()):
            return ExportResult(False, str(path), issues + (ValidationIssue(
                "export_path", "ERROR", "Use an empty directory for glTF and its texture/binary sidecars."),))
        selected = tuple(context.selected_objects)
        active = context.view_layer.objects.active
        frame, subframe = context.scene.frame_current, context.scene.frame_subframe
        success = False
        try:
            for obj in selected:
                obj.select_set(False)
            for obj in asset_objects(root):
                obj.select_set(True)
            context.view_layer.objects.active = root
            status = _export_gltf(options)
            success = "FINISHED" in status and path.is_file() and path.stat().st_size > 0
            if not success:
                issues += (ValidationIssue("export_failed", "ERROR", "glTF export did not produce a completed file."),)
        except Exception as exc:
            issues += (ValidationIssue("export_failed", "ERROR", str(exc) + "; check for partial output files before retrying."),)
        finally:
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in selected:
                obj.select_set(True)
            context.view_layer.objects.active = active
            context.scene.frame_set(frame, subframe=subframe)
        return ExportResult(success, str(path), issues)


ADAPTERS = {"GODOT": GodotAdapter}


def get_adapter(target_key, **options):
    target = get_target(target_key)
    if target.key not in ADAPTERS:
        raise ValueError("Blender adapter not implemented for target: " + target.key)
    return ADAPTERS[target.key](**options)
