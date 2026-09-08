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


def _side_face_index(level, segment):
    """Face index for one side quad in the standard 8-sided vertical loft."""
    return 1 + level * RING_SIDES + segment


def _append_branch(vertices, faces, root, centers, widths, depths):
    """Stitch a 4-edge torso opening into an 8-sided deformable chain.

    ``root`` contains the four existing torso vertex indices in the same
    winding as the removed torso quad. The transition reuses those vertices,
    so the branch shares topology with the torso instead of overlapping it.
    """
    if len(root) != 4:
        raise ValueError("branch root must contain four torso vertices")
    if not (len(centers) == len(widths) == len(depths)) or len(centers) < 2:
        raise ValueError("branch inputs must have equal lengths of at least two")

    rings = []
    for index, center in enumerate(centers):
        if index == 0:
            tangent = _subtract(centers[1], center)
        elif index == len(centers) - 1:
            tangent = _subtract(center, centers[index - 1])
        else:
            tangent = _subtract(centers[index + 1], centers[index - 1])
        ring = _ring(center, widths[index], depths[index], tangent)
        start = len(vertices)
        vertices.extend(ring)
        rings.append(tuple(range(start, start + RING_SIDES)))

    first = rings[0]
    for index in range(4):
        root_start = root[index]
        root_end = root[(index + 1) % 4]
        ring_start = first[(2 * index) % RING_SIDES]
        ring_mid = first[(2 * index + 1) % RING_SIDES]
        ring_end = first[(2 * index + 2) % RING_SIDES]
        faces.append((root_start, root_end, ring_end))
        faces.append((root_start, ring_end, ring_mid, ring_start))

    for level in range(len(rings) - 1):
        lower = rings[level]
        upper = rings[level + 1]
        for index in range(RING_SIDES):
            nxt = (index + 1) % RING_SIDES
            faces.append((lower[index], lower[nxt], upper[nxt], upper[index]))

    faces.append(tuple(rings[-1]))


def generate_deformable_mesh(proportions: HumanoidProportions) -> ObjectMesh:
    """Return one connected Human 1.0 deformation-oriented surface.

    Shoulder and hip roots are stitched into explicit torso openings. Neck,
    shoulders, elbows, wrists, knees, ankles, and foot bends retain support
    loops so skinning has enough local geometry to distribute motion. Hands
    and feet use simple multi-ring silhouettes suitable for first-pass artist
    refinement rather than ending as featureless limb caps.
    """
    if not isinstance(proportions, HumanoidProportions):
        raise TypeError("proportions must be HumanoidProportions")
    p = proportions
    points = generate_landmarks(p)
    hip_z = points["hip_center"][2]
    shoulder_z = points["shoulder_center"][2]
    chin_z = points["chin"][2]
    crown_z = points["crown"][2]
    neck_length = chin_z - shoulder_z

    body = vertical_loft(
        "human",
        (
            (hip_z, p.hip_width_cm, p.hip_depth_cm),
            (hip_z + p.torso_length_cm * 0.35, p.waist_width_cm, p.waist_depth_cm),
            (hip_z + p.torso_length_cm * 0.78, p.chest_width_cm, p.chest_depth_cm),
            (shoulder_z, p.shoulder_width_cm, p.chest_depth_cm * 0.8),
            (shoulder_z + neck_length * 0.18, p.neck_width_cm * 1.08, p.neck_width_cm * 1.08),
            (shoulder_z + neck_length * 0.38, p.neck_width_cm, p.neck_width_cm),
            (shoulder_z + neck_length * 0.62, p.neck_width_cm * 0.96, p.neck_width_cm * 0.96),
            (shoulder_z + neck_length * 0.82, p.neck_width_cm * 0.92, p.neck_width_cm * 0.92),
            (chin_z, p.neck_width_cm * 0.9, p.neck_width_cm * 0.9),
            (chin_z + p.head_height_cm * 0.3, p.head_width_cm, p.head_depth_cm),
            (chin_z + p.head_height_cm * 0.8, p.head_width_cm, p.head_depth_cm),
            (crown_z, p.head_width_cm * 0.7, p.head_depth_cm * 0.7),
        ),
    )

    vertices = list(body.vertices)
    body_faces = list(body.faces)

    openings = {
        ("hip", "left"): body_faces[_side_face_index(0, 0)],
        ("hip", "right"): body_faces[_side_face_index(0, 3)],
        ("shoulder", "left"): body_faces[_side_face_index(2, 0)],
        ("shoulder", "right"): body_faces[_side_face_index(2, 3)],
    }
    removed = {
        _side_face_index(0, 0),
        _side_face_index(0, 3),
        _side_face_index(2, 0),
        _side_face_index(2, 3),
    }
    faces = [face for index, face in enumerate(body_faces) if index not in removed]

    for side in ("left", "right"):
        shoulder = points["shoulder." + side]
        elbow = points["elbow." + side]
        wrist = points["wrist." + side]
        fingertips = points["fingertips." + side]
        shoulder_exit = _lerp_point(shoulder, elbow, 0.12)
        palm = _lerp_point(wrist, fingertips, 0.42)
        knuckles = _lerp_point(wrist, fingertips, 0.72)
        hand_width = p.forearm_thickness_cm * 0.92
        hand_depth = p.forearm_thickness_cm * 0.40
        arm_centers, arm_widths, arm_depths = _supported_joint_chain(
            (shoulder, shoulder_exit, elbow, wrist, palm, knuckles, fingertips),
            (p.upper_arm_thickness_cm * 1.05, p.upper_arm_thickness_cm,
             p.upper_arm_thickness_cm * 0.82, p.forearm_thickness_cm * 0.72,
             hand_width, hand_width * 0.94, hand_width * 0.48),
            (p.upper_arm_thickness_cm * 1.05, p.upper_arm_thickness_cm,
             p.upper_arm_thickness_cm * 0.82, p.forearm_thickness_cm * 0.72,
             hand_depth, hand_depth * 0.88, hand_depth * 0.54),
        )
        _append_branch(
            vertices,
            faces,
            openings[("shoulder", side)],
            arm_centers,
            arm_widths,
            arm_depths,
        )

        hip = points["hip." + side]
        knee = points["knee." + side]
        ankle = points["ankle." + side]
        hip_exit = _lerp_point(hip, knee, 0.10)
        foot_height = p.foot_height_cm
        foot_center_z = foot_height * 0.5
        heel = (ankle[0], -p.foot_length_cm * 0.18, foot_center_z)
        midfoot = (ankle[0], p.foot_length_cm * 0.22, foot_center_z)
        ball = (ankle[0], p.foot_length_cm * 0.56, foot_center_z)
        toe = (ankle[0], p.foot_length_cm * 0.82, foot_center_z)
        foot_width = p.calf_thickness_cm * 0.88
        leg_centers, leg_widths, leg_depths = _supported_joint_chain(
            (hip_exit, knee, ankle, heel, midfoot, ball, toe),
            (p.thigh_thickness_cm, p.calf_thickness_cm,
             p.calf_thickness_cm * 0.6, foot_width * 0.82,
             foot_width, foot_width * 1.06, foot_width * 0.74),
            (p.thigh_thickness_cm, p.calf_thickness_cm,
             p.calf_thickness_cm * 0.6, foot_height * 0.92,
             foot_height, foot_height * 0.82, foot_height * 0.56),
        )
        _append_branch(
            vertices,
            faces,
            openings[("hip", side)],
            leg_centers,
            leg_widths,
            leg_depths,
        )

    return ObjectMesh((MeshPart("human", tuple(vertices), tuple(faces)),))
