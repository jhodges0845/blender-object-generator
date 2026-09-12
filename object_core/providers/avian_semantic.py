# SPDX-License-Identifier: GPL-3.0-or-later
"""Provider-owned semantic geometry transforms for Avian Modify.

These transforms deliberately live beside the Avian provider.  Shared Modify
code only carries and validates portable operations; it never learns what an
avian beak, wing, chest, tail, leg, or foot means.
"""

from math import isfinite

from ..models import MeshPart, ObjectMesh


_SHAPE_ARGUMENTS = {
    "body": {"width_factor", "depth_factor", "length_factor"},
    "chest": {"width_factor", "depth_factor", "forward_factor"},
    "head": {"width_factor", "depth_factor", "length_factor"},
    "beak": {"length_factor", "width_factor", "depth_factor", "hook"},
    "wing.left": {"length_factor", "chord_factor", "sweep"},
    "wing.right": {"length_factor", "chord_factor", "sweep"},
    "tail": {"length_factor", "fan_factor", "lift"},
    "leg.left": {"length_factor", "thickness_factor"},
    "leg.right": {"length_factor", "thickness_factor"},
    "foot.left": {"length_factor", "width_factor"},
    "foot.right": {"length_factor", "width_factor"},
}


def _number(value, label, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(label + " must be a number")
    result = float(value)
    if not isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(label + " must be between " + str(minimum) + " and " + str(maximum))
    return result


def validate_avian_semantic_operation(operation):
    """Validate Avian-specific arguments without exposing them to shared code."""
    args = operation.argument_values()
    if operation.operation == "scale":
        allowed = {"factor", "x", "y", "z"}
        unknown = set(args) - allowed
        if unknown:
            raise ValueError("Unsupported Avian scale argument: " + sorted(unknown)[0])
        if not args:
            raise ValueError("Avian scale requires factor or axis scale arguments")
        for key, value in args.items():
            _number(value, operation.target + "." + key, 0.25, 4.0)
        return

    if operation.operation != "shape":
        raise ValueError("Avian semantic apply currently supports shape and scale operations")
    allowed = _SHAPE_ARGUMENTS.get(operation.target)
    if allowed is None:
        raise ValueError("Avian shape is not implemented for semantic target " + operation.target)
    unknown = set(args) - allowed
    if unknown:
        raise ValueError("Unsupported " + operation.target + " shape argument: " + sorted(unknown)[0])
    if not args:
        raise ValueError(operation.target + " shape requires at least one argument")
    for key, value in args.items():
        if key in ("hook",):
            _number(value, operation.target + "." + key, 0.0, 1.5)
        elif key in ("sweep", "lift", "forward_factor"):
            _number(value, operation.target + "." + key, -1.5, 1.5)
        else:
            _number(value, operation.target + "." + key, 0.25, 4.0)


def _factor(args, key, default=1.0):
    return float(args.get(key, default))


def _scale_vertex(vertex, anchor, factors):
    return tuple(anchor[i] + (vertex[i] - anchor[i]) * factors[i] for i in range(3))


def _is_target(vertex, target, dimensions):
    x, y, z = vertex
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    body_z = height * 0.52
    side = -1.0 if target.endswith(".left") else 1.0

    if target == "body":
        return abs(x) <= width * 0.55 and -length * 0.46 <= y <= length * 0.48
    if target == "chest":
        return abs(x) <= width * 0.60 and length * 0.08 <= y <= length * 0.42 and z >= body_z - height * 0.30
    if target == "head":
        return abs(x) <= width * 0.55 and length * 0.47 <= y <= length * 0.70
    if target == "beak":
        return y > length * 0.68
    if target.startswith("wing."):
        return x * side > width * 0.48 and z > body_z - height * 0.20
    if target == "tail":
        return y < -length * 0.47
    if target.startswith("leg."):
        return x * side > 0 and abs(x) < width * 0.60 and z < body_z - height * 0.14 and y < length * 0.14
    if target.startswith("foot."):
        return x * side > 0 and z < height * 0.13 and y > -length * 0.08
    return False


def _anchor(target, dimensions):
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    body_z = height * 0.52
    sign = -1.0 if target.endswith(".left") else 1.0
    anchors = {
        "body": (0.0, 0.0, body_z),
        "chest": (0.0, length * 0.26, body_z + height * 0.06),
        "head": (0.0, length * 0.58, body_z + height * 0.27),
        "beak": (0.0, length * 0.64, body_z + height * 0.29),
        "tail": (0.0, -length * 0.48, body_z),
        "wing.left": (sign * width * 0.36, length * 0.08, body_z + height * 0.14),
        "wing.right": (sign * width * 0.36, length * 0.08, body_z + height * 0.14),
        "leg.left": (sign * width * 0.25, -length * 0.04, body_z - height * 0.26),
        "leg.right": (sign * width * 0.25, -length * 0.04, body_z - height * 0.26),
        "foot.left": (sign * width * 0.25, length * 0.01, height * 0.08),
        "foot.right": (sign * width * 0.25, length * 0.01, height * 0.08),
    }
    return anchors[target]


def _apply_scale(vertex, target, args, dimensions):
    factor = _factor(args, "factor")
    factors = (
        factor * _factor(args, "x"),
        factor * _factor(args, "y"),
        factor * _factor(args, "z"),
    )
    return _scale_vertex(vertex, _anchor(target, dimensions), factors)


def _apply_shape(vertex, target, args, dimensions):
    x, y, z = vertex
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    anchor = _anchor(target, dimensions)

    if target in ("body", "head"):
        return _scale_vertex(vertex, anchor, (
            _factor(args, "width_factor"),
            _factor(args, "length_factor"),
            _factor(args, "depth_factor"),
        ))
    if target == "chest":
        shaped = _scale_vertex(vertex, anchor, (
            _factor(args, "width_factor"), 1.0, _factor(args, "depth_factor")
        ))
        return (shaped[0], shaped[1] + length * 0.06 * float(args.get("forward_factor", 0.0)), shaped[2])
    if target == "beak":
        shaped = _scale_vertex(vertex, anchor, (
            _factor(args, "width_factor"),
            _factor(args, "length_factor"),
            _factor(args, "depth_factor"),
        ))
        forward = max(0.0, shaped[1] - anchor[1]) / max(length * 0.18, 1e-9)
        return (shaped[0], shaped[1], shaped[2] - height * 0.16 * float(args.get("hook", 0.0)) * forward * forward)
    if target.startswith("wing."):
        sign = -1.0 if target.endswith(".left") else 1.0
        distance = max(0.0, (x - anchor[0]) * sign)
        length_factor = _factor(args, "length_factor")
        chord = _factor(args, "chord_factor")
        new_x = anchor[0] + (x - anchor[0]) * length_factor
        new_y = anchor[1] + (y - anchor[1]) * chord - distance * float(args.get("sweep", 0.0)) * 0.25
        new_z = anchor[2] + (z - anchor[2]) * chord
        return (new_x, new_y, new_z)
    if target == "tail":
        distance = max(0.0, anchor[1] - y)
        return (
            x * _factor(args, "fan_factor"),
            anchor[1] + (y - anchor[1]) * _factor(args, "length_factor"),
            z + distance * float(args.get("lift", 0.0)) * 0.25,
        )
    if target.startswith("leg."):
        shaped = _scale_vertex(vertex, anchor, (
            _factor(args, "thickness_factor"), 1.0, _factor(args, "length_factor")
        ))
        return shaped
    if target.startswith("foot."):
        return _scale_vertex(vertex, anchor, (
            _factor(args, "width_factor"), _factor(args, "length_factor"), 1.0
        ))
    return vertex


def apply_avian_semantics(mesh, operations, dimensions):
    """Return a new immutable mesh with the semantic operation stack applied."""
    if not operations:
        return mesh
    parts = []
    for part in mesh.parts:
        vertices = list(part.vertices)
        for operation in operations:
            validate_avian_semantic_operation(operation)
            args = operation.argument_values()
            updated = []
            for vertex in vertices:
                if not _is_target(vertex, operation.target, dimensions):
                    updated.append(vertex)
                elif operation.operation == "scale":
                    updated.append(_apply_scale(vertex, operation.target, args, dimensions))
                else:
                    updated.append(_apply_shape(vertex, operation.target, args, dimensions))
            vertices = updated
        parts.append(MeshPart(part.name, tuple(vertices), part.faces, part.uvs))
    return ObjectMesh(tuple(parts))
