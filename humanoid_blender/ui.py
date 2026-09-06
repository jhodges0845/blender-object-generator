# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender generation, preparation, validation and file export workflow."""

import textwrap
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, PointerProperty, StringProperty

from .adapter import create_character
from .core import OBJECT_TYPES, get_provider, ValidationIssue
from .workflow import add_basic_rig, find_character, is_generated, provider_for
from .animation import add_idle
from .targets import get_adapter, is_ready
from .materials import prepare_materials


def _clear_report(settings, context):
    settings.validation_results.clear()
    settings.last_export = ""


def _character_poll(settings, obj):
    return is_generated(obj)


def _character(context):
    root = context.scene.humanoid_settings.target or find_character(context.object)
    return root if root and context.scene.objects.get(root.name) == root else None


def _select(context, obj):
    for selected in context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


class HUMANOID_PG_result(bpy.types.PropertyGroup):
    code: StringProperty()
    status: StringProperty()
    message: StringProperty()


class HUMANOID_PG_settings(bpy.types.PropertyGroup):
    # Retained for saved files/scripts; visible navigation uses sidebar categories.
    workflow_tab: EnumProperty(name="Stage", default="MODEL", items=[
        ("MODEL", "Model", "Create a model"),
        ("RIGGING", "Rigging", "Rig an existing character"),
        ("ANIMATION", "Animation", "Animation workflow status"),
        ("VALIDATION", "Validation", "Check the selected character"),
        ("EXPORT", "Export", "Prepare and export a file for the selected application"),
    ])
    output_target: EnumProperty(name="Export To", default="GODOT", update=_clear_report, items=[
        ("GODOT", "Godot (.glb)", "Meshes, materials, rig and animation in GLB"),
        ("UNITY", "Unity (.fbx)", "Meshes, materials, rig and animation in FBX"),
        ("UNREAL", "Unreal Engine (.fbx)", "Meshes, materials, rig and animation in FBX"),
        ("CURA", "Cura (.stl)", "Current pose as a closed solid in millimetres"),
    ])
    last_export: StringProperty()
    target: PointerProperty(name="Object", type=bpy.types.Object, poll=_character_poll, update=_clear_report)
    object_type: EnumProperty(name="Object Type", default="humanoid", items=[
        (p.key, p.label, "Generate " + p.label) for p in OBJECT_TYPES.values()
    ])
    asset_use: EnumProperty(name="Validate For", default="RIGGED", update=_clear_report, items=[
        ("STATIC", "Static Asset", "No skeleton or animation required"),
        ("RIGGED", "Rigged Asset", "Require a skeleton and weights"),
        ("ANIMATED", "Animated Asset", "Also require a keyed animation clip"),
    ])
    require_textures: BoolProperty(name="Image Textures Expected", default=False, update=_clear_report,
                                   description="Require image textures and UV maps; leave off for material-only assets")
    validation_results: CollectionProperty(type=HUMANOID_PG_result)
    idle_duration: FloatProperty(name="Cycle (seconds)", default=4, min=1, max=20)
    idle_strength: FloatProperty(name="Motion Strength", default=1, min=0.1, max=2)
    idle_set_range: BoolProperty(name="Set Playback Range", default=True)


def _field_name(provider, field):
    # Preserve saved humanoid settings from earlier add-on versions.
    return field.key if provider.key == 'humanoid' else provider.key + '_' + field.key


for _provider in OBJECT_TYPES.values():
    for _field in _provider.parameters:
        _property = (EnumProperty(name=_field.label, default=_field.default,
                                 items=[(key, label, label) for key, label in _field.choices])
                     if _field.choices else FloatProperty(name=_field.label, default=_field.default,
                                                         min=_field.minimum, max=_field.maximum))
        HUMANOID_PG_settings.__annotations__[_field_name(_provider, _field)] = _property


