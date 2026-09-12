# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent animation identity, ownership, and compatibility contracts."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Mapping, Optional


class AnimationSource(str, Enum):
    GENERATED = "generated"
    IMPORTED = "imported"
    ARTIST = "artist"


class RootMotionIntent(str, Enum):
    NONE = "none"
    IN_PLACE = "in_place"
    ROOT = "root"


@dataclass(frozen=True)
class AnimationRecord:
    animation_id: str
    display_name: str
    export_name: str
    source: AnimationSource
    rig_signature: str
    frame_start: float
    frame_end: float
    fps: float
    looping: bool = False
    root_motion: RootMotionIntent = RootMotionIntent.NONE
    owns_curves: bool = False
    source_reference: Optional[str] = None
    provider_key: Optional[str] = None
    capability: Optional[str] = None


def _text(value, field, *, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + " must be a nonempty string")
    return value.strip()


def _finite_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(field + " must be a finite numeric value")
    return value


def validate_animation(record):
    """Validate one portable animation record without host-specific assumptions."""
    if not isinstance(record, AnimationRecord):
        raise TypeError("record must be an AnimationRecord")
    _text(record.animation_id, "animation_id")
    _text(record.display_name, "display_name")
    _text(record.export_name, "export_name")
    _text(record.rig_signature, "rig_signature")
    _text(record.source_reference, "source_reference", optional=True)
    _text(record.provider_key, "provider_key", optional=True)
    _text(record.capability, "capability", optional=True)
    if not isinstance(record.source, AnimationSource):
        raise ValueError("source must be an AnimationSource")
    if not isinstance(record.root_motion, RootMotionIntent):
        raise ValueError("root_motion must be a RootMotionIntent")
    _finite_number(record.frame_start, "frame_start")
    _finite_number(record.frame_end, "frame_end")
    if record.frame_end < record.frame_start:
        raise ValueError("frame_end must be greater than or equal to frame_start")
    _finite_number(record.fps, "fps")
    if record.fps <= 0:
        raise ValueError("fps must be greater than zero")
    if not isinstance(record.looping, bool):
        raise ValueError("looping must be a boolean")
    if not isinstance(record.owns_curves, bool):
        raise ValueError("owns_curves must be a boolean")
    if record.source == AnimationSource.GENERATED and not record.owns_curves:
        raise ValueError("generated animation records must own their curves")
    return record


def animation_document(record):
    """Return the JSON-safe portable document for one validated animation."""
    validate_animation(record)
    document = {
        "animation_id": record.animation_id.strip(),
        "display_name": record.display_name.strip(),
        "export_name": record.export_name.strip(),
        "source": record.source.value,
        "rig_signature": record.rig_signature.strip(),
        "frame_start": float(record.frame_start),
        "frame_end": float(record.frame_end),
        "fps": float(record.fps),
        "looping": record.looping,
        "root_motion": record.root_motion.value,
        "owns_curves": record.owns_curves,
    }
    for key, value in (
        ("source_reference", record.source_reference),
        ("provider_key", record.provider_key),
        ("capability", record.capability),
    ):
        if value is not None:
            document[key] = value.strip()
    return document


def animation_from_document(document):
    """Parse and strictly validate one portable animation document."""
    if not isinstance(document, Mapping):
        raise TypeError("animation document must be a mapping")
    allowed = {
        "animation_id", "display_name", "export_name", "source", "rig_signature",
        "frame_start", "frame_end", "fps", "looping", "root_motion", "owns_curves",
        "source_reference", "provider_key", "capability",
    }
    unknown = set(document) - allowed
    if unknown:
        raise ValueError("unknown animation fields: " + ", ".join(sorted(unknown)))
    required = {
        "animation_id", "display_name", "export_name", "source", "rig_signature",
        "frame_start", "frame_end", "fps", "looping", "root_motion", "owns_curves",
    }
    missing = required - set(document)
    if missing:
        raise ValueError("missing animation fields: " + ", ".join(sorted(missing)))
    try:
        source = AnimationSource(document["source"])
    except (TypeError, ValueError):
        raise ValueError("unknown animation source") from None
    try:
        root_motion = RootMotionIntent(document["root_motion"])
    except (TypeError, ValueError):
        raise ValueError("unknown root motion intent") from None
    record = AnimationRecord(
        animation_id=document["animation_id"],
        display_name=document["display_name"],
        export_name=document["export_name"],
        source=source,
        rig_signature=document["rig_signature"],
        frame_start=document["frame_start"],
        frame_end=document["frame_end"],
        fps=document["fps"],
        looping=document["looping"],
        root_motion=root_motion,
        owns_curves=document["owns_curves"],
        source_reference=document.get("source_reference"),
        provider_key=document.get("provider_key"),
        capability=document.get("capability"),
    )
    return validate_animation(record)


__all__ = [
    "AnimationRecord",
    "AnimationSource",
    "RootMotionIntent",
    "animation_document",
    "animation_from_document",
    "validate_animation",
]
