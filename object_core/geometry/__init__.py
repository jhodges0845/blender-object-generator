# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent mesh generation."""

from .deformable import generate_deformable_mesh
from .generator import generate_mesh
from .topology import boundary_edges, edge_use_counts, is_closed_manifold, nonmanifold_edges

__all__ = [
    "generate_mesh",
    "generate_deformable_mesh",
    "edge_use_counts",
    "boundary_edges",
    "nonmanifold_edges",
    "is_closed_manifold",
]