class HUMANOID_OT_generate(bpy.types.Operator):
    bl_idname = "humanoid.generate_blockout"
    bl_label = "Generate Model"
    bl_description = "Create a new editable blockout at the 3D cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def execute(self, context):
        settings = context.scene.humanoid_settings
        try:
            provider = get_provider(settings.object_type)
            values = {field.key: getattr(settings, _field_name(provider, field)) for field in provider.parameters}
            root = create_character(provider.mesh(values), name=provider.label, scene=context.scene)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        root["object_type"] = settings.object_type
        for key, value in values.items():
            root[key] = value
        root.location = context.scene.cursor.location
        settings.target = root
        settings.asset_use = 'RIGGED' if provider.supports_rig else 'STATIC'
        _select(context, root)
        for obj in root.children:
            obj.select_set(True)
        self.report({"INFO"}, "Model created. " + ('Open Rigging to add its skeleton.' if provider.supports_rig else 'Open Validation to check this static asset.'))
        return {"FINISHED"}


class HUMANOID_OT_rig(bpy.types.Operator):
    bl_idname = "humanoid.add_basic_rig"
    bl_label = "Add Basic Rig"
    bl_description = "Rig this character using its saved generation dimensions"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        try:
            rig = add_basic_rig(_character(context), context)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        context.scene.humanoid_settings.validation_results.clear()
        _select(context, rig)
        self.report({"INFO"}, "Rig added to the existing model.")
        return {"FINISHED"}


class HUMANOID_OT_pose(bpy.types.Operator):
    bl_idname = "humanoid.enter_pose_mode"
    bl_label = "Enter Pose Mode"

    @classmethod
    def poll(cls, context):
        root = _character(context) if context.scene else None
        return context.mode == "OBJECT" and root is not None and any(o.type == "ARMATURE" for o in root.children)

    def execute(self, context):
        rig = next(o for o in _character(context).children if o.type == "ARMATURE")
        _select(context, rig)
        bpy.ops.object.mode_set(mode="POSE")
        return {"FINISHED"}


class HUMANOID_OT_idle(bpy.types.Operator):
    bl_idname = "humanoid.generate_idle"
    bl_label = "Generate Idle"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        settings = context.scene.humanoid_settings
        try:
            action, end = add_idle(_character(context), context.scene, settings.idle_duration, settings.idle_strength)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        if settings.idle_set_range:
            context.scene.frame_end = end
            context.scene.use_preview_range = False
        context.scene.frame_set(context.scene.frame_start)
        settings.validation_results.clear()
        self.report({"INFO"}, "Idle created. Press Play to preview.")
        return {"FINISHED"}


class HUMANOID_OT_preview(bpy.types.Operator):
    bl_idname = 'humanoid.preview_idle'
    bl_label = 'Preview Motion Pose'
    bl_description = 'Show the middle of the active clip with the rig in Pose Position'

    @classmethod
    def poll(cls, context):
        root = _character(context) if context.scene else None
        return root is not None and any(o.type == 'ARMATURE' and o.animation_data and
                                       o.animation_data.action for o in root.children)

    def execute(self, context):
        rig = next(o for o in _character(context).children if o.type == 'ARMATURE' and
                   o.animation_data and o.animation_data.action)
        rig.data.pose_position = 'POSE'
        start, end = rig.animation_data.action.frame_range
        frame = (start + end) / 2
        context.scene.frame_set(int(frame), subframe=frame - int(frame))
        return {'FINISHED'}


class HUMANOID_OT_validate(bpy.types.Operator):
    bl_idname = "humanoid.validate_character"
    bl_label = "Run Validation"
    bl_description = "Inspect the current character without changing its meshes or materials"

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _character(context) is not None

    def execute(self, context):
        settings = context.scene.humanoid_settings
        settings.validation_results.clear()
        results = _export_issues(context)
        for issue in results:
            row = settings.validation_results.add()
            row.code, row.status, row.message = issue.code, issue.status, issue.message
        self.report({"INFO"}, "Validation snapshot updated; review the results below.")
        return {"FINISHED"}


def _output_adapter(context):
    settings = context.scene.humanoid_settings
    return get_adapter(settings.output_target, asset_use=settings.asset_use,
                       require_textures=settings.require_textures if settings.output_target != 'CURA' else False)


def _export_issues(context):
    try:
        return _output_adapter(context).prepare(_character(context), context)
    except (ValueError, TypeError, RuntimeError, AttributeError) as error:
        return (ValidationIssue('preparation', 'ERROR', str(error)),)


