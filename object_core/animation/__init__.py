# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent animation generation."""

from .idle import IdleClip, RotationTrack, generate_idle
from .walk import WalkClip, generate_walk
from .run import RunClip, generate_run
