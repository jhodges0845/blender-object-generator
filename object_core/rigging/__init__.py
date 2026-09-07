# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent skeleton and skin-weight generation."""

from .generator import generate_skeleton
from .deforming import generate_deforming_skeleton, generate_skin_weights

__all__ = ["generate_skeleton", "generate_deforming_skeleton", "generate_skin_weights"]
