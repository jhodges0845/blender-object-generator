# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent dimensions for a symmetric, standing humanoid."""

from dataclasses import dataclass, fields

from .spec import _positive_finite_number


@dataclass(frozen=True)
class HumanoidProportions:
    """Full dimensions in centimeters, never radii or half-widths.

    Standing height is the sum of head, neck, torso, upper leg, lower leg,
    and foot height. Torso includes the pelvis. Limb lengths are per limb;
    left and right sides share the same dimensions. See docs/proportions.md
    for measurement landmarks and the intended pose.
    """

    head_height_cm: float
    head_width_cm: float
    head_depth_cm: float
    neck_length_cm: float
    neck_width_cm: float
    torso_length_cm: float
    shoulder_width_cm: float
    chest_width_cm: float
    chest_depth_cm: float
    waist_width_cm: float
    waist_depth_cm: float
    hip_width_cm: float
    hip_depth_cm: float
    upper_arm_length_cm: float
    forearm_length_cm: float
    upper_arm_thickness_cm: float
    forearm_thickness_cm: float
    hand_length_cm: float
    upper_leg_length_cm: float
    lower_leg_length_cm: float
    thigh_thickness_cm: float
    calf_thickness_cm: float
    foot_height_cm: float
    foot_length_cm: float

    def __post_init__(self) -> None:
        for field in fields(self):
            object.__setattr__(self, field.name, _positive_finite_number(
                field.name, getattr(self, field.name)
            ))

    @property
    def standing_height_cm(self) -> float:
        return sum((self.head_height_cm, self.neck_length_cm,
                    self.torso_length_cm, self.upper_leg_length_cm,
                    self.lower_leg_length_cm, self.foot_height_cm))
