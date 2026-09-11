# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent Avian provider foundation."""

from math import isfinite

from ..models import MeshPart, ObjectMesh
from .base import Parameter


AVIAN_PARAMETERS = (
    Parameter("body_length_cm", "Body Length (cm)", 42, 12, 140),
    Parameter("body_width_cm", "Body Width (cm)", 16, 5, 60),
    Parameter("body_height_cm", "Body Height (cm)", 20, 6, 70),
    Parameter("wingspan_cm", "Wingspan (cm)", 90, 20, 320),
    Parameter("tail_length_cm", "Tail Length (cm)", 22, 4, 100),
)


def _dimensions(parameters, values):
    dimensions = {}
    for field in parameters:
        value = values[field.key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(field.label + " must be a number")
        if not isfinite(value) or not field.minimum <= value <= field.maximum:
            raise ValueError(field.label + " is outside its supported range")
        dimensions[field.key] = float(value)
    if dimensions["wingspan_cm"] <= dimensions["body_width_cm"]:
        raise ValueError("Wingspan must be wider than the body")
    return dimensions


def _box(name, x0, x1, y0, y1, z0, z1):
    vertices = (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    )
    faces = (
        (3, 2, 1, 0), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    )
    return MeshPart(name, vertices, faces)


def _wing(name, side, body_width, wingspan, body_length, body_height):
    root_x = side * body_width * 0.42
    tip_x = side * wingspan * 0.5
    front_y = body_length * 0.18
    rear_y = -body_length * 0.24
    z = body_height * 0.58
    thickness = max(body_height * 0.08, 0.5)
    vertices = (
        (root_x, front_y, z),
        (root_x, rear_y, z),
        (tip_x, -body_length * 0.08, z - body_height * 0.08),
        (root_x, front_y, z + thickness),
        (root_x, rear_y, z + thickness),
        (tip_x, -body_length * 0.08, z - body_height * 0.08 + thickness),
    )
    faces = (
        (0, 2, 1), (3, 4, 5),
        (0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 4, 3),
    )
    return MeshPart(name, vertices, faces)


def _tail(body_width, body_length, body_height, tail_length):
    rear_y = -body_length * 0.5
    tip_y = rear_y - tail_length
    z = body_height * 0.42
    half_width = body_width * 0.30
    thickness = max(body_height * 0.07, 0.4)
    vertices = (
        (-half_width, rear_y, z),
        (half_width, rear_y, z),
        (0, tip_y, z - body_height * 0.08),
        (-half_width, rear_y, z + thickness),
        (half_width, rear_y, z + thickness),
        (0, tip_y, z - body_height * 0.08 + thickness),
    )
    faces = (
        (0, 2, 1), (3, 4, 5),
        (0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 4, 3),
    )
    return MeshPart("avian.tail", vertices, faces)


def generate_avian_blockout(dimensions):
    """Return a deterministic editable multipart Avian blockout."""
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    wingspan = dimensions["wingspan_cm"]
    tail = dimensions["tail_length_cm"]

    body = _box(
        "avian.body",
        -width * 0.5, width * 0.5,
        -length * 0.5, length * 0.5,
        0, height,
    )
    head_size = min(width * 0.72, height * 0.72, length * 0.30)
    head = _box(
        "avian.head",
        -head_size * 0.5, head_size * 0.5,
        length * 0.5, length * 0.5 + head_size,
        height * 0.46, height * 0.46 + head_size,
    )
    return ObjectMesh((
        body,
        head,
        _wing("avian.wing.left", 1, width, wingspan, length, height),
        _wing("avian.wing.right", -1, width, wingspan, length, height),
        _tail(width, length, height, tail),
    ))


class AvianProvider:
    """Editable Avian blockout provider; rigging and flight follow in later milestones."""

    key, label = "avian", "Avian"
    supports_rig = supports_idle = uses_skin_weights = supports_materials = False
    supports_locomotion = supports_run = False
    parameters = AVIAN_PARAMETERS

    def dimensions(self, values):
        return _dimensions(self.parameters, values)

    def mesh(self, values):
        return generate_avian_blockout(self.dimensions(values))
