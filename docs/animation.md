# Generated animation

Asset Assistant keeps animation intent host-independent. Providers return immutable sampled rotation tracks in seconds/radians around axes expressed in rest-armature coordinates. The Blender adapter translates those samples into editable quaternion action curves, converts seconds using FPS / FPS Base, adds Cycles modifiers for looping clips, and preserves generated actions with a fake user.

## Clip selection

The Blender Animation panel exposes a clip selector. Supported providers can generate Idle or Walk as separate editable Blender actions. A generated clip is created once; selecting it again activates the existing action instead of rebuilding or overwriting its keys. This lets an artist keep edits to one generated clip while switching to another.

Only one action is active on the rig at a time for editing and preview. Inactive generated actions remain saved with the Blender file through fake users. Export is different: engine adapters can package the generated clip library without permanently changing the `.blend` file. Temporary export state is always restored after writing.

Artist-authored actions are never replaced by generated clips. Existing NLA tracks, drivers, constraints, and manual non-rest poses remain preservation boundaries that require deliberate artist preparation.

## Idle

The idle generator produces a closed breathing cycle affecting torso, head, and upper arms while leaving root and legs stationary. In Blender, generate a model, add its basic rig, choose Idle in the Animation panel, set cycle duration and motion strength, and generate the clip. Preview Motion Pose shows the middle of the active clip without playback.

## Human 1.0 locomotion

Human 1.0 exposes a portable in-place walk cycle in addition to idle. The cycle uses opposing upper-leg and upper-arm swing, lower-leg motion, and a small torso counter-rotation. It is deliberately an in-place game-animation foundation rather than root-motion navigation. The core cycle is deterministic, closed, strength-scalable, and independent of Blender.

The Blender adapter translates locomotion through the same shared clip-to-action path as idle and creates an editable `.Walk` action. Direct Blender integration coverage verifies cyclic action curves, opposing leg motion, coexistence of Idle and Walk actions, clip switching without overwriting generated keys, and preservation of artist animation.

## Export behavior

Animated engine export treats Asset Assistant-generated actions as a clip library, but packaging is destination-specific.

Godot GLB/glTF exports all generated clips in one file. Current Blender uses Actions mode while older Blender relies on the temporary one-strip-per-action NLA organization. Unity FBX also keeps the generated clips together in one FBX as separate animation stacks; `bake_anim_use_all_actions` remains disabled so unrelated compatible actions are not broadcast into the export.

Unreal uses a different packaging strategy because the standard Unreal skeletal-animation import workflow is most reliable with one animation per FBX. Choosing an Unreal output such as `Human_Unreal.fbx` creates the skeletal mesh/skeleton FBX plus adjacent clip files such as `Human_Unreal_Idle.fbx` and `Human_Unreal_Walk.fbx`. Each animation sidecar is exported with only that generated action active and is intended to be imported against the skeleton created by the model FBX. Unity's working multi-clip FBX behavior is intentionally unchanged.

All temporary action, playback-range, and export state is restored after export. Existing artist NLA tracks and drivers remain preservation boundaries rather than being silently reorganized.

## Preservation and validation

Generated animation refuses to overwrite artist actions, NLA tracks, drivers, constraints, or non-rest poses. Generated Asset Assistant clips can coexist on the same rig and can be switched explicitly. Removing the add-on preserves the actions and keyframes.

Validation checks changing unmuted curves, missing targets, non-finite values, Rest Position, zero action influence, and exporter-specific animation restrictions. A successful Blender action or file write is not destination certification; destination import and playback remain part of the Human 1.0 checkpoint.
