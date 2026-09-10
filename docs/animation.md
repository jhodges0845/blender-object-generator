# Generated animation

Asset Assistant keeps animation intent host-independent. Providers return immutable sampled rotation tracks in seconds/radians around axes expressed in rest-armature coordinates. The Blender adapter translates those samples into editable quaternion action curves, converts seconds using FPS / FPS Base, adds Cycles modifiers for looping clips, and preserves generated actions with a fake user.

## Clip selection

The Blender Animation panel exposes a clip selector. Supported providers can generate Idle or Walk as separate editable Blender actions. A generated clip is created once; selecting it again activates the existing action instead of rebuilding or overwriting its keys. This lets an artist keep edits to one generated clip while switching to another.

Only one action is active on the rig at a time for editing and preview. Inactive generated actions remain saved with the Blender file through fake users. Export is different: when more than one Asset Assistant-generated clip exists for the rig, the adapter temporarily stages each generated action as its own one-strip NLA track, exports the clip library, then removes those temporary tracks and restores the original active action. The `.blend` file is therefore not reorganized or permanently pushed into NLA just to satisfy an engine exporter.

Artist-authored actions are never replaced by generated clips. Existing NLA tracks, drivers, constraints, and manual non-rest poses remain preservation boundaries that require deliberate artist preparation.

## Idle

The idle generator produces a closed breathing cycle affecting torso, head, and upper arms while leaving root and legs stationary. In Blender, generate a model, add its basic rig, choose Idle in the Animation panel, set cycle duration and motion strength, and generate the clip. Preview Motion Pose shows the middle of the active clip without playback.

## Human 1.0 locomotion

Human 1.0 exposes a portable in-place walk cycle in addition to idle. The cycle uses opposing upper-leg and upper-arm swing, lower-leg motion, and a small torso counter-rotation. It is deliberately an in-place game-animation foundation rather than root-motion navigation. The core cycle is deterministic, closed, strength-scalable, and independent of Blender.

The Blender adapter translates locomotion through the same shared clip-to-action path as idle and creates an editable `.Walk` action. Direct Blender integration coverage verifies cyclic action curves, opposing leg motion, coexistence of Idle and Walk actions, clip switching without overwriting generated keys, and preservation of artist animation.

## Export behavior

Animated engine export now treats Asset Assistant-generated actions as a clip library. If only one generated action exists, the normal active-action path is used. If multiple generated actions exist, each is staged temporarily as a separate NLA track for the duration of export so destinations can receive distinct clips such as Idle and Walk in one file.

For FBX targets such as Unity and Unreal, the temporary tracks are exported as separate FBX animation stacks while `bake_anim_use_all_actions` remains disabled; this avoids broadcasting unrelated compatible actions. For GLB/glTF, current Blender uses Actions mode and older Blender relies on the existing NLA-strip export behavior. In both cases the active Blender action is restored and the temporary NLA tracks are removed after export.

## Preservation and validation

Generated animation refuses to overwrite artist actions, NLA tracks, drivers, constraints, or non-rest poses. Generated Asset Assistant clips can coexist on the same rig and can be switched explicitly. Removing the add-on preserves the actions and keyframes.

Validation checks changing unmuted curves, missing targets, non-finite values, Rest Position, zero action influence, and exporter-specific animation restrictions. A successful Blender action or file write is not destination certification; destination import and playback remain part of the Human 1.0 checkpoint.
