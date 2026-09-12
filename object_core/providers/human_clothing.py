# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-specific lightweight clothing proof using the existing parent rig."""

from ..models import BoneWeight, MeshPart, ObjectMesh, Skeleton, SkinWeights


def _bone(skeleton, name):
    return next((bone for bone in skeleton.bones if bone.name == name), None)


def basic_shirt_mesh(skeleton, ease_cm=2.0, length_cm=42.0):
    """Return a deliberately simple torso garment fitted around the Human rig."""
    if not isinstance(skeleton, Skeleton):
        raise TypeError("skeleton must be Skeleton")
    if ease_cm < 0 or length_cm <= 0:
        raise ValueError("shirt ease must be nonnegative and length must be positive")
    torso = _bone(skeleton, "torso")
    neck = _bone(skeleton, "neck")
    if torso is None or neck is None:
        raise ValueError("Human shirt requires torso and neck bones")

    top_z = neck.head[2] - 2.0
    bottom_z = max(torso.head[2], top_z - length_cm)
    half_width = max(16.0, abs(neck.head[0] - torso.head[0]) + 22.0) + ease_cm
    half_depth = 10.0 + ease_cm
    vertices = (
        (-half_width, -half_depth, bottom_z), (half_width, -half_depth, bottom_z),
        (half_width, half_depth, bottom_z), (-half_width, half_depth, bottom_z),
        (-half_width, -half_depth, top_z), (half_width, -half_depth, top_z),
        (half_width, half_depth, top_z), (-half_width, half_depth, top_z),
    )
    # Open neck/top and bottom so this behaves as a garment shell rather than a solid box.
    faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
    return ObjectMesh((MeshPart("Shirt", vertices, faces),))


def basic_shirt_weights(mesh):
    """Weight upper garment vertices toward neck and lower vertices to torso."""
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    result = []
    for part in mesh.parts:
        min_z = min(vertex[2] for vertex in part.vertices)
        max_z = max(vertex[2] for vertex in part.vertices)
        span = max(max_z - min_z, 1e-6)
        vertices = []
        for vertex in part.vertices:
            t = (vertex[2] - min_z) / span
            neck_amount = min(0.35, max(0.0, (t - 0.55) / 0.45 * 0.35))
            if neck_amount > 0:
                vertices.append((BoneWeight("torso", 1.0 - neck_amount), BoneWeight("neck", neck_amount)))
            else:
                vertices.append((BoneWeight("torso", 1.0),))
        result.append(SkinWeights(part.name, tuple(vertices)))
    return tuple(result)


__all__ = ["basic_shirt_mesh", "basic_shirt_weights"]
