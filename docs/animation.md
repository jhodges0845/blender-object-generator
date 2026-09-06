# Looping idle (0.7)

Install the rebuilt ZIP, then restart Blender to load the updated modules.
Generate a Model, add its Basic Rig, and return to Object Mode if needed.
Open Animation, choose the cycle duration and motion strength, and click
Generate Idle. Click Preview Motion Pose to see the middle of the cycle without
playing the timeline, or Play / Pause for continuous movement. The clip starts at
the scene's start frame; Set Playback Range sets one cycle and disables any old
preview range. Generation and preview put the armature in Pose Position.

This clip adds visible breathing motion to the torso, head and upper arms
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
Validation checks changing unmuted curves, missing targets, non-finite values,
Rest Position and zero action influence. It is a conservative inspection, not
an evaluation of every constraint/NLA combination or engine compatibility.

If movement is hidden, confirm the Object field points to the intended model,
hide other models overlapping it, and use Preview Motion Pose. To try the stronger
0.7 idle, generate a fresh humanoid; existing 0.6 clips are deliberately preserved.
