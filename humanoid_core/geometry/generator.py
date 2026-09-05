"""Generate a symmetric low-poly A-pose blockout from proportions."""

from math import cos, radians, sin

from humanoid_core.models import HumanoidProportions
from humanoid_core.models.mesh import HumanoidMesh
from .primitives import limb, vertical_loft


ARM_ANGLE_FROM_VERTICAL_DEGREES = 30.0


def generate_mesh(proportions: HumanoidProportions) -> HumanoidMesh:
    """Return separate capped body parts in centimeters, with feet on Z=0.

    This blockout is deliberately not welded, UV-mapped, rigged, or skinned.
    It consumes dimensions directly so adapters never own generation rules.
    """
    if not isinstance(proportions, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    p = proportions
    ankle_z = p.foot_height_cm
    knee_z = ankle_z + p.lower_leg_length_cm
    hip_z = knee_z + p.upper_leg_length_cm
    shoulder_z = hip_z + p.torso_length_cm
    chin_z = shoulder_z + p.neck_length_cm
    crown_z = chin_z + p.head_height_cm

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

    angle = radians(ARM_ANGLE_FROM_VERTICAL_DEGREES)
    for side, sign in (("left", 1), ("right", -1)):
        leg_x = sign * p.hip_width_cm * 0.25
        ankle = (leg_x, 0.0, ankle_z)
        knee = (leg_x, 0.0, knee_z)
        hip = (leg_x, 0.0, hip_z)
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

        def advance(point, length):
            return (point[0] + sign * sin(angle) * length, 0.0,
                    point[2] - cos(angle) * length)

        shoulder = (sign * p.shoulder_width_cm * 0.5, 0.0, shoulder_z)
        elbow = advance(shoulder, p.upper_arm_length_cm)
        wrist = advance(elbow, p.forearm_length_cm)
        fingertips = advance(wrist, p.hand_length_cm)
        parts.extend((
            limb(f"upper_arm.{side}", shoulder, elbow,
                 p.upper_arm_thickness_cm, p.upper_arm_thickness_cm * 0.8),
            limb(f"forearm.{side}", elbow, wrist,
                 p.forearm_thickness_cm, p.forearm_thickness_cm * 0.7),
            limb(f"hand.{side}", wrist, fingertips,
                 p.forearm_thickness_cm * 0.8, p.forearm_thickness_cm * 0.65,
                 depth_ratio=0.5),
        ))
    return HumanoidMesh(tuple(parts))
