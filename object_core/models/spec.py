# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-selected humanoid inputs; no host application dependencies."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class BodyType(str, Enum):
    """Artistic shape presets, not medical classifications."""

    SLIM = "slim"
    AVERAGE = "average"
    MUSCULAR = "muscular"
    OVERWEIGHT = "overweight"
    OBESE = "obese"


def _positive_finite_number(name: str, value: float) -> float:
    # bool is an int subclass, but is never a useful physical measurement.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number (int or float)")
    try:
        normalized = float(value)
    except OverflowError:
        raise ValueError(f"{name} must be positive and finite") from None
    if not isfinite(normalized) or normalized <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return normalized


@dataclass(frozen=True)
class HumanoidSpec:
    """Immutable input contract using centimeters and kilograms.

    Body type is explicitly selected by the artist, never inferred from weight.
    This contract checks input validity, not anatomical plausibility. Supported
    generation ranges belong to the future generator, not this input contract.
    """

    height_cm: float
    weight_kg: float
    body_type: BodyType

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "height_cm", _positive_finite_number("height_cm", self.height_cm)
        )
        object.__setattr__(
            self, "weight_kg", _positive_finite_number("weight_kg", self.weight_kg)
        )
        if not isinstance(self.body_type, BodyType):
            raise TypeError("body_type must be a BodyType enum member")
