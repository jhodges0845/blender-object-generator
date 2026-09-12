# Editable asset persistence and animation workflow

Asset Assistant generation is one entry path, not a requirement for every editing session. Artists must be able to create or import a base asset, attach reusable component assets later, work on animations independently, save an editable checkpoint, reopen it, and continue without regenerating the character.

## Working asset versus destination export

Asset Assistant separates an editable working asset from destination delivery formats.

- `.blend` is the first canonical editable save/checkpoint format because it can preserve Blender objects, armatures, Actions, modifiers, vertex groups, materials, Asset Assistant ownership metadata, component records, and future physics configuration.
- GLB/glTF, FBX, STL, 3MF, and future target-specific packages remain destination/export formats. They are not assumed to preserve every Asset Assistant editing contract required to resume work.

The `.blend` checkpoint action lives in the existing Export section, but it is not modeled as another engine/print target. It saves a copy of the complete Blender working state with `copy=True`, so the current open file/session path is not changed. This keeps editable checkpoints and destination exports adjacent in the artist workflow while preserving their different meanings.

A successful engine export must never replace or destroy the editable working state.

## Base asset entry paths

The artist-facing workflow has two explicit base-asset entry paths:

1. Generate a supported provider asset such as Human, Quadruped, or Avian.
2. Open an Asset Assistant editable `.blend` checkpoint from the Generate section and continue from the saved state.

Checkpoint files are marked with an Asset Assistant working-state kind/version when the copy is written. After Blender opens a checkpoint, a persistent post-load validator re-inspects every recognizable Asset Assistant base asset, including provider/ownership/Modify state and attached component state. When exactly one base asset exists, it becomes the active Asset Assistant target automatically. Invalid or unsupported checkpoint state is reported instead of silently claiming ownership.

External Blender assets that do not carry Asset Assistant checkpoint/ownership metadata are deliberately not adopted by this reopen path. They require a separate explicit adoption/registration workflow before destructive Modify operations can claim ownership.

## Reusable component assets

Hair, clothing, and accessories are independent assets that are attached to a base model. They are not required to be generated as part of the Human or other body provider.

A component may originate from generated geometry or imported artist-authored geometry. Once registered, the existing component contract supplies stable identity, kind, provider/source key, attachment target, rigid/skinned mode, parent-rig binding, ownership, parameters, and optional physics intent.

Imported component adoption supports one artist-selected external Blender mesh at a time. Adoption is explicit ownership transfer rather than a copy: Asset Assistant creates the component root and portable record, reparents the existing mesh while preserving its world transform, and immediately reuses the existing component inspection/lifecycle contract. Materials remain artist-owned so shared material datablocks are not silently claimed.

Rigid adoption supports `asset_root` and `bone:<bone-name>` attachment targets. Parent-rig skinned adoption uses `attachment_target="body"`, preserves the artist's existing vertex groups, verifies that every weighted group maps to a bone in the active Asset Assistant rig, and requires every vertex to be weighted. If no Armature modifier exists, adoption creates one targeting the active Asset Assistant rig. If an Armature modifier already exists, it must already target that rig and use vertex groups without bone envelopes; Asset Assistant does not silently retarget or reconfigure it. The observed weights are persisted and re-inspected through the same exact-weight tamper detection used by generated skinned components.

An unregistered artist mesh may already be parented somewhere under the selected Asset Assistant asset and still be adopted as skinned geometry, provided it is not generated body geometry and is not already component-owned. Geometry owned by another Asset Assistant asset is rejected.

Because adoption transfers geometry ownership, removing an adopted component may delete the adopted mesh object. Asset Assistant does not silently claim arbitrary scene objects, body geometry, already-owned component geometry, child hierarchies, or incompatible weight groups. Failed attachment or post-adoption inspection restores the original parenting, world transform, and component metadata; any Armature modifier created by the failed adoption is removed.

This enables workflows such as:

`Open Maxine base -> import hair asset -> import jacket asset -> attach accessory -> save editable checkpoint`

and later:

`Open saved checkpoint -> replace jacket -> remove accessory -> add animations -> save -> export to game engine`

Component import preserves the same transactional inspection/removal/replacement boundaries already established by the component foundation.

## Animation assets

Animations should become first-class editable assets rather than only generated clips embedded in the initial character workflow.

A portable animation identity should eventually describe at least:

- stable animation/clip ID;
- artist-facing and export name;
- source/import provenance;
- rig compatibility/signature;
- frame range and FPS;
- loop intent;
- root-motion intent;
- ownership of generated/imported keyframe or curve data;
- provider/capability requirements where relevant.

The workflow should support importing, adding, inspecting, renaming, removing, replacing, and continuing to modify animations without regenerating the base model.

## Animation Modify

Animation Modify should follow the preservation-aware pattern already proven for model Modify:

`Inspect animation -> export portable inspection -> edit externally -> import returned request -> preview/validate -> apply -> re-inspect`

Initial executable semantics should be deliberately narrow and measurable. Candidate operations include timing/cycle length, overall motion amplitude, root motion, torso lean, limb swing/lift, contact timing, looping, and other provider/clip-specific tuning. Shared Modify transport must not hard-code Human anatomy; animation providers/capabilities own semantic interpretation.

Artist-authored keyframes must not be overwritten unless ownership is explicit and the requested operation can preserve unowned work.

## Intended artist workflow

`Generate OR open saved base asset -> inspect/modify base -> import/attach/remove/replace component assets -> import/add/remove/replace/modify animation assets -> save editable .blend checkpoint -> export destination formats -> reopen editable checkpoint later and continue`

The workflow should not force regeneration simply because the artist wants to add clothing, change an accessory, tune a Run animation, or add a new animation.

## Implementation order before hair/clothing catalogs

1. [x] Add an explicit editable working-asset save/checkpoint operation with `.blend` as the initial format and non-destructive destination export separation.
2. [x] Add reopen validation for Asset Assistant `.blend` working assets and restore/inspect known provider, ownership, component, rig, animation, and Modify state.
3. [x] Add imported component registration/adoption so artist-authored reusable hair/clothing/accessory assets can enter the existing rigid or parent-rig-skinned component lifecycle without being generated by a provider.
4. [ ] Promote animations to first-class portable records with stable identity, ownership, compatibility, and inspection.
5. [ ] Add animation import/add/remove/replace lifecycle operations.
6. [ ] Add preservation-aware animation Modify transport and the first narrowly scoped executable animation tuning semantics.
7. [ ] Run a save -> reopen -> component edit -> animation edit -> save -> engine export regression/manual checkpoint.
8. [ ] Only then begin real hair, clothing, and accessory catalogs/providers and richer component physics.

## Non-goals for this stage

- replacing Blender's native `.blend` file format;
- inventing a custom binary project format before a demonstrated need;
- forcing every imported external Blender asset to become Asset Assistant-owned;
- baking hair/clothing into Human body geometry;
- making GLB or FBX the authoritative editable project state;
- implementing engine-specific physics before portable ownership and intent are established.
