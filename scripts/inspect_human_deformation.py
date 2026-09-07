# SPDX-License-Identifier: GPL-3.0-or-later
"""Build representative Human 1.0 poses for repeatable visual deformation review.

The script can be opened directly in Blender's Scripting workspace and run with
Run Script, or launched from the repository root with:

    blender --python scripts/inspect_human_deformation.py

The script leaves one neutral reference plus seven posed deforming Humans in a
compact 2x4 inspection grid. Each pose exercises a joint already protected by
Blender deformation regression tests; this harness is for the complementary
visual-quality review.
"""

import math
import sys
from pathlib import Path

import bpy


def _script_path():
    """Return the real path of this script in both CLI and Text Editor execution."""
    text = getattr(bpy.context.space_data, "text", None)
    if text is not None and text.filepath:
        return Path(bpy.path.abspath(text.filepath)).resolve()
    return Path(bpy.path.abspath(__file__)).resolve()


def _find_repo_root(start):
    """Walk upward so the helper does not depend on a particular checkout layout."""
    for candidate in (start.parent, *start.parents):
        if (candidate / "object_core").is_dir() and (candidate / "blender_adapter").is_dir():
            return candidate
    raise RuntimeError(
        "Could not locate the Asset Assistant repository root from "
        + str(start)
        + ". Open scripts/inspect_human_deformation.py from the repository checkout before running it."
    )


def _ensure_repo_on_path():
    repo_root = _find_repo_root(_script_path())
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)


_ensure_repo_on_path()

from blender_adapter.adapter import create_asset
from object_core import BodyType, HumanoidSpec, generate_proportions
from object_core.geometry import generate_deformable_mesh
from object_core.rigging import generate_deforming_skeleton, generate_skin_weights


POSES = (
    ("Shoulder", "upper_arm.left", "Y", 0.75),
    ("Elbow", "forearm.left", "Z", 1.05),
    ("Wrist", "hand.left", "Y", 0.75),
    ("Hip", "upper_leg.left", "X", 0.75),
    ("Knee", "lower_leg.left", "X", 1.05),
    ("Ankle", "foot.left", "X", 0.75),
    ("Neck", "neck", "Y", 0.55),
)


def _clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def _human(name):
    proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
    mesh = generate_deformable_mesh(proportions)
    skeleton = generate_deforming_skeleton(proportions)
    weights = generate_skin_weights(mesh, skeleton)
    root = create_asset(mesh, name=name, skeleton=skeleton, skin_weights=weights)
    armature = next(child for child in root.children if child.type == "ARMATURE")
    return root, armature


def _label(name, location):
    bpy.ops.object.text_add(location=location)
    label = bpy.context.object
    label.name = name + "_Label"
    label.data.body = name
    label.data.align_x = "CENTER"
    label.data.size = 0.12
    label.rotation_euler.x = math.radians(90.0)


def main():
    _clear_scene()
    cases = (("Neutral", None, None, 0.0),) + POSES

    # Generated Humans use Blender's normal meter-scale coordinates. Keep the
    # inspection grid on that same scale so Frame All produces a useful view.
    columns = 4
    column_spacing = 1.4
    row_spacing = 2.4
    x_offset = -column_spacing * (columns - 1) / 2.0
    y_offset = row_spacing / 2.0

    for index, (name, bone_name, axis, angle) in enumerate(cases):
        row, column = divmod(index, columns)
        x = x_offset + column * column_spacing
        y = y_offset - row * row_spacing
        root, armature = _human("Human_" + name)
        root.location.x = x
        root.location.y = y
        _label(name, (x, y - 0.42, 1.95))

        if bone_name is not None:
            pose_bone = armature.pose.bones[bone_name]
            pose_bone.rotation_mode = "XYZ"
            setattr(pose_bone.rotation_euler, axis.lower(), angle)

    bpy.context.view_layer.update()
    print("Human deformation inspection scene ready in a meter-scale 2x4 grid: Neutral + " + ", ".join(name for name, *_ in POSES))


if __name__ == "__main__":
    main()
