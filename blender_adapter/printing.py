# SPDX-License-Identifier: GPL-3.0-or-later
"""Read evaluated print geometry and write millimetre STL without changing source assets."""

from math import isfinite
import struct

from .core import AssetSnapshot


def _components(bm):
    count = 0
    unseen = set(bm.verts)
    while unseen:
        count += 1
        pending = [unseen.pop()]
        while pending:
            vert = pending.pop()
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                if other in unseen:
                    unseen.remove(other)
                    pending.append(other)
    return count


def _invalid_reasons(bm, check_self_intersection=True):
    """Return concrete print-topology failures instead of one opaque invalid flag.

    Source geometry gets the full BVH overlap check. A successful voxel remesh is
    validated as a closed solid structurally because the remesh itself is the
    operation that resolves source self-intersections; re-running the triangle
    overlap heuristic on that generated surface can report false positives where
    voxel faces meet closely.
    """
    reasons = []
    if not bm.faces:
        reasons.append('no faces')
        return tuple(reasons)
    if any(not edge.is_manifold for edge in bm.edges):
        reasons.append('non-manifold edges')
    if any(not edge.is_contiguous for edge in bm.edges):
        reasons.append('inconsistent face winding')
    if any(not isfinite(v) for vert in bm.verts for v in vert.co):
        reasons.append('non-finite vertices')
    if any(face.calc_area() <= 1e-12 for face in bm.faces):
        reasons.append('degenerate faces')
    volume = bm.calc_volume(signed=True)
    if not isfinite(volume) or abs(volume) <= 1e-12:
        reasons.append('zero or invalid enclosed volume')

    if check_self_intersection and not reasons:
        from mathutils.bvhtree import BVHTree

        bm.faces.ensure_lookup_table()
        tree = BVHTree.FromBMesh(bm)
        for first, second in tree.overlap(tree):
            if first != second and not set(bm.faces[first].verts).intersection(bm.faces[second].verts):
                reasons.append('self-intersection')
                break
    return tuple(reasons)


def _evaluated_bmesh(objects, context):
    """Combine evaluated mesh objects into one world-space bmesh."""
    import bmesh
    import bpy

    graph = context.evaluated_depsgraph_get()
    combined = bmesh.new()
    mesh_count = 0
    for obj in objects:
        if obj.type != 'MESH':
            continue
        mesh_count += 1
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        source = bmesh.new()
        try:
            source.from_mesh(mesh)
            source.transform(evaluated.matrix_world)
            source_mesh = bpy.data.meshes.new('AssetAssistantPrintSource')
            try:
                source.to_mesh(source_mesh)
                combined.from_mesh(source_mesh)
            finally:
                bpy.data.meshes.remove(source_mesh)
        finally:
            source.free()
            evaluated.to_mesh_clear()
    return combined, mesh_count


def _voxel_repair(bm, context):
    """Return a temporary manifold bmesh made from the evaluated printable volume.

    The source asset is never modified. The temporary object is needed because
    Blender's voxel remesh is an object operator in both supported Blender lines.
    """
    import bmesh
    import bpy

    mesh = bpy.data.meshes.new('AssetAssistantPrintableMesh')
    obj = bpy.data.objects.new('AssetAssistantPrintable', mesh)
    context.scene.collection.objects.link(obj)
    previous_selected = tuple(context.selected_objects)
    previous_active = context.view_layer.objects.active
    repaired = None
    try:
        bm.to_mesh(mesh)
        dimensions = [max((vert.co[i] for vert in bm.verts), default=0.0) -
                      min((vert.co[i] for vert in bm.verts), default=0.0)
                      for i in range(3)]
        longest = max(dimensions) if dimensions else 0.0
        if longest <= 0:
            return None
        mesh.remesh_mode = 'VOXEL'
        mesh.remesh_voxel_size = max(0.0001, longest / 256.0)
        mesh.remesh_voxel_adaptivity = 0.0

        for selected in context.selected_objects:
            selected.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        result = bpy.ops.object.voxel_remesh()
        if 'FINISHED' not in result:
            return None

        repaired = bmesh.new()
        repaired.from_mesh(obj.data)
        if repaired.faces:
            bmesh.ops.recalc_face_normals(repaired, faces=list(repaired.faces))
        return repaired
    finally:
        for selected in tuple(context.selected_objects):
            selected.select_set(False)
        for selected in previous_selected:
            if selected.name in context.view_layer.objects:
                selected.select_set(True)
        context.view_layer.objects.active = previous_active
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.name in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)


def print_geometry(objects, context):
    """Return validated printable geometry, repairing only source self-intersections.

    Cura preparation may resolve a self-intersection in an otherwise closed,
    manifold solid (the current Human case). Structural failures such as open or
    non-manifold geometry are never auto-closed by the repair path; those remain
    validation errors that the source asset must fix.
    """
    import bmesh

    bm, count = _evaluated_bmesh(objects, context)
    repaired = None
    try:
        source_reasons = _invalid_reasons(bm)
        if source_reasons == ('self-intersection',):
            repaired = _voxel_repair(bm, context)
            working = repaired if repaired is not None else bm
            reasons = _invalid_reasons(working, check_self_intersection=False)
        else:
            working = bm
            reasons = source_reasons

        invalid = () if not reasons else ('printable geometry (' + ', '.join(reasons) + ')',)
        components = _components(working)
        bmesh.ops.triangulate(working, faces=list(working.faces))
        triangles = [tuple(tuple(vert.co) for vert in face.verts) for face in working.faces]
        return AssetSnapshot(mesh_count=count, invalid_meshes=invalid, is_blockout=False), components, triangles
    finally:
        if repaired is not None:
            repaired.free()
        bm.free()


def _scene_scale_divisor():
    """Read the optional Cura UI scale preset while keeping 1:1 as the API default."""
    try:
        import bpy
        settings = getattr(bpy.context.scene, 'humanoid_settings', None)
        value = getattr(settings, 'cura_print_scale', '1') if settings else '1'
        return float(value)
    except (AttributeError, TypeError, ValueError):
        return 1.0


def write_stl(filepath, triangles, unit_scale, scale_divisor=None):
    """Write binary STL in millimetres at the requested physical print ratio."""
    from mathutils import Vector

    if scale_divisor is None:
        scale_divisor = _scene_scale_divisor()
    if not isfinite(scale_divisor) or scale_divisor <= 0:
        raise ValueError('Cura print scale divisor must be greater than zero.')
    millimetre_scale = unit_scale * 1000 / scale_divisor

    with open(filepath, 'xb') as stream:
        stream.write(b'Object Generator - Cura STL in millimetres'.ljust(80, b'\0'))
        stream.write(struct.pack('<I', len(triangles)))
        for triangle in triangles:
            vertices = [Vector(vertex) * millimetre_scale for vertex in triangle]
            normal = (vertices[1] - vertices[0]).cross(vertices[2] - vertices[0]).normalized()
            values = tuple(normal) + tuple(value for vertex in vertices for value in vertex)
            stream.write(struct.pack('<12fH', *values, 0))
    return {'FINISHED'}
