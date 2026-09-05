"""Blender sidebar and operator. Generation is delegated to the core."""

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, PointerProperty

from .adapter import create_character
from .core import (BodyType, HumanoidSpec, generate_mesh, generate_proportions, generate_skeleton,
                   MIN_HEIGHT_CM, MAX_HEIGHT_CM, MIN_WEIGHT_KG, MAX_WEIGHT_KG)


class HUMANOID_PG_settings(bpy.types.PropertyGroup):
    object_type: EnumProperty(
        name="Object Type", default="humanoid",
        items=[("humanoid", "Humanoid", "Generate a stylized humanoid blockout")],
    )
    add_rig: BoolProperty(name="Basic Rig", default=True,
                          description="Make separate parts poseable with rigid bone weights")
    height_cm: FloatProperty(name="Height (cm)", default=180,
                             min=MIN_HEIGHT_CM, max=MAX_HEIGHT_CM, precision=1)
    weight_kg: FloatProperty(name="Weight (kg)", default=95,
                             min=MIN_WEIGHT_KG, max=MAX_WEIGHT_KG, precision=1)
    body_type: EnumProperty(name="Body Type", default="average",
                            items=[(kind.value, kind.value.title(), "Artistic shape preset")
                                   for kind in BodyType])


class HUMANOID_OT_generate(bpy.types.Operator):
    bl_idname = "humanoid.generate_blockout"
    bl_label = "Generate Blockout"
    bl_description = "Create a new editable humanoid blockout at the 3D cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def execute(self, context):
        settings = context.scene.humanoid_settings
        if settings.object_type != "humanoid":
            self.report({"ERROR"}, "This object type does not have a generator yet")
            return {"CANCELLED"}
        try:
            spec = HumanoidSpec(settings.height_cm, settings.weight_kg, BodyType(settings.body_type))
            proportions = generate_proportions(spec)
            mesh = generate_mesh(proportions)
            skeleton = generate_skeleton(proportions) if settings.add_rig else None
            root = create_character(mesh, scene=context.scene, skeleton=skeleton)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        root["object_type"] = settings.object_type
        root["height_cm"] = spec.height_cm
        root["weight_kg"] = spec.weight_kg
        root["body_type"] = spec.body_type.value
        root.location = context.scene.cursor.location
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in root.children:
            obj.select_set(True)
        root.select_set(True)
        armature = next((obj for obj in root.children if obj.type == "ARMATURE"), None)
        context.view_layer.objects.active = armature or root
        self.report({"INFO"}, "Created poseable blockout" if armature else "Created 15 editable blockout parts")
        return {"FINISHED"}


class HUMANOID_PT_panel(bpy.types.Panel):
    bl_label = "Object Generator"
    bl_idname = "HUMANOID_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Generator"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.humanoid_settings
        layout.prop(settings, "object_type")
        if settings.object_type == "humanoid":
            layout.prop(settings, "height_cm")
            layout.prop(settings, "weight_kg")
            layout.prop(settings, "body_type")
            layout.prop(settings, "add_rig")
            layout.operator("humanoid.generate_blockout", icon="OUTLINER_OB_MESH")
            layout.label(text="Rigid joints; separate parts")


_CLASSES = (HUMANOID_PG_settings, HUMANOID_OT_generate, HUMANOID_PT_panel)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.humanoid_settings = PointerProperty(type=HUMANOID_PG_settings)


def unregister():
    del bpy.types.Scene.humanoid_settings
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
