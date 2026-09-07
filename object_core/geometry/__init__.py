# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent mesh generation."""

from .deformable import generate_deformable_mesh
from .generator import generate_mesh

__all__ = ["generate_mesh", "generate_deformable_mesh"]
