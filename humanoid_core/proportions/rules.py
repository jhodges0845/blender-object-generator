# SPDX-License-Identifier: GPL-3.0-or-later
"""Initial artistic calibration. These constants are not anatomical measurements."""

from dataclasses import dataclass
from types import MappingProxyType

from ..models import BodyType


MIN_HEIGHT_CM = 120.0
MAX_HEIGHT_CM = 240.0
MIN_WEIGHT_KG = 30.0
MAX_WEIGHT_KG = 300.0
REFERENCE_HEIGHT_CM = 180.0
REFERENCE_WEIGHT_KG = 80.0


@dataclass(frozen=True)
class ShapeFactors:
    shoulders: float
    chest: float
    waist: float
    hips: float
    arms: float
    legs: float


SHAPE_FACTORS = MappingProxyType({
    BodyType.SLIM: ShapeFactors(0.95, 0.90, 0.85, 0.93, 0.85, 0.90),
    BodyType.AVERAGE: ShapeFactors(1.00, 1.00, 1.00, 1.00, 1.00, 1.00),
    BodyType.MUSCULAR: ShapeFactors(1.12, 1.15, 0.95, 1.03, 1.25, 1.15),
    BodyType.OVERWEIGHT: ShapeFactors(1.02, 1.10, 1.20, 1.12, 1.10, 1.12),
    BodyType.OBESE: ShapeFactors(1.04, 1.22, 1.45, 1.28, 1.20, 1.25),
})

# Fractions of standing height. Axial segments sum to one.
LENGTH_RATIOS = MappingProxyType({
    "head_height_cm": 0.13,
    "neck_length_cm": 0.04,
    "torso_length_cm": 0.31,
    "upper_leg_length_cm": 0.25,
    "lower_leg_length_cm": 0.23,
    "foot_height_cm": 0.04,
    "upper_arm_length_cm": 0.18,
    "forearm_length_cm": 0.15,
    "hand_length_cm": 0.10,
    "foot_length_cm": 0.15,
    "head_width_cm": 0.09,
    "head_depth_cm": 0.11,
})

# Full transverse dimension as a height fraction, and its preset factor.
GIRTH_RATIOS = MappingProxyType({
    "neck_width_cm": (0.065, "chest"),
    "shoulder_width_cm": (0.23, "shoulders"),
    "chest_width_cm": (0.19, "chest"),
    "chest_depth_cm": (0.12, "chest"),
    "waist_width_cm": (0.16, "waist"),
    "waist_depth_cm": (0.11, "waist"),
    "hip_width_cm": (0.19, "hips"),
    "hip_depth_cm": (0.13, "hips"),
    "upper_arm_thickness_cm": (0.055, "arms"),
    "forearm_thickness_cm": (0.045, "arms"),
    "thigh_thickness_cm": (0.10, "legs"),
    "calf_thickness_cm": (0.07, "legs"),
})
