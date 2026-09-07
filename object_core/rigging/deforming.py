# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender-independent deforming rig and skin-weight generation for Human 1.0."""

from math import sqrt

from ..models.mesh import ObjectMesh
from ..models.proportions import HumanoidProportions
from ..models.skeleton import Bone, Skeleton
from ..models.skinning import BoneWeight, SkinWeights
from ..proportions.landmarks import generate_landmarks


def generate_deforming_skeleton(proportions: HumanoidProportions) -> Skeleton:
    """Return the Human 1.0 skeleton without legacy rigid-part bindings."""
    if not isinstance(proportions, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    points = generate_landmarks(proportions)
    hip = points["hip_center"]
    bones = [
        Bone("root", hip, (hip[0], hip[1], hip[2] + proportions.torso_length_cm * 0.1)),
        Bone("torso", hip, points["shoulder_center"], "root"),
        Bone("neck", points["shoulder_center"], points["chin"], "torso"),
        Bone("head", points["chin"], points["crown"], "neck"),
    ]
    for side in ("left", "right"):
        bones.extend(
            (
                Bone("upper_arm." + side, points["shoulder." + side], points["elbow." + side], "torso"),
                Bone("forearm." + side, points["elbow." + side], points["wrist." + side], "upper_arm." + side),
                Bone("hand." + side, points["wrist." + side], points["fingertips." + side], "forearm." + side),
                Bone("upper_leg." + side, points["hip." + side], points["knee." + side], "root"),
                Bone("lower_leg." + side, points["knee." + side], points["ankle." + side], "upper_leg." + side),
                Bone("foot." + side, points["ankle." + side], points["toe." + side], "lower_leg." + side),
            )
        )
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
    """Keep skinning local enough to prevent left/right limb cross-influence."""
    x = vertex[0]
    side = "left" if x >= 0 else "right"
    limb_side = tuple(
        bone for bone in bones
        if not (bone.name.endswith(".left") or bone.name.endswith(".right"))
        or bone.name.endswith("." + side)
    )
    return limb_side


def _weights_for_vertex(vertex, bones, max_influences=4):
    candidates = _candidate_bones(vertex, bones)
    ranked = sorted(
        ((_distance_to_segment(vertex, bone.head, bone.tail), bone.name) for bone in candidates),
        key=lambda item: (item[0], item[1]),
    )[:max_influences]
    # A small epsilon makes vertices lying directly on a bone deterministic and finite.
    raw = [(name, 1.0 / ((distance + 1e-3) ** 2)) for distance, name in ranked]
    total = sum(value for _, value in raw)
    normalized = [(name, value / total) for name, value in raw]
    # Force exact normalization after floating point division.
    correction = 1.0 - sum(value for _, value in normalized)
    name, value = normalized[0]
    normalized[0] = (name, value + correction)
    return tuple(BoneWeight(name, value) for name, value in normalized if value > 0.0)


def generate_skin_weights(mesh: ObjectMesh, skeleton: Skeleton, *, max_influences=4):
    """Return deterministic normalized weights for each vertex of each mesh part."""
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    if not isinstance(skeleton, Skeleton):
        raise TypeError("skeleton must be Skeleton")
    if isinstance(max_influences, bool) or not isinstance(max_influences, int):
        raise TypeError("max_influences must be an integer")
    if max_influences < 1:
        raise ValueError("max_influences must be at least 1")
    deform_bones = tuple(bone for bone in skeleton.bones if bone.name != "root")
    if not deform_bones:
        raise ValueError("skeleton must contain deform bones")
    return tuple(
        SkinWeights(
            part.name,
            tuple(_weights_for_vertex(vertex, deform_bones, max_influences) for vertex in part.vertices),
        )
        for part in mesh.parts
    )
