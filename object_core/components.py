# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent contracts for attachable asset components.

Components such as hair, clothing, and accessories are separate owned assets.
They are not ordinary Human body semantics and may carry adapter-facing physics
intent without teaching the shared core about Blender, Godot, Unity, or Unreal.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ComponentKind(str, Enum):
    HAIR = "hair"
    CLOTHING = "clothing"
    ACCESSORY = "accessory"


class AttachmentMode(str, Enum):
    RIGID = "rigid"
    SKINNED = "skinned"


@dataclass(frozen=True)
class PhysicsIntent:
    """Portable dynamics intent; host adapters decide how or whether to realize it."""

    mode: str
    parameters: Tuple[Tuple[str, object], ...] = ()


@dataclass(frozen=True)
class ComponentRecord:
    """Persistent identity and ownership record for one attachable component."""

    component_id: str
    kind: ComponentKind
    provider_key: str
    attachment_target: str
    attachment_mode: AttachmentMode
    parameters: Tuple[Tuple[str, object], ...] = ()
    physics: Optional[PhysicsIntent] = None
    owns_geometry: bool = True
    owns_materials: bool = True
    owns_rig: bool = False


def _validate_pairs(label, pairs):
    if not isinstance(pairs, tuple):
        raise TypeError(label + " must be a tuple of key/value pairs")
    keys = set()
    for item in pairs:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TypeError(label + " must contain key/value pairs")
        key = item[0]
        if not isinstance(key, str) or not key.strip() or key in keys:
            raise ValueError(label + " keys must be nonempty and unique")
        keys.add(key)


def validate_component(record):
    """Validate persisted component metadata without depending on a host API."""
    if not isinstance(record, ComponentRecord):
        raise TypeError("component must be a ComponentRecord")
    for field in ("component_id", "provider_key", "attachment_target"):
        value = getattr(record, field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("component " + field + " must be a nonempty string")
    if not isinstance(record.kind, ComponentKind):
        raise TypeError("component kind must be a ComponentKind")
    if not isinstance(record.attachment_mode, AttachmentMode):
        raise TypeError("component attachment_mode must be an AttachmentMode")
    for field in ("owns_geometry", "owns_materials", "owns_rig"):
        if not isinstance(getattr(record, field), bool):
            raise TypeError("component " + field + " must be a boolean")
    if record.attachment_mode == AttachmentMode.SKINNED and not record.owns_rig:
        raise ValueError("skinned components must own or declare rig data")
    _validate_pairs("component parameters", record.parameters)
    if record.physics is not None:
        if not isinstance(record.physics, PhysicsIntent):
            raise TypeError("component physics must be PhysicsIntent or None")
        if not isinstance(record.physics.mode, str) or not record.physics.mode.strip():
            raise ValueError("physics mode must be a nonempty string")
        _validate_pairs("physics parameters", record.physics.parameters)
    return record


def component_document(record):
    """Return a portable persistence document for adapters and future Modify transport."""
    validate_component(record)
    return {
        "component_id": record.component_id,
        "kind": record.kind.value,
        "provider_key": record.provider_key,
        "attachment_target": record.attachment_target,
        "attachment_mode": record.attachment_mode.value,
        "parameters": dict(record.parameters),
        "physics": None if record.physics is None else {
            "mode": record.physics.mode,
            "parameters": dict(record.physics.parameters),
        },
        "ownership": {
            "geometry": record.owns_geometry,
            "materials": record.owns_materials,
            "rig": record.owns_rig,
        },
    }


__all__ = [
    "AttachmentMode",
    "ComponentKind",
    "ComponentRecord",
    "PhysicsIntent",
    "component_document",
    "validate_component",
]
