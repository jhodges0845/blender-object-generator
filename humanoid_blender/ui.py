"""Blender sidebar and operator. Generation is delegated to the core."""

import bpy
from bpy.props import EnumProperty, FloatProperty, PointerProperty

from .adapter import create_character
from .core import (BodyType, HumanoidSpec, generate_mesh, generate_proportions,
                   MIN_HEIGHT_CM, MAX_HEIGHT_CM, MIN_WEIGHT_KG, MAX_WEIGHT_KG)


class HUMANOID_PG_settings(bpy.types.PropertyGroup):
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
        try:
            spec = HumanoidSpec(settings.height_cm, settings.weight_kg, BodyType(settings.body_type))
            mesh = generate_mesh(generate_proportions(spec))
            root = create_character(mesh, scene=context.scene)
        except (ValueError, TypeError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        root["height_cm"] = spec.height_cm
        root["weight_kg"] = spec.weight_kg
        root["body_type"] = spec.body_type.value
        root.location = context.scene.cursor.location
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in root.children:
            obj.select_set(True)
        root.select_set(True)
        context.view_layer.objects.active = root
        self.report({"INFO"}, "Created 15 editable blockout parts")
        return {"FINISHED"}


class HUMANOID_PT_panel(bpy.types.Panel):
    bl_label = "Humanoid Blockout"
    bl_idname = "HUMANOID_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Humanoid"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.humanoid_settings
        layout.prop(settings, "height_cm")
        layout.prop(settings, "weight_kg")
        layout.prop(settings, "body_type")
        layout.operator("humanoid.generate_blockout", icon="OUTLINER_OB_MESH")
        layout.label(text="Separate parts; no rig yet")


_CLASSES = (HUMANOID_PG_settings, HUMANOID_OT_generate, HUMANOID_PT_panel)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.humanoid_settings = PointerProperty(type=HUMANOID_PG_settings)


def unregister():
    del bpy.types.Scene.humanoid_settings
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
