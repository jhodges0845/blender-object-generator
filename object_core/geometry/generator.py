# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate a symmetric low-poly A-pose blockout from proportions."""

from ..models import HumanoidProportions
from ..models.mesh import ObjectMesh
from .primitives import limb, vertical_loft
from ..proportions.landmarks import generate_landmarks


def generate_mesh(proportions: HumanoidProportions) -> ObjectMesh:
    """Return separate capped body parts in centimeters, with feet on Z=0.

    This blockout is deliberately not welded, UV-mapped, rigged, or skinned.
    It consumes dimensions directly so adapters never own generation rules.
    """
    if not isinstance(proportions, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    p = proportions
    points = generate_landmarks(p)
    ankle_z = points["ankle.left"][2]
    hip_z = points["hip_center"][2]
    shoulder_z = points["shoulder_center"][2]
    chin_z = points["chin"][2]
    crown_z = points["crown"][2]

    parts = [
        vertical_loft("torso", (
            (hip_z, p.hip_width_cm, p.hip_depth_cm),
            (hip_z + p.torso_length_cm * 0.35, p.waist_width_cm, p.waist_depth_cm),
            (hip_z + p.torso_length_cm * 0.78, p.chest_width_cm, p.chest_depth_cm),
            (shoulder_z, p.shoulder_width_cm, p.chest_depth_cm * 0.8),
        )),
        vertical_loft("neck", (
            (shoulder_z, p.neck_width_cm, p.neck_width_cm),
            (chin_z, p.neck_width_cm * 0.9, p.neck_width_cm * 0.9),
        )),
        vertical_loft("head", (
            (chin_z, p.head_width_cm * 0.65, p.head_depth_cm * 0.75),
            (chin_z + p.head_height_cm * 0.3, p.head_width_cm, p.head_depth_cm),
            (chin_z + p.head_height_cm * 0.8, p.head_width_cm, p.head_depth_cm),
            (crown_z, p.head_width_cm * 0.7, p.head_depth_cm * 0.7),
        )),
    ]

    for side in ("left", "right"):
        ankle = points["ankle." + side]
        knee = points["knee." + side]
        hip = points["hip." + side]
        leg_x = hip[0]
        parts.extend((
            limb(f"upper_leg.{side}", knee, hip,
                 p.thigh_thickness_cm * 0.7, p.thigh_thickness_cm),
            limb(f"lower_leg.{side}", ankle, knee,
                 p.calf_thickness_cm * 0.6, p.calf_thickness_cm),
            vertical_loft(f"foot.{side}", (
                (0.0, p.calf_thickness_cm * 0.8, p.foot_length_cm),
                (ankle_z, p.calf_thickness_cm * 0.6, p.foot_length_cm * 0.9),
            ), center_x=leg_x, center_y=p.foot_length_cm * 0.25),
        ))

        shoulder = points["shoulder." + side]
        elbow = points["elbow." + side]
        wrist = points["wrist." + side]
        fingertips = points["fingertips." + side]
        parts.extend((
            limb(f"upper_arm.{side}", shoulder, elbow,
                 p.upper_arm_thickness_cm, p.upper_arm_thickness_cm * 0.8),
            limb(f"forearm.{side}", elbow, wrist,
                 p.forearm_thickness_cm, p.forearm_thickness_cm * 0.7),
            limb(f"hand.{side}", wrist, fingertips,
                 p.forearm_thickness_cm * 0.8, p.forearm_thickness_cm * 0.65,
                 depth_ratio=0.5),
        ))
    return ObjectMesh(tuple(parts))
