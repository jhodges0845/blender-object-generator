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
    """Sample a closed asymmetric joint arc for joints that remain flexed."""
    quarter = duration / 4
    return tuple(
        (time, radians(angle) * strength)
        for time, angle in zip(
            (0.0, quarter, 2 * quarter, 3 * quarter, duration),
            degrees,
        )
    )


def generate_run(duration=0.72, strength=1.0):
    """Return a closed in-place run cycle with anatomically consistent joint flexion.

    Hip and shoulder swing alternate across the body. Knees and elbows, however,
    flex in the same anatomical direction on both sides and are phase-shifted rather
    than mirrored by sign. This avoids the bow-legged / backwards-joint silhouette
    that results from treating a run as a larger walk sine wave.
    """
    for name, value, lower, upper in (("duration", duration, 0.35, 2.0), ("strength", strength, 0.1, 2.0)):
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise TypeError(name + " must be a number")
        if not isfinite(value) or not lower <= value <= upper:
            raise ValueError(name + " must be between " + str(lower) + " and " + str(upper))

    tracks = (
        # Long opposing stride at the hips.
        RotationTrack("upper_leg.left", (1.0, 0.0, 0.0), _keys(duration, 44.0, strength)),
        RotationTrack("upper_leg.right", (1.0, 0.0, 0.0), _keys(duration, -44.0, strength)),

        # Both knees bend backwards anatomically; the right leg is half a cycle out
        # of phase with the left rather than bending in the opposite direction.
        RotationTrack("lower_leg.left", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-24.0, -78.0, -34.0, -96.0, -24.0), strength)),
        RotationTrack("lower_leg.right", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-34.0, -96.0, -24.0, -78.0, -34.0), strength)),

        # Strong opposing arm drive with elbows kept bent throughout the cycle.
        RotationTrack("upper_arm.left", (1.0, 0.0, 0.0), _keys(duration, -34.0, strength)),
        RotationTrack("upper_arm.right", (1.0, 0.0, 0.0), _keys(duration, 34.0, strength)),
        RotationTrack("forearm.left", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-68.0, -88.0, -72.0, -98.0, -68.0), strength)),
        RotationTrack("forearm.right", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (-72.0, -98.0, -68.0, -88.0, -72.0), strength)),

        # A small forward body pitch reads more like running than a large torso twist.
        RotationTrack("torso", (1.0, 0.0, 0.0),
                      _pose_keys(duration, (8.0, 10.0, 8.0, 10.0, 8.0), strength)),
    )
    return RunClip(float(duration), tracks)
