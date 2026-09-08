# Generated animation

Asset Assistant keeps animation intent host-independent. Providers return immutable sampled rotation tracks in seconds/radians around axes expressed in rest-armature coordinates. The Blender adapter translates those samples into editable quaternion action curves, converts seconds using FPS / FPS Base, adds Cycles modifiers for looping clips, and preserves generated actions with a fake user.

## Clip selection

The Blender Animation panel exposes a clip selector. Supported providers can generate Idle or Walk as separate editable Blender actions. A generated clip is created once; selecting it again activates the existing action instead of rebuilding or overwriting its keys. This lets an artist keep edits to one generated clip while switching to another.

Only one action is active on the rig at a time. Asset Assistant treats that active action as the clip intended for preview, validation, and export. Inactive generated actions remain saved with the Blender file through fake users. This avoids silently blending clips through NLA and keeps export behavior explicit.

Artist-authored actions are never replaced by generated clips. NLA tracks, drivers, constraints, and manual non-rest poses remain preservation boundaries that require deliberate artist preparation.

## Idle

The idle generator produces a closed breathing cycle affecting torso, head, and upper arms while leaving root and legs stationary. In Blender, generate a model, add its basic rig, choose Idle in the Animation panel, set cycle duration and motion strength, and generate the clip. Preview Motion Pose shows the middle of the active clip without playback.

## Human 1.0 locomotion

Human 1.0 exposes a portable in-place walk cycle in addition to idle. The cycle uses opposing upper-leg and upper-arm swing, lower-leg motion, and a small torso counter-rotation. It is deliberately an in-place game-animation foundation rather than root-motion navigation. The core cycle is deterministic, closed, strength-scalable, and independent of Blender.

The Blender adapter translates locomotion through the same shared clip-to-action path as idle and creates an editable `.Walk` action. Direct Blender integration coverage verifies cyclic action curves, opposing leg motion, coexistence of Idle and Walk actions, clip switching without overwriting generated keys, and preservation of artist animation.

## Export behavior

FBX export already bakes the active action only and does not bake all actions or NLA strips. GLB/glTF export is validated against the active rig animation; inactive generated actions are retained in the `.blend` file but are not selected as the current export clip. The Human 1.0 milestone pass should verify the intended active clip after import into each destination rather than treating file creation alone as certification.

## Preservation and validation

Generated animation refuses to overwrite artist actions, NLA tracks, drivers, constraints, or non-rest poses. Generated Asset Assistant clips can coexist on the same rig and can be switched explicitly. Removing the add-on preserves the actions and keyframes.

Validation checks changing unmuted curves, missing targets, non-finite values, Rest Position, zero action influence, and exporter-specific animation restrictions. A successful Blender action or file write is not destination certification; destination import and playback remain part of the Human 1.0 checkpoint.
