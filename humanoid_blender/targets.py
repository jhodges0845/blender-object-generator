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
    options = dict(options)
    # Blender 2.92 scopes selected objects without this newer scene option.
    if 'use_active_scene' not in bpy.ops.export_scene.gltf.get_rna_type().properties:
        options.pop('use_active_scene', None)
    return bpy.ops.export_scene.gltf(**options)


def is_ready(issues):
    """Only completed checks with no unresolved problems can enable Export."""
    return bool(issues) and not any(issue.status in ('ERROR', 'WARN') for issue in issues)


class BlenderOutputAdapter:
    target_key = None
    extensions = ()
    operator_name = None

    def __init__(self, *, asset_use=None, require_textures=False):
        self.profile = get_target(self.target_key)
        self.profile = replace(self.profile, require_textures=require_textures) if require_textures else self.profile
        if not self.profile.supports_rig:
            asset_use = "STATIC"
        if asset_use is not None:
            if asset_use not in ("STATIC", "RIGGED", "ANIMATED"):
                raise ValueError("asset_use must be STATIC, RIGGED, or ANIMATED")
            self.profile = replace(self.profile, asset_use=asset_use,
                                   require_rig=asset_use != "STATIC",
                                   require_animation=asset_use == "ANIMATED")

    def prepare(self, root, context):
        """Read-only checks; scene edits use explicit undoable UI operators."""
        return self.validate(root, context)

    def output_path(self, filepath):
        path = Path(filepath)
        if not path.suffix:
            path = path.with_suffix(self.default_extension)
        if path.suffix.lower() not in self.extensions:
            raise ValueError(self.profile.display_name + " export requires " + " or ".join(self.extensions))
        return path.with_suffix(path.suffix.lower()).resolve()

    def export_options(self, filepath):
        raise NotImplementedError

    def write(self, options, root, context):
        raise NotImplementedError

    def inspect(self, objects, context):
        return inspect_objects(objects)

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
            if self.target_key == "CURA":
                continue
            for modifier in obj.modifiers:
                if modifier.type != 'ARMATURE' and modifier.show_viewport:
                    add('export_modifier', 'ERROR', obj.name + ': apply non-armature modifiers on an export copy before export.')
                if modifier.type == "ARMATURE" and modifier.object and modifier.object not in objects:
                    add("export_scope", "ERROR", obj.name + ": armature is outside the asset hierarchy.")
            animation = obj.animation_data
            if animation:
                for track in animation.nla_tracks:
                    strips = [strip for strip in track.strips if strip.action and not strip.mute]
                    if track.mute or track.is_solo or len(strips) > 1:
                        add("export_nla", "ERROR", obj.name + ": muted, solo, or multi-strip NLA tracks require manual preparation for export.")
            if obj.constraints:
                add("export_constraints", "WARN", obj.name + ": constraints need exported playback review.")
        if self.target_key == "GODOT" and context.scene.unit_settings.scale_length != 1.0:
            add("export_units", "ERROR", "Export currently requires scene unit scale 1.0; review asset dimensions before changing units. No automatic rescaling is performed.")
        try:
            issues[:0] = validate_for_target(self.inspect(objects, context), self.profile)
        except (AttributeError, ValueError, RuntimeError) as exc:
            add("export_inspection", "ERROR", "Could not inspect this Blender asset: " + str(exc))
        if self.target_key != 'CURA':
            from .materials import material_issues
            issues.extend(material_issues(objects))
        if self.operator_name:
            import bpy
            try:
                getattr(bpy.ops.export_scene, self.operator_name).get_rna_type()
            except (AttributeError, RuntimeError):
                add("exporter", "ERROR", "Enable Blender's " + self.operator_name + " exporter add-on.")
        return tuple(issues)

    def export(self, root, context, filepath):
        try:
            options = self.export_options(filepath)
        except (ValueError, TypeError, OSError) as exc:
            return ExportResult(False, str(filepath), (ValidationIssue("export_path", "ERROR", str(exc)),))
        path = Path(options["filepath"])
        issues = self.prepare(root, context)
        if not is_ready(issues):
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
            status = self.write(options, root, context)
            success = "FINISHED" in status and path.is_file() and path.stat().st_size > 0
            if not success:
                issues += (ValidationIssue("export_failed", "ERROR", "Export did not produce a completed file."),)
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


