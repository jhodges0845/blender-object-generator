# Looping idle (0.6)

Install the rebuilt ZIP, then restart Blender to load the updated modules.
Generate a Model, add its Basic Rig, and return to Object Mode if needed.
Open Animation, choose the cycle duration and motion strength, and click
Generate Idle. Click Play / Pause to preview. The clip starts at the scene's
start frame; Set Playback Range adjusts the end frame to one cycle.

This first clip adds subtle breathing motion to the torso, head and upper arms
from the generated A-pose. Root and legs stay still. It is editable in Blender's
Action Editor. Existing actions, NLA tracks, drivers, constraints and non-rest
poses are refused without replacement. Use a newly generated character to try
different settings. Removing the add-on preserves the action and its keyframes.

The core returns immutable rotation tracks: seconds and angle radians about an
axis in rest armature coordinates. The adapter converts that axis into each
bone's local coordinates, avoiding dependency on Blender's choice of bone roll.
Parent rotations compose normally. Thirty-two linear segments approximate a
cosine breathing cycle; endpoints match exactly. This is sampled motion rather
than a mathematically smooth interpolation curve.

Blender converts seconds using FPS / FPS Base, creates quaternion curves with
Cycles modifiers, and keeps the action saved with a fake user. The playback end
excludes the duplicate endpoint; fractional-frame periods are rounded up for
the integer timeline. Engine export may require baking the repeating curves.
Validation checks clip presence, not artistic quality or engine compatibility.
