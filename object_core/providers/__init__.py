# SPDX-License-Identifier: GPL-3.0-or-later
"""Provider implementations kept separate from the shared registry."""

from .base import Parameter
from .box import BoxProvider
from .dog import DOG_PARAMETERS, DogProvider
from .human import HUMAN_PARAMETERS, HumanExperimentalProvider, HumanoidProvider

__all__ = [
    "Parameter",
    "BoxProvider",
    "DOG_PARAMETERS",
    "DogProvider",
    "HUMAN_PARAMETERS",
    "HumanoidProvider",
    "HumanExperimentalProvider",
]
