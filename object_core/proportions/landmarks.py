# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared rest-pose landmarks for mesh and skeleton generation, in centimeters."""

from math import cos, radians, sin
from types import MappingProxyType

from ..models.proportions import HumanoidProportions

ARM_ANGLE_FROM_VERTICAL_DEGREES = 30.0


def generate_landmarks(p: HumanoidProportions):
    if not isinstance(p, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    ankle_z = p.foot_height_cm
    knee_z = ankle_z + p.lower_leg_length_cm
    hip_z = knee_z + p.upper_leg_length_cm
    shoulder_z = hip_z + p.torso_length_cm
    chin_z = shoulder_z + p.neck_length_cm
    points = {"hip_center": (0.0, 0.0, hip_z),
              "shoulder_center": (0.0, 0.0, shoulder_z),
              "chin": (0.0, 0.0, chin_z),
              "crown": (0.0, 0.0, chin_z + p.head_height_cm)}
    angle = radians(ARM_ANGLE_FROM_VERTICAL_DEGREES)
    for side, sign in (("left", 1), ("right", -1)):
        x = sign * p.hip_width_cm * 0.25
        for name, z in (("ankle", ankle_z), ("knee", knee_z), ("hip", hip_z)):
            points[name + "." + side] = (x, 0.0, z)
        points["toe." + side] = (x, p.foot_length_cm * 0.75, ankle_z)
        point = (sign * p.shoulder_width_cm * 0.5, 0.0, shoulder_z)
        points["shoulder." + side] = point
        for name, length in (("elbow", p.upper_arm_length_cm), ("wrist", p.forearm_length_cm),
                             ("fingertips", p.hand_length_cm)):
            point = (point[0] + sign * sin(angle) * length, 0.0,
                     point[2] - cos(angle) * length)
            points[name + "." + side] = point
    return MappingProxyType(points)
