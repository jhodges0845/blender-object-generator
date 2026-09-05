"""Simple forward-kinematic skeleton for the separate-part humanoid blockout."""

from ..models.proportions import HumanoidProportions
from ..models.skeleton import Bone, Skeleton
from ..proportions.landmarks import generate_landmarks


def generate_skeleton(proportions: HumanoidProportions) -> Skeleton:
    points = generate_landmarks(proportions)
    hip = points["hip_center"]
    bones = [Bone("root", hip, (hip[0], hip[1], hip[2] + proportions.torso_length_cm * 0.1)),
             Bone("torso", hip, points["shoulder_center"], "root", "torso"),
             Bone("neck", points["shoulder_center"], points["chin"], "torso", "neck"),
             Bone("head", points["chin"], points["crown"], "neck", "head")]
    for side in ("left", "right"):
        for name, start, end, parent in (
            ("upper_arm", "shoulder", "elbow", "torso"),
            ("forearm", "elbow", "wrist", "upper_arm." + side),
            ("hand", "wrist", "fingertips", "forearm." + side),
            ("upper_leg", "hip", "knee", "root"),
            ("lower_leg", "knee", "ankle", "upper_leg." + side),
            ("foot", "ankle", "toe", "lower_leg." + side),
        ):
            part = name + "." + side
            bones.append(Bone(part, points[start + "." + side], points[end + "." + side], parent, part))
    return Skeleton(tuple(bones))
