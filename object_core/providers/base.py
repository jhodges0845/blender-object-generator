# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared provider contracts with no host or asset-family dependencies."""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    default: Union[float, str]
    minimum: float
    maximum: float
    choices: tuple = ()
