# SPDX-License-Identifier: GPL-3.0-or-later
"""Build representative Human 1.0 poses for repeatable visual deformation review.

The script can be opened directly in Blender's Scripting workspace and run with
Run Script, or launched from the repository root with:

    blender --python scripts/inspect_human_deformation.py

The script leaves one neutral reference plus seven posed deforming Humans in the
scene. Each pose exercises a joint already protected by Blender deformation
regression tests; this harness is for the complementary visual-quality review.
"""

import math
import sys
from pathlib import Path

import bpy


# Blender's Text Editor does not automatically add the script's repository root
# to sys.path. Resolve it from the opened text block's filepath so this helper can
# be run directly from the Scripting workspace without environment setup.
def _ensure_repo_on_path():
    script_path = Path(bpy.path.abspath(__file__)).resolve()
    repo_root = script_path.parent.parent
    if not (repo_root / "object_core").is_dir() or not (repo_root / "blender_adapter").is_dir():
        raise RuntimeError(
            "Could not locate the Asset Assistant repository root from "
            + str(script_path)
            + ". Open scripts/inspect_human_deformation.py from the repository checkout before running it."
        )
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
    label.data.size = 8.0
    label.rotation_euler.x = math.radians(90.0)


def main():
    _clear_scene()
    spacing = 115.0
    cases = (("Neutral", None, None, 0.0),) + POSES
    offset = -spacing * (len(cases) - 1) / 2.0

    for index, (name, bone_name, axis, angle) in enumerate(cases):
        x = offset + index * spacing
        root, armature = _human("Human_" + name)
        root.location.x = x
        _label(name, (x, -30.0, 195.0))

        if bone_name is not None:
            pose_bone = armature.pose.bones[bone_name]
            pose_bone.rotation_mode = "XYZ"
            setattr(pose_bone.rotation_euler, axis.lower(), angle)

    bpy.context.view_layer.update()
    print("Human deformation inspection scene ready: Neutral + " + ", ".join(name for name, *_ in POSES))


if __name__ == "__main__":
    main()
