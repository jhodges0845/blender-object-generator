# SPDX-License-Identifier: GPL-3.0-or-later
"""Undoable, conservative material preparation for generated assets."""

from .targets import asset_objects


def prepare_materials(root):
    """Fill missing face materials only; preserve existing materials and shared meshes."""
    import bpy

    default = None
    for obj in asset_objects(root):
        if obj.type != 'MESH':
            continue
        missing = [face.index for face in obj.data.polygons
                   if face.material_index >= len(obj.material_slots)
                   or obj.material_slots[face.material_index].material is None]
        if not missing:
            continue
        if default is None:
            default = bpy.data.materials.new('Generator Material')
            default.use_nodes = True
            shader = default.node_tree.nodes.get('Principled BSDF')
            shader.inputs['Base Color'].default_value = (0.55, 0.55, 0.55, 1)
            shader.inputs['Roughness'].default_value = 0.65
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        index = len(obj.data.materials)
        obj.data.materials.append(default)
        for face_index in missing:
            obj.data.polygons[face_index].material_index = index
    return default


def material_issues(objects):
    """Reject shader graphs that these file exporters cannot reliably translate."""
    from .core import ValidationIssue

    seen = set()
    issues = []
    for obj in objects:
        for slot in obj.material_slots:
            material = slot.material
            if material is None or material.as_pointer() in seen or not material.use_nodes:
                continue
            seen.add(material.as_pointer())
            outputs = [node for node in material.node_tree.nodes
                       if node.type == 'OUTPUT_MATERIAL' and node.is_active_output]
            surface = outputs[0].inputs['Surface'] if outputs else None
            shader = surface.links[0].from_node if surface and surface.is_linked else None
            supported = shader is not None and shader.type == 'BSDF_PRINCIPLED'
            if supported:
                for socket in shader.inputs:
                    for link in socket.links:
                        source = link.from_node
                        if source.type == 'NORMAL_MAP':
                            source = source.inputs['Color'].links[0].from_node if source.inputs['Color'].is_linked else None
                        if source is None or source.type != 'TEX_IMAGE':
                            supported = False
                        elif source.inputs['Vector'].is_linked:
                            supported = False
            if not supported or (outputs and outputs[0].inputs['Displacement'].is_linked):
                issues.append(ValidationIssue('material_shader', 'ERROR', material.name +
                    ': use a Principled BSDF with plain values or direct image textures; bake procedural shaders and mapping before export.'))
    return tuple(issues)
