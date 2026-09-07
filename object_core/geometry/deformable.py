# SPDX-License-Identifier: GPL-3.0-or-later
"""Human 1.0 deformation-oriented geometry foundation.

This module intentionally lives beside the legacy rigid blockout generator.
The rigid rig still depends on one mesh object per bound bone, so callers can
adopt this surface incrementally while skinning support is developed.
"""

from math import cos, sqrt, pi, sin

from ..models import HumanoidProportions
from ..models.mesh import MeshPart, ObjectMesh
from ..proportions.landmarks import generate_landmarks
from .primitives import RING_SIDES, vertical_loft


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normalize(vector):
    length = sqrt(sum(component * component for component in vector))
    if length == 0:
        raise ValueError("ring tangent must have nonzero length")
    return tuple(component / length for component in vector)


def _ring(center, width, depth, tangent=(0.0, 0.0, 1.0)):
    """Return an elliptical ring normal to an arbitrary 3D tangent."""
    tangent = _normalize(tangent)
    # Prefer world Y as the depth reference for upright limbs. Near a foot's
    # Y-aligned direction use Z instead, avoiding a degenerate cross product.
    reference = (0.0, 1.0, 0.0)
    if abs(sum(tangent[i] * reference[i] for i in range(3))) > 0.95:
        reference = (0.0, 0.0, 1.0)
    width_axis = _normalize(_cross(reference, tangent))
    depth_axis = _normalize(_cross(tangent, width_axis))
    return tuple(
        tuple(
            center[axis]
            + width_axis[axis] * width * 0.5 * cos(2 * pi * i / RING_SIDES)
            + depth_axis[axis] * depth * 0.5 * sin(2 * pi * i / RING_SIDES)
            for axis in range(3)
        )
        for i in range(RING_SIDES)
    )


def _lerp_point(a, b, amount):
    return tuple(a[i] + (b[i] - a[i]) * amount for i in range(3))


def _supported_joint_chain(points, widths, depths, support=0.14):
    """Add rings immediately before/after internal joints for deformation."""
    centers = [points[0]]
    out_widths = [widths[0]]
    out_depths = [depths[0]]
    for index in range(1, len(points) - 1):
        joint = points[index]
        centers.extend(
            (
                _lerp_point(joint, points[index - 1], support),
                joint,
                _lerp_point(joint, points[index + 1], support),
            )
        )
        out_widths.extend((widths[index], widths[index], widths[index]))
        out_depths.extend((depths[index], depths[index], depths[index]))
    centers.append(points[-1])
    out_widths.append(widths[-1])
    out_depths.append(depths[-1])
    return tuple(centers), tuple(out_widths), tuple(out_depths)


def _subtract(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _chain(name, centers, widths, depths):
    """Build one capped quad surface through all supplied joint centers."""
    if not (len(centers) == len(widths) == len(depths)) or len(centers) < 2:
        raise ValueError("chain inputs must have equal lengths of at least two")
    rings = []
    for index, center in enumerate(centers):
        if index == 0:
            tangent = _subtract(centers[1], center)
        elif index == len(centers) - 1:
            tangent = _subtract(center, centers[index - 1])
        else:
            tangent = _subtract(centers[index + 1], centers[index - 1])
        rings.append(_ring(center, widths[index], depths[index], tangent))

    vertices = tuple(vertex for ring in rings for vertex in ring)
    faces = [tuple(reversed(range(RING_SIDES)))]
    for level in range(len(rings) - 1):
        lower = level * RING_SIDES
        upper = lower + RING_SIDES
        for index in range(RING_SIDES):
            nxt = (index + 1) % RING_SIDES
            faces.append((lower + index, lower + nxt, upper + nxt, upper + index))
    faces.append(tuple(range(len(vertices) - RING_SIDES, len(vertices))))
    return MeshPart(name, vertices, tuple(faces))


def generate_deformable_mesh(proportions: HumanoidProportions) -> ObjectMesh:
    """Return the Human 1.0 deformation-oriented surface in progress.

    The torso/neck/head is continuous, arms have support loops around elbow and
    wrist deformation zones, and each leg now continues through ankle into the
    foot. Arms and legs remain separate from the torso until the shoulder/hip
    branch topology can be welded without creating a non-manifold junction.

    The function is deliberately opt-in until the deforming rig replaces the
    legacy rigid part-binding contract.
    """
    if not isinstance(proportions, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    p = proportions
    points = generate_landmarks(p)
    hip_z = points["hip_center"][2]
    shoulder_z = points["shoulder_center"][2]
    chin_z = points["chin"][2]
    crown_z = points["crown"][2]

    body = vertical_loft(
        "body",
        (
            (hip_z, p.hip_width_cm, p.hip_depth_cm),
            (hip_z + p.torso_length_cm * 0.35, p.waist_width_cm, p.waist_depth_cm),
            (hip_z + p.torso_length_cm * 0.78, p.chest_width_cm, p.chest_depth_cm),
            (shoulder_z, p.shoulder_width_cm, p.chest_depth_cm * 0.8),
            (shoulder_z + (chin_z - shoulder_z) * 0.35, p.neck_width_cm, p.neck_width_cm),
            (chin_z, p.neck_width_cm * 0.9, p.neck_width_cm * 0.9),
            (chin_z + p.head_height_cm * 0.3, p.head_width_cm, p.head_depth_cm),
            (chin_z + p.head_height_cm * 0.8, p.head_width_cm, p.head_depth_cm),
            (crown_z, p.head_width_cm * 0.7, p.head_depth_cm * 0.7),
        ),
    )
    parts = [body]

    for side in ("left", "right"):
        shoulder = points["shoulder." + side]
        elbow = points["elbow." + side]
        wrist = points["wrist." + side]
        fingertips = points["fingertips." + side]
        arm_centers, arm_widths, arm_depths = _supported_joint_chain(
            (shoulder, elbow, wrist, fingertips),
            (p.upper_arm_thickness_cm, p.upper_arm_thickness_cm * 0.82,
             p.forearm_thickness_cm * 0.72, p.forearm_thickness_cm * 0.52),
            (p.upper_arm_thickness_cm, p.upper_arm_thickness_cm * 0.82,
             p.forearm_thickness_cm * 0.72, p.forearm_thickness_cm * 0.30),
        )
        parts.append(_chain("arm." + side, arm_centers, arm_widths, arm_depths))

        hip = points["hip." + side]
        knee = points["knee." + side]
        ankle = points["ankle." + side]
        foot_back = (ankle[0], -p.foot_length_cm * 0.18, 0.0)
        foot_front = (ankle[0], p.foot_length_cm * 0.72, 0.0)
        leg_centers, leg_widths, leg_depths = _supported_joint_chain(
            (hip, knee, ankle, foot_back, foot_front),
            (p.thigh_thickness_cm, p.calf_thickness_cm,
             p.calf_thickness_cm * 0.6, p.calf_thickness_cm * 0.72,
             p.calf_thickness_cm * 0.62),
            (p.thigh_thickness_cm, p.calf_thickness_cm,
             p.calf_thickness_cm * 0.6, p.foot_length_cm * 0.34,
             p.foot_length_cm * 0.18),
        )
        parts.append(_chain("leg." + side, leg_centers, leg_widths, leg_depths))

    return ObjectMesh(tuple(parts))
