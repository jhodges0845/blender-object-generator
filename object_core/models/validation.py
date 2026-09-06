# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent observations and results for asset validation."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AssetSnapshot:
    mesh_count: int = 0
    invalid_meshes: Tuple[str, ...] = ()
    missing_materials: Tuple[str, ...] = ()
    missing_uvs: Tuple[str, ...] = ()
    missing_images: Tuple[str, ...] = ()
    texture_warnings: Tuple[str, ...] = ()
    texture_count: int = 0
    has_rig: bool = False
    rig_errors: Tuple[str, ...] = ()
    has_animation: bool = False
    animation_errors: Tuple[str, ...] = ()
    transform_warnings: Tuple[str, ...] = ()
    is_blockout: bool = True


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    status: str
    message: str
