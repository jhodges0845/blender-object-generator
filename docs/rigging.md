# Piece 5: basic rigid rigging

A generated humanoid can now include a 16-bone skeleton: one root control and
15 bones matching the separate mesh parts. Parent relationships let the hand
follow the forearm and upper arm, and the foot follow the lower and upper leg.
This is forward kinematics: rotate bones directly to pose the character.
There are no IK controls, joint limits, or smooth joints yet. A basic [idle animation](animation.md) is available.

## Try it in Blender

1. Update to the rebuilt add-on ZIP using the steps in [the Blender guide](blender.md).
2. In Object Mode, open N > Generator > Model and choose Object Type: Humanoid.
3. Choose your measurements and click **Generate Model**. Open **Rigging** and
   click **Add Basic Rig** to rig that same character.
4. Click **Enter Pose Mode**, or choose Pose Mode in the viewport mode dropdown.
5. Select an upper-arm bone and press R to rotate it; its forearm and hand follow.
6. Press Alt-R on selected bones to clear their rotations and return them to rest.

To pose an existing generated character, select its `Humanoid.Rig` armature in
the Outliner first. Bones display in front of the mesh. The Empty parent still
moves the whole character. The Model tab always generates meshes without a rig.
The Rigging tab can add a rig to a previously generated, unrigged character;
it preserves existing rigs. Choose the intended root in its Character field.

Each mesh part has an Armature modifier and one vertex group. Every vertex in
that part has weight 1.0 for its assigned bone. This is rigid skinning: parts
move as solid pieces. Gaps or overlaps can appear at joints when posing. Smooth
bending will require different mesh topology and blended weights in a later step.

Removing the add-on leaves the bones, modifiers, groups, and meshes editable.
Pose rotations, translations, and scales remain ordinary Blender operations.
The stored measurements describe generation inputs, not live controls.

## Core contracts and generation

```python
from humanoid_core import BodyType, HumanoidSpec
from humanoid_core import generate_proportions, generate_mesh, generate_skeleton

proportions = generate_proportions(HumanoidSpec(180, 95, BodyType.AVERAGE))
mesh = generate_mesh(proportions)
skeleton = generate_skeleton(proportions)
```

`Bone` stores its name, head and tail in centimeters, parent name, and optional
bound part name. `Skeleton` validates a single-root tree in parent-before-child
order, unique names, nonzero bone lengths, finite coordinates, and unique part
bindings. These immutable models contain no Blender data. Bone roll is currently
chosen by Blender; the animation adapter converts rest armature axes into each bone's local coordinates.

`proportions/landmarks.py` is the shared source of joint positions for geometry
and rigging. Mesh generation remains unchanged in appearance. The skeleton uses
the same A-pose, axes, units, and initial supported dimensions as the blockout.
The root bone starts at the hip center; torso and both upper legs are its children.

`humanoid_blender/rigging.py` translates the core tree into an armature and full
vertex weights. `create_character(..., skeleton=skeleton)` requires Object Mode
in the active scene because Blender creates bones in Edit Mode. It restores
selection and active object after that temporary mode change. The UI then
selects the generated character and activates its armature for posing.

## Validation

The test suite checks skeleton hierarchy, mirrored joints, correspondence with
mesh endpoints throughout the supported input grid, unit conversion, unchanged
rest geometry, actual evaluated limb motion, rigid part lengths, and cleanup
after a simulated failure. Run the normal Python and Blender commands from the
[Blender guide](blender.md). The isolated ZIP check generates a rigged preview
scene at `artifacts/blockout-preview.blend`.