class HUMANOID_OT_prepare_materials(bpy.types.Operator):
    bl_idname = 'humanoid.prepare_materials'
    bl_label = 'Add Missing Materials'
    bl_description = 'Assign a neutral exportable material only to faces without one; keep existing materials'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == 'OBJECT' and _character(context) is not None

    def execute(self, context):
        prepare_materials(_character(context))
        context.scene.humanoid_settings.validation_results.clear()
        self.report({'INFO'}, 'Missing material assignments filled. Existing materials preserved.')
        return {'FINISHED'}


class HUMANOID_OT_export(bpy.types.Operator, ExportHelper):
    bl_idname = 'humanoid.export_asset'
    bl_label = 'Export Asset'
    bl_description = 'Export the selected model after checking all requirements again'
    filename_ext = ''
    filter_glob: StringProperty(default='*.glb', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if context.scene is None or context.mode != 'OBJECT' or _character(context) is None:
            return False
        # Never trust a stored report after the artist edits the scene.
        return is_ready(_export_issues(context))

    def invoke(self, context, event):
        adapter = _output_adapter(context)
        self.filter_glob = ';'.join('*' + extension for extension in adapter.extensions)
        self.filepath = _character(context).name + adapter.default_extension
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        result = _output_adapter(context).export(_character(context), context, bpy.path.abspath(self.filepath))
        settings = context.scene.humanoid_settings
        settings.validation_results.clear()
        for issue in result.issues:
            row = settings.validation_results.add()
            row.code, row.status, row.message = issue.code, issue.status, issue.message
        if not result.success:
            settings.last_export = ''
            message = next((issue.message for issue in result.issues if issue.status in ('ERROR', 'WARN')), 'Export failed.')
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
        settings.last_export = result.filepath
        self.report({'INFO'}, 'Exported: ' + result.filepath)
        return {'FINISHED'}


def _needs_attention(context, stage):
    codes = {
        'MODEL': {'geometry', 'target_geometry', 'cura_solid', 'export_transform', 'export_units', 'export_modifier'},
        'RIGGING': {'rig', 'target_rig'},
        'ANIMATION': {'animation', 'target_animation', 'export_nla', 'fbx_animation_range', 'export_constraints'},
    }.get(stage)
    return any(issue.status in ('ERROR', 'WARN') and (codes is None or issue.code in codes)
               for issue in _export_issues(context))


class _WorkflowPanel:
    """Shared stage layout; each registered panel owns a fixed sidebar category."""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    stage = "MODEL"

    def draw_header(self, context):
        attention = _needs_attention(context, self.stage)
        self.layout.label(text='', icon='ERROR' if attention else 'CHECKMARK')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.humanoid_settings
        if context.mode != "OBJECT":
            layout.operator("object.mode_set", text="Return to Object Mode").mode = "OBJECT"
        stage = self.stage
        if stage == "MODEL":
            layout.prop(settings, "object_type")
            for field in get_provider(settings.object_type).parameters:
                layout.prop(settings, _field_name(get_provider(settings.object_type), field))
            layout.operator("humanoid.generate_blockout", icon="OUTLINER_OB_MESH")
            layout.label(text="Creates a new model each time.")
            return
        layout.prop(settings, "target")
        root = _character(context)
        if root is None:
            layout.label(text="Create or choose a character first.")
            return
        has_rig = any(obj.type == "ARMATURE" for obj in root.children)
        try:
            provider = provider_for(root)
        except ValueError as error:
            layout.label(text=str(error))
            return
        if stage in ('RIGGING', 'ANIMATION') and not getattr(provider, 'supports_rig' if stage == 'RIGGING' else 'supports_idle'):
            layout.label(text=provider.label + ' is a static object.')
            layout.label(text='Use Validation for static asset checks.')
            return
        if stage == "RIGGING":
            if has_rig:
                layout.label(text="Rig found; existing rig preserved.")
                layout.operator("humanoid.enter_pose_mode")
                layout.label(text="In Pose Mode: R rotates a bone.")
                layout.label(text="Alt-R clears its rotation.")
            else:
                layout.operator("humanoid.add_basic_rig", icon="ARMATURE_DATA")
                layout.label(text="Uses saved generation dimensions.")
            layout.label(text="Rigid parts; no smooth joints yet.")
        elif stage == "ANIMATION":
            if not has_rig:
                layout.label(text="Add a rig before animating.")
            else:
                layout.prop(settings, "idle_duration")
                layout.prop(settings, "idle_strength")
                layout.prop(settings, "idle_set_range")
                layout.operator("humanoid.generate_idle")
                layout.operator("humanoid.preview_idle")
                layout.operator("screen.animation_play", text="Play / Pause", icon="PLAY")
                layout.label(text='Preview shows motion without playback.')
                layout.label(text="Requires a fresh rig in rest pose.")
                layout.label(text="Existing animation is preserved.")
        else:
            layout.prop(settings, "output_target")
            if settings.output_target == 'CURA':
                layout.label(text='STL: current pose, millimetres, one solid.')
            else:
                layout.prop(settings, "asset_use")
                layout.prop(settings, "require_textures")
                if stage == 'VALIDATION':
                    layout.operator("humanoid.prepare_materials", icon="MATERIAL")
            if stage == 'VALIDATION':
                layout.operator("humanoid.validate_character", icon="CHECKMARK")
            rows = _export_issues(context) if stage == 'EXPORT' else settings.validation_results
            if stage == 'EXPORT':
                ready = is_ready(rows)
                layout.label(text='Ready to export.' if ready else 'Needs attention: see Validation.',
                             icon='CHECKMARK' if ready else 'ERROR')
                row = layout.row()
                row.enabled = ready
                row.operator('humanoid.export_asset', icon='EXPORT')
                if settings.last_export:
                    layout.label(text='Saved: ' + settings.last_export)
                return

            if rows:
                errors = sum(row.status == "ERROR" for row in rows)
                warnings = sum(row.status == "WARN" for row in rows)
                layout.label(text=f"{errors} errors, {warnings} warnings")
                if stage != 'EXPORT':
                    layout.label(text="Snapshot: rerun after editing.")
                width = max(24, int(context.region.width / 7) - 6)
                for row in rows:
                    box = layout.box()
                    box.label(text=row.status + ": " + row.code.replace("_", " ").title(),
                              icon={"ERROR": "ERROR", "WARN": "INFO", "PASS": "CHECKMARK", "INFO": "INFO"}[row.status])
                    for line in textwrap.wrap(row.message, width):
                        box.label(text=line)


class HUMANOID_PT_panel(_WorkflowPanel, bpy.types.Panel):
    bl_label = "Object Generator"
    bl_idname = "HUMANOID_PT_panel"
    bl_category = "Generator"
    stage = "MODEL"


class HUMANOID_PT_rigging(_WorkflowPanel, bpy.types.Panel):
    bl_label = "Rigging"
    bl_idname = "HUMANOID_PT_rigging"
    bl_category = "Rigging"
    stage = "RIGGING"


class HUMANOID_PT_animations(_WorkflowPanel, bpy.types.Panel):
    bl_label = "Animations"
    bl_idname = "HUMANOID_PT_animations"
    bl_category = "Animations"
    stage = "ANIMATION"


class HUMANOID_PT_validation(_WorkflowPanel, bpy.types.Panel):
    bl_label = "Validation"
    bl_idname = "HUMANOID_PT_validation"
    bl_category = "Validation"
    stage = "VALIDATION"


class HUMANOID_PT_export(_WorkflowPanel, bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "HUMANOID_PT_export"
    bl_category = "Export"
    stage = "EXPORT"


_CLASSES = (HUMANOID_PG_result, HUMANOID_PG_settings, HUMANOID_OT_generate,
            HUMANOID_OT_rig, HUMANOID_OT_pose, HUMANOID_OT_idle, HUMANOID_OT_preview, HUMANOID_OT_validate,
            HUMANOID_OT_prepare_materials, HUMANOID_OT_export, HUMANOID_PT_panel,
            HUMANOID_PT_rigging, HUMANOID_PT_animations, HUMANOID_PT_validation, HUMANOID_PT_export)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.humanoid_settings = PointerProperty(type=HUMANOID_PG_settings)


def unregister():
    del bpy.types.Scene.humanoid_settings
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
