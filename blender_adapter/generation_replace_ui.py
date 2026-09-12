# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate a new base asset while replacing the currently referenced generated asset."""

import bpy


def _descendants(root):
    found = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        found.append(obj)
        stack.extend(obj.children)
    return found


def _remove_generated_asset(root):
    """Remove one generated asset hierarchy and now-empty generated collections."""
    if root is None:
        return

    objects = [root, *_descendants(root)]
    collections = {collection for obj in objects for collection in obj.users_collection}
    data_blocks = [(obj.type, obj.data) for obj in objects if getattr(obj, "data", None) is not None]

    for obj in reversed(objects):
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    for object_type, data in data_blocks:
        if data is None or data.users:
            continue
        if object_type == "MESH" and data.name in bpy.data.meshes:
            bpy.data.meshes.remove(data)
        elif object_type == "ARMATURE" and data.name in bpy.data.armatures:
            bpy.data.armatures.remove(data)

    for collection in collections:
        if collection.name in bpy.data.collections and not collection.objects and not collection.children:
            bpy.data.collections.remove(collection)


class ASSET_ASSISTANT_OT_generate_replace_current(bpy.types.Operator):
    """Generate from the current settings and replace the current generated target on success."""

    bl_idname = "asset_assistant.generate_replace_current"
    bl_label = "Generate Asset"
    bl_description = "Generate this asset and replace the currently referenced generated asset"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def execute(self, context):
        settings = context.scene.humanoid_settings
        previous = getattr(settings, "target", None)
        previous_name = previous.name if previous is not None else None
        previous_type = previous.get("object_type") if previous is not None else None

        result = bpy.ops.humanoid.generate_blockout()
        if "FINISHED" not in result:
            return {"CANCELLED"}

        current = getattr(settings, "target", None)
        if current is None:
            self.report({"ERROR"}, "Generation finished without selecting the new asset.")
            return {"CANCELLED"}

        if previous is not None and previous != current and previous.name in bpy.data.objects:
            same_type = previous_type == current.get("object_type")
            _remove_generated_asset(previous)
            if same_type and previous_name:
                current.name = previous_name
            self.report({"INFO"}, "Generated asset replaced the previous current asset.")
        else:
            self.report({"INFO"}, "Generated asset is now the current asset.")
        return {"FINISHED"}


_CLASSES = (ASSET_ASSISTANT_OT_generate_replace_current,)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
