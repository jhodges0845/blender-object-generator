# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic adult, stylized proportion generation."""

from math import sqrt

from ..models import HumanoidProportions, HumanoidSpec
from .rules import (
    GIRTH_RATIOS, LENGTH_RATIOS, MAX_HEIGHT_CM, MAX_WEIGHT_KG,
    MIN_HEIGHT_CM, MIN_WEIGHT_KG, REFERENCE_HEIGHT_CM,
    REFERENCE_WEIGHT_KG, SHAPE_FACTORS,
)


def generate_proportions(spec: HumanoidSpec) -> HumanoidProportions:
    """Calculate dimensions without modifying the input or any application state."""
    if not isinstance(spec, HumanoidSpec):
        raise TypeError("spec must be a HumanoidSpec")
    if not MIN_HEIGHT_CM <= spec.height_cm <= MAX_HEIGHT_CM:
        raise ValueError(f"height_cm must be between {MIN_HEIGHT_CM:g} and "
                         f"{MAX_HEIGHT_CM:g} for this generator")
    if not MIN_WEIGHT_KG <= spec.weight_kg <= MAX_WEIGHT_KG:
        raise ValueError(f"weight_kg must be between {MIN_WEIGHT_KG:g} and "
                         f"{MAX_WEIGHT_KG:g} for this generator")

    height_scale = spec.height_cm / REFERENCE_HEIGHT_CM
    reference_weight = REFERENCE_WEIGHT_KG * height_scale ** 3
    girth_scale = sqrt(spec.weight_kg / reference_weight)
    shape = SHAPE_FACTORS[spec.body_type]
    dimensions = {
        name: spec.height_cm * ratio for name, ratio in LENGTH_RATIOS.items()
    }
    dimensions.update({
        name: spec.height_cm * ratio * girth_scale * getattr(shape, factor)
        for name, (ratio, factor) in GIRTH_RATIOS.items()
    })
    return HumanoidProportions(**dimensions)
