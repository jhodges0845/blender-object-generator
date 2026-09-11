# SPDX-License-Identifier: GPL-3.0-or-later
"""Provider implementations kept separate from the shared registry."""

from .avian import AVIAN_PARAMETERS, AvianProvider
from .base import Parameter
from .box import BoxProvider
from .human import HUMAN_PARAMETERS, HumanExperimentalProvider, HumanoidProvider
from .quadruped import QUADRUPED_PARAMETERS, QuadrupedProvider

__all__ = [
    "Parameter",
    "AVIAN_PARAMETERS",
    "AvianProvider",
    "BoxProvider",
    "QUADRUPED_PARAMETERS",
    "QuadrupedProvider",
    "HUMAN_PARAMETERS",
    "HumanoidProvider",
    "HumanExperimentalProvider",
]
