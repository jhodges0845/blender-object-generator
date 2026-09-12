# SPDX-License-Identifier: GPL-3.0-or-later
"""Avian rig and skin-weight generation."""

from math import sqrt

from ..models import Bone, BoneWeight, Skeleton, SkinWeights


def generate_avian_skeleton(dimensions):
    """Build a deterministic Avian skeleton from validated dimensions."""
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    wingspan = dimensions["wingspan_cm"]
    tail_length = dimensions["tail_length_cm"]

    body_z = height * 0.56
    rear_y = -length * 0.34
    chest_y = length * 0.28
    neck_y = length * 0.48
    head_y = length * 0.66
    half_span = wingspan * 0.5
    shoulder_x = width * 0.34
    shoulder_y = length * 0.08
    shoulder_z = body_z + height * 0.12
    tail_base_y = -length * 0.48

    bones = [
        Bone("root", (0, 0, height * 0.22), (0, 0, body_z)),
        Bone("spine", (0, rear_y, body_z), (0, chest_y, body_z + height * 0.06), "root"),
        Bone("neck", (0, chest_y, body_z + height * 0.06), (0, neck_y, body_z + height * 0.22), "spine"),
        Bone("head", (0, neck_y, body_z + height * 0.22), (0, head_y, body_z + height * 0.30), "neck"),
    ]

    for side, sign in (("left", -1.0), ("right", 1.0)):
        shoulder = (sign * shoulder_x, shoulder_y, shoulder_z)
        elbow = (sign * (shoulder_x + (half_span - shoulder_x) * 0.50), shoulder_y - length * 0.06, shoulder_z - height * 0.07)
        tip = (sign * half_span, shoulder_y - length * 0.16, shoulder_z - height * 0.12)
        bones.extend((
            Bone("wing.upper." + side, shoulder, elbow, "spine"),
            Bone("wing.lower." + side, elbow, tip, "wing.upper." + side),
        ))

    # Birds need a ground-contact chain as well as wings. Keep the leg anatomy
    # provider-specific so shared Blender rigging stays body-plan agnostic.
    hip_x = width * 0.24
    hip_y = -length * 0.04
    hip_z = body_z - height * 0.28
    knee_z = height * 0.28
    ankle_z = height * 0.08
    toe_y = hip_y + length * 0.16
    for side, sign in (("left", -1.0), ("right", 1.0)):
        hip = (sign * hip_x, hip_y, hip_z)
        knee = (sign * hip_x * 1.08, hip_y + length * 0.025, knee_z)
        ankle = (sign * hip_x * 1.02, hip_y + length * 0.055, ankle_z)
        toe = (sign * hip_x, toe_y, ankle_z * 0.72)
        bones.extend((
            Bone("leg.upper." + side, hip, knee, "spine"),
            Bone("leg.lower." + side, knee, ankle, "leg.upper." + side),
            Bone("foot." + side, ankle, toe, "leg.lower." + side),
        ))

    tail_segment = max(tail_length / 2.0, 1.0)
    start = (0, tail_base_y, body_z)
    mid = (0, tail_base_y - tail_segment, body_z + height * 0.04)
    tip = (0, tail_base_y - tail_length, body_z + height * 0.02)
    bones.extend((
        Bone("tail.1", start, mid, "spine"),
        Bone("tail.2", mid, tip, "tail.1"),
    ))
    return Skeleton(tuple(bones))


def _distance_to_segment(point, start, end):
    axis = tuple(end[i] - start[i] for i in range(3))
    offset = tuple(point[i] - start[i] for i in range(3))
    length_sq = sum(value * value for value in axis)
    amount = sum(offset[i] * axis[i] for i in range(3)) / length_sq
    amount = max(0.0, min(1.0, amount))
    closest = tuple(start[i] + axis[i] * amount for i in range(3))
    return sqrt(sum((point[i] - closest[i]) ** 2 for i in range(3)))


def _candidate_bones(vertex, bones):
    side = "left" if vertex[0] <= 0 else "right"
    return tuple(
        bone for bone in bones
        if not (bone.name.endswith(".left") or bone.name.endswith(".right"))
        or bone.name.endswith("." + side)
    )


def _weights_for_vertex(vertex, bones, max_influences=4):
    candidates = _candidate_bones(vertex, bones)
    ranked = sorted(
        ((_distance_to_segment(vertex, bone.head, bone.tail), bone) for bone in candidates),
        key=lambda item: (item[0], item[1].name),
    )
    nearest = ranked[0][1]
    local_names = {nearest.name}
    if nearest.parent:
        local_names.add(nearest.parent)
    local_names.update(bone.name for bone in candidates if bone.parent == nearest.name)
    local = [(distance, bone) for distance, bone in ranked if bone.name in local_names][:max_influences]
    raw = [(bone.name, 1.0 / ((distance + 1e-3) ** 2)) for distance, bone in local]
    total = sum(value for _name, value in raw)
    normalized = [(name, value / total) for name, value in raw]
    correction = 1.0 - sum(value for _name, value in normalized)
    normalized[0] = (normalized[0][0], normalized[0][1] + correction)
    return tuple(BoneWeight(name, value) for name, value in normalized if value > 0)


def generate_avian_skin_weights(mesh, skeleton, *, max_influences=4):
    """Return normalized local weights for the connected Avian surface."""
    deform_bones = tuple(bone for bone in skeleton.bones if bone.name != "root")
    if not deform_bones:
        raise ValueError("Avian skeleton must contain deform bones")
    return tuple(
        SkinWeights(
            part.name,
            tuple(_weights_for_vertex(vertex, deform_bones, max_influences) for vertex in part.vertices),
        )
        for part in mesh.parts
    )
