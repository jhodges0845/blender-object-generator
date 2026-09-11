# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable quadruped animation generation."""

from math import cos, isfinite, pi, radians

from ..animation import IdleClip, RotationTrack, RunClip, WalkClip


def _validate(duration, strength, duration_min, duration_max):
    for name, value, lower, upper in (
        ("duration", duration, duration_min, duration_max),
        ("strength", strength, 0.1, 2.0),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(name + " must be a number")
        if not isfinite(value) or not lower <= value <= upper:
            raise ValueError(name + " must be between " + str(lower) + " and " + str(upper))


def _closed_wave(duration, degrees, strength, samples=16, phase=0.0):
    return tuple(
        (
            duration * index / samples,
            radians(degrees) * strength * cos(2 * pi * index / samples + phase),
        )
        for index in range(samples + 1)
    )


def generate_quadruped_idle(duration=4.0, strength=1.0):
    """Return a subtle closed quadruped idle with breathing, head and tail motion."""
    _validate(duration, strength, 1.0, 20.0)
    tracks = (
        RotationTrack("spine", (1.0, 0.0, 0.0), _closed_wave(duration, 2.0, strength)),
        RotationTrack("neck", (1.0, 0.0, 0.0), _closed_wave(duration, 2.5, strength, phase=pi)),
        RotationTrack("head", (0.0, 0.0, 1.0), _closed_wave(duration, 2.0, strength, phase=pi / 2)),
        RotationTrack("tail.1", (0.0, 0.0, 1.0), _closed_wave(duration, 4.0, strength, phase=pi / 2)),
        RotationTrack("tail.2", (0.0, 0.0, 1.0), _closed_wave(duration, 6.0, strength, phase=pi)),
        RotationTrack("tail.3", (0.0, 0.0, 1.0), _closed_wave(duration, 8.0, strength, phase=3 * pi / 2)),
    )
    return IdleClip(float(duration), tracks)


def generate_quadruped_walk(duration=1.2, strength=1.0):
    """Return an in-place closed quadruped walk with diagonal gait timing."""
    _validate(duration, strength, 0.5, 4.0)
    tracks = []
    for bone, degrees, phase in (
        ("fore_upper.left", 24.0, 0.0),
        ("hind_upper.right", 22.0, 0.0),
        ("fore_upper.right", 24.0, pi),
        ("hind_upper.left", 22.0, pi),
        ("fore_lower.left", -12.0, pi / 2),
        ("hind_lower.right", -14.0, pi / 2),
        ("fore_lower.right", -12.0, 3 * pi / 2),
        ("hind_lower.left", -14.0, 3 * pi / 2),
    ):
        tracks.append(RotationTrack(bone, (1.0, 0.0, 0.0), _closed_wave(duration, degrees, strength, phase=phase)))
    tracks.extend((
        RotationTrack("spine", (0.0, 0.0, 1.0), _closed_wave(duration, 3.0, strength, phase=pi / 2)),
        RotationTrack("neck", (1.0, 0.0, 0.0), _closed_wave(duration, 2.0, strength, phase=pi)),
        RotationTrack("tail.1", (0.0, 0.0, 1.0), _closed_wave(duration, 7.0, strength, phase=pi)),
        RotationTrack("tail.2", (0.0, 0.0, 1.0), _closed_wave(duration, 10.0, strength, phase=3 * pi / 2)),
        RotationTrack("tail.3", (0.0, 0.0, 1.0), _closed_wave(duration, 12.0, strength, phase=0.0)),
    ))
    return WalkClip(float(duration), tuple(tracks))


def generate_quadruped_run(duration=0.64, strength=1.0):
    """Return an in-place closed faster quadruped run with stronger limb drive."""
    _validate(duration, strength, 0.3, 2.0)
    tracks = []
    for bone, degrees, phase in (
        ("fore_upper.left", 38.0, 0.0),
        ("fore_upper.right", 38.0, pi),
        ("hind_upper.left", 34.0, pi),
        ("hind_upper.right", 34.0, 0.0),
        ("fore_lower.left", -24.0, pi / 2),
        ("fore_lower.right", -24.0, 3 * pi / 2),
        ("hind_lower.left", -28.0, 3 * pi / 2),
        ("hind_lower.right", -28.0, pi / 2),
    ):
        tracks.append(RotationTrack(bone, (1.0, 0.0, 0.0), _closed_wave(duration, degrees, strength, phase=phase)))
    tracks.extend((
        RotationTrack("spine", (1.0, 0.0, 0.0), _closed_wave(duration, 7.0, strength, phase=pi / 2)),
        RotationTrack("neck", (1.0, 0.0, 0.0), _closed_wave(duration, 5.0, strength, phase=pi)),
        RotationTrack("tail.1", (0.0, 0.0, 1.0), _closed_wave(duration, 11.0, strength, phase=pi)),
        RotationTrack("tail.2", (0.0, 0.0, 1.0), _closed_wave(duration, 14.0, strength, phase=3 * pi / 2)),
        RotationTrack("tail.3", (0.0, 0.0, 1.0), _closed_wave(duration, 16.0, strength)),
    ))
    return RunClip(float(duration), tuple(tracks))
