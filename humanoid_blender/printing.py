# SPDX-License-Identifier: GPL-3.0-or-later
"""Read evaluated print geometry and write millimetre STL without changing the scene."""

from math import isfinite
import struct

from .core import AssetSnapshot


def print_geometry(objects, context):
    import bmesh
    from mathutils.bvhtree import BVHTree

    graph = context.evaluated_depsgraph_get()
    triangles, invalid = [], []
    count, components = 0, 0
    for obj in objects:
        if obj.type != 'MESH':
            continue
        count += 1
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            bm.transform(evaluated.matrix_world)
            bad = (not bm.faces or any(not edge.is_manifold or not edge.is_contiguous for edge in bm.edges)
                   or any(not isfinite(v) for vert in bm.verts for v in vert.co)
                   or any(face.calc_area() <= 1e-12 for face in bm.faces)
                   or bm.calc_volume(signed=True) <= 1e-12)
            if not bad:
                bm.faces.ensure_lookup_table()
                tree = BVHTree.FromBMesh(bm)
                for first, second in tree.overlap(tree):
                    if first != second and not set(bm.faces[first].verts).intersection(bm.faces[second].verts):
                        bad = True
                        break
            if bad:
                invalid.append(obj.name)
            unseen = set(bm.verts)
            while unseen:
                components += 1
                pending = [unseen.pop()]
                while pending:
                    vert = pending.pop()
                    for edge in vert.link_edges:
                        other = edge.other_vert(vert)
                        if other in unseen:
                            unseen.remove(other)
                            pending.append(other)
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            for face in bm.faces:
                triangles.append(tuple(tuple(vert.co) for vert in face.verts))
        finally:
            bm.free()
            evaluated.to_mesh_clear()
    return AssetSnapshot(mesh_count=count, invalid_meshes=tuple(invalid), is_blockout=False), components, triangles


def write_stl(filepath, triangles, unit_scale):
    from mathutils import Vector

    with open(filepath, 'xb') as stream:
        stream.write(b'Object Generator - Cura STL in millimetres'.ljust(80, b'\0'))
        stream.write(struct.pack('<I', len(triangles)))
        for triangle in triangles:
            vertices = [Vector(vertex) * unit_scale * 1000 for vertex in triangle]
            normal = (vertices[1] - vertices[0]).cross(vertices[2] - vertices[0]).normalized()
            values = tuple(normal) + tuple(value for vertex in vertices for value in vertex)
            stream.write(struct.pack('<12fH', *values, 0))
    return {'FINISHED'}