class GodotAdapter(BlenderOutputAdapter):
    target_key = "GODOT"
    default_extension = ".glb"
    extensions = (".glb", ".gltf")
    operator_name = "gltf"

    def export_options(self, filepath):
        path = self.output_path(filepath)
        return dict(filepath=str(path), check_existing=False,
                    export_format="GLB" if path.suffix == ".glb" else "GLTF_SEPARATE",
                    use_selection=True, use_active_scene=True, export_yup=True, export_apply=False,
                    export_skins=True, export_animations=True, export_materials="EXPORT",
                    export_frame_range=False, export_force_sampling=True,
                    export_nla_strips=True, export_texcoords=True, export_normals=True)

    def write(self, options, root, context):
        return _export_gltf(options)


class FBXAdapter(BlenderOutputAdapter):
    default_extension = ".fbx"
    extensions = (".fbx",)
    operator_name = "fbx"
    axis_forward = '-Z'
    axis_up = 'Y'

    def export_options(self, filepath):
        return dict(filepath=str(self.output_path(filepath)), check_existing=False,
                    use_selection=True, object_types={'EMPTY', 'MESH', 'ARMATURE'},
                    axis_forward=self.axis_forward, axis_up=self.axis_up,
                    apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                    use_mesh_modifiers=False, add_leaf_bones=False,
                    bake_anim=True, bake_anim_use_all_actions=False,
                    bake_anim_use_nla_strips=False, bake_anim_use_all_bones=True,
                    bake_anim_simplify_factor=0.0, path_mode='COPY', embed_textures=True)

    def validate(self, root, context):
        issues = list(super().validate(root, context))
        # Blender FBX cannot embed unsaved generated/packed-only images reliably.
        import bpy
        from .validation import _image_nodes
        for obj in asset_objects(root):
            animation = obj.animation_data
            if animation and animation.action:
                start, end = animation.action.frame_range
                if end < context.scene.frame_start or start > context.scene.frame_end:
                    issues.append(ValidationIssue('fbx_animation_range', 'ERROR', obj.name +
                        ': active action is outside the playback range. Set the range to the clip before export.'))
            for slot in obj.material_slots:
                material = slot.material
                if material is None:
                    continue
                for node in _image_nodes(material.node_tree if material.use_nodes else None):
                    image = node.image
                    if image and (image.source != 'FILE' or not image.filepath or
                                  not Path(bpy.path.abspath(image.filepath, library=image.library)).is_file()):
                        issues.append(ValidationIssue('fbx_texture', 'ERROR', image.name +
                            ': save this texture as a PNG/JPEG file before FBX export.'))
        return tuple(issues)

    def write(self, options, root, context):
        import bpy
        return bpy.ops.export_scene.fbx(**options)


class UnityAdapter(FBXAdapter):
    target_key = 'UNITY'


class UnrealAdapter(FBXAdapter):
    target_key = 'UNREAL'
    axis_forward = '-Y'
    axis_up = 'Z'


class CuraAdapter(BlenderOutputAdapter):
    target_key = 'CURA'
    default_extension = '.stl'
    extensions = ('.stl',)

    def export_options(self, filepath):
        return dict(filepath=str(self.output_path(filepath)))

    def inspect(self, objects, context):
        from .printing import print_geometry
        snapshot, _, _ = print_geometry(objects, context)
        return snapshot

    def validate(self, root, context):
        from .printing import print_geometry
        issues = list(super().validate(root, context))
        _, components, _ = print_geometry(asset_objects(root), context)
        if components > 1:
            issues.append(ValidationIssue('cura_solid', 'ERROR',
                'Cura export requires one connected solid. Join/remesh a copy of the parts and bridge gaps before validation. Joining objects alone does not connect their surfaces.'))
        else:
            issues.append(ValidationIssue('cura_pose', 'INFO',
                'STL uses the evaluated current pose in millimetres; materials, rigs and animation are not needed. Check printer fit, wall thickness and supports in Cura.'))
        return tuple(issues)

    def write(self, options, root, context):
        from .printing import print_geometry, write_stl
        _, _, triangles = print_geometry(asset_objects(root), context)
        return write_stl(options['filepath'], triangles, context.scene.unit_settings.scale_length)


ADAPTERS = {'GODOT': GodotAdapter, 'UNITY': UnityAdapter, 'UNREAL': UnrealAdapter, 'CURA': CuraAdapter}


def get_adapter(target_key, **options):
    target = get_target(target_key)
    if target.key not in ADAPTERS:
        raise ValueError("Blender adapter not implemented for target: " + target.key)
    return ADAPTERS[target.key](**options)
