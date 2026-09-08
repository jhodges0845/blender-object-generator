# Generated animation

Asset Assistant keeps animation intent host-independent. Providers return immutable sampled rotation tracks in seconds/radians around axes expressed in rest-armature coordinates. The Blender adapter translates those samples into editable quaternion action curves, converts seconds using FPS / FPS Base, adds Cycles modifiers for looping clips, and preserves generated actions with a fake user.

## Idle

The existing idle generator produces a closed breathing cycle affecting torso, head, and upper arms while leaving root and legs stationary. In Blender, generate a model, add its basic rig, then use the Animation panel to choose cycle duration and motion strength and generate the idle. Preview Motion Pose shows the middle of the active clip without playback.

## Human 1.0 locomotion

Human 1.0 now exposes a portable in-place walk cycle in addition to idle. The cycle uses opposing upper-leg and upper-arm swing, lower-leg motion, and a small torso counter-rotation. It is deliberately an in-place game-animation foundation rather than root-motion navigation. The core cycle is deterministic, closed, strength-scalable, and independent of Blender.

The Blender adapter translates locomotion through the same shared clip-to-action path as idle and creates an editable `.Walk` action. A direct Blender integration test verifies cyclic action curves, opposing leg motion, and animation validation. The Blender sidebar still exposes the existing idle workflow only; adding clip selection/multi-action handling is part of the next animation-export hardening slice rather than duplicating temporary UI here.

## Preservation and validation

Generated animation refuses to overwrite existing actions, NLA tracks, drivers, constraints, or non-rest poses. Use a fresh rig for a generated clip until multi-clip action management is implemented. Removing the add-on preserves the action and keyframes.

Validation checks changing unmuted curves, missing targets, non-finite values, Rest Position, and zero action influence. A successful Blender action is not destination certification; engine export may still require baking or explicit multi-clip handling.
