# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable in-place Human run-cycle generation."""

from dataclasses import dataclass
from math import isfinite, radians
from typing import Tuple

from .idle import RotationTrack


@dataclass(frozen=True)
class RunClip:
    duration: float
    tracks: Tuple[RotationTrack, ...]


def _keys(duration, degrees, strength):
    quarter = duration / 4
    return tuple(
        (time, radians(angle) * strength)
        for time, angle in (
            (0.0, degrees),
            (quarter, 0.0),
            (2 * quarter, -degrees),
            (3 * quarter, 0.0),
            (duration, degrees),
        )
    )


def _pose_keys(duration, degrees, strength):
    """Sample an asymmetric closed joint arc for joints that stay flexed while running."""
    quarter = duration / 4
    return tuple(
        (time, radians(angle) * strength)
        for time, angle in zip(
            (0.0, quarter, 2 * quarter, 3 * quarter, duration),
            degrees,
        )
    )


def generate_run(duration=0.72, strength=1.0):
    """Return a closed in-place run cycle with a visibly different running silhouette."""
    for name, value, lower, upper in (("duration", duration, 0.35, 2.0), ("strength", strength, 0.1, 2.0)):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise TypeError(name + " must be a number")
        if not isfinite(value) or not lower <= value <= upper:
            raise ValueError(name + " must be between " + str(lower) + " and " + str(upper))

    tracks = (
        RotationTrack("upper_leg.left", (1.0, 0.0, 0.0), _keys(duration, 48.0, strength)),
        RotationTrack("upper_leg.right", (1.0, 0.0, 0.0), _keys(duration, -48.0, strength)),
        RotationTrack("lower_leg.left", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-28.0, -72.0, -42.0, -88.0, -28.0), strength)),
        RotationTrack("lower_leg.right", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (42.0, 88.0, 28.0, 72.0, 42.0), strength)),
        RotationTrack("upper_arm.left", (1.0, 0.0, 0.0), _keys(duration, -42.0, strength)),
        RotationTrack("upper_arm.right", (1.0, 0.0, 0.0), _keys(duration, 42.0, strength)),
        RotationTrack("forearm.left", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-62.0, -92.0, -70.0, -102.0, -62.0), strength)),
        RotationTrack("forearm.right", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (70.0, 102.0, 62.0, 92.0, 70.0), strength)),
        RotationTrack("torso", (0.0, 0.0, 1.0), _keys(duration, 7.0, strength)),
    )
    return RunClip(float(duration), tracks)
