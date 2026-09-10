# SPDX-License-Identifier: GPL-3.0-or-later
"""Dog-specific quadruped rig and skin-weight generation."""

from ..models import Bone, BoneWeight, Skeleton, SkinWeights


def generate_dog_skeleton(dimensions):
    """Build a deterministic quadruped skeleton from validated Dog dimensions."""
    length = dimensions["body_length_cm"]
    shoulder = dimensions["shoulder_height_cm"]
    width = dimensions["body_width_cm"]
    head_length = dimensions["head_length_cm"]
    tail_length = dimensions["tail_length_cm"]

    torso_height = shoulder * 0.42
    torso_z = shoulder - torso_height * 0.48
    back_z = torso_z + torso_height * 0.18
    fore_y = length * 0.32
    hind_y = -length * 0.32
    leg_height = shoulder - torso_height * 0.45
    knee_z = leg_height * 0.48
    side_x = width * 0.34
    head_y = length * 0.5 + head_length * 0.28
    neck_y = length * 0.5
    tail_segment = max(tail_length / 3, 2.0)
    tail_base_y = -length * 0.5

    bones = [
        Bone("root", (0, 0, shoulder * 0.45), (0, 0, back_z)),
        Bone("spine", (0, hind_y, back_z), (0, fore_y, back_z), "root"),
        Bone("neck", (0, fore_y, back_z), (0, neck_y, shoulder), "spine"),
        Bone("head", (0, neck_y, shoulder),
             (0, head_y + head_length * 0.35, shoulder + torso_height * 0.08), "neck"),
    ]

    for side, x in (("left", -side_x), ("right", side_x)):
        bones.extend((
            Bone("fore_upper." + side, (x, fore_y, shoulder), (x, fore_y, knee_z), "spine"),
            Bone("fore_lower." + side, (x, fore_y, knee_z), (x, fore_y, 0), "fore_upper." + side),
            Bone("hind_upper." + side, (x, hind_y, shoulder * 0.86), (x, hind_y, knee_z), "root"),
            Bone("hind_lower." + side, (x, hind_y, knee_z), (x, hind_y, 0), "hind_upper." + side),
        ))

    parent = "root"
    start_y = tail_base_y
    start_z = back_z
    for index in range(3):
        end_y = start_y - tail_segment * 0.75
        end_z = start_z + torso_height * 0.12
        name = "tail.%d" % (index + 1)
        bones.append(Bone(name, (0, start_y, start_z), (0, end_y, end_z), parent))
        parent = name
        start_y, start_z = end_y, end_z

    return Skeleton(tuple(bones))


def _single(name):
    return (BoneWeight(name, 1.0),)


def _leg_weights(part, upper_name, lower_name):
    zs = [vertex[2] for vertex in part.vertices]
    midpoint = (min(zs) + max(zs)) / 2
    return tuple(_single(upper_name if vertex[2] > midpoint else lower_name) for vertex in part.vertices)


def generate_dog_skin_weights(mesh):
    """Return local quadruped skin weights for the current Dog blockout."""
    weights = []
    for part in mesh.parts:
        name = part.name
        if name == "dog_torso":
            rows = tuple(_single("spine") for _ in part.vertices)
        elif name in ("dog_head", "dog_muzzle"):
            rows = tuple(_single("head") for _ in part.vertices)
        elif name.startswith("dog_foreleg_"):
            side = name.rsplit("_", 1)[1]
            rows = _leg_weights(part, "fore_upper." + side, "fore_lower." + side)
        elif name.startswith("dog_hindleg_"):
            side = name.rsplit("_", 1)[1]
            rows = _leg_weights(part, "hind_upper." + side, "hind_lower." + side)
        elif name.startswith("dog_tail_"):
            index = int(name.rsplit("_", 1)[1])
            rows = tuple(_single("tail.%d" % index) for _ in part.vertices)
        else:
            raise ValueError("Unsupported Dog mesh part for skinning: " + name)
        weights.append(SkinWeights(name, rows))
    return tuple(weights)
