# Editable continuity audit

This audit reviews the production-character workflow after the initial editable continuity checkpoint. The focus is not on adding features for their own sake; it is on identifying places where a real artist could lose state, misunderstand ownership, or fail to resume work safely.

## Current conclusion

No architecture-blocking issue was found. The core boundaries remain sound: host-independent contracts stay in `object_core`, Blender scene/persistence behavior stays in `blender_adapter`, providers own anatomy-specific generation/Modify semantics, and destination-specific behavior stays behind target adapters.

The remaining risk is primarily workflow/expectation clarity plus manual visual validation.

## Findings

### 1. Native Blender reopen needed automatic checkpoint validation

**Status: fixed in this audit.**

Previously, post-load checkpoint validation was only triggered when the file was opened through Asset Assistant's **Open Editable Checkpoint** operator. A user opening the same marked checkpoint through Blender's normal **File -> Open** or recent-files flow could retain all data but would not get automatic Asset Assistant validation/target restoration.

Marked Asset Assistant checkpoints now validate after any Blender file load. Ordinary unmarked `.blend` files remain untouched. The dedicated Asset Assistant Open operator still reports an error if the selected file is not a marked checkpoint.

### 2. Machine-readable model inspection is not visual inspection

**Status: documented workflow limitation.**

The exported model inspection describes provider parameters, semantic operations, ownership, component/rig/animation state, and executable Modify capabilities. It does not contain a rendered view of the character or enough visual information to judge likeness, silhouette, facial appeal, proportion aesthetics, clipping, or deformation quality by eye.

For production character work, external JSON refinement should therefore be paired with a screenshot or viewport review after Preview. The JSON is the authoritative state/operation contract; the screenshot is the visual feedback loop.

This distinction matters especially for iterative character work such as establishing a named protagonist. A structurally valid request can still be aesthetically wrong.

### 3. Recommended body-first workflow should be explicit

**Status: documentation recommendation.**

For a new production Human, the least wasteful path is generally:

`Generate base -> inspect/refine body -> visual review -> add/confirm rig -> animations/components -> save/export`

Asset Assistant can preserve or rebuild generated rig state during supported modifications, but there is no advantage to doing animation work before the major body proportions are accepted. The workflow should encourage large body/proportion decisions before animation polish.

A checkpoint can still be saved at any stage.

### 4. External requests are state-sensitive and should be treated as short-lived

**Status: existing protection; documentation emphasis needed.**

Returned model and animation requests are validated against current asset/provider/animation identity before mutation. This is correct, but users should understand that an old returned JSON request may become stale after another Modify/apply/reopen sequence.

Recommended rule: export a fresh inspection before each independent external refinement round instead of building a library of old pending requests.

### 5. Animation refinement intentionally does not equal arbitrary keyframe editing

**Status: by design.**

The first animation Modify surface safely reproduces duration/speed, motion strength, and export naming for Asset Assistant-owned generated clips. This is enough to prove the external refinement loop, but it will not yet express higher-level direction such as "more confident stride", "less shoulder bounce", or "stronger knee lift" except indirectly through global strength/speed.

Those richer controls should be provider/capability-specific additions after production use demonstrates which controls matter. They should not be implemented as blind quaternion-curve edits in shared code.

### 6. Artist/imported ownership boundaries remain a deliberate limitation

**Status: by design and should remain strict.**

Artist/imported Actions are visible and manageable without transferring curve ownership. The generated-animation refinement path must continue refusing to regenerate those curves. Likewise imported component materials remain artist-owned while adopted geometry ownership can be transferred explicitly.

Future convenience features should not weaken these boundaries merely to make a workflow appear simpler.

### 7. Real reopen/preview remains the final continuity checkpoint

**Status: manual checkpoint pending.**

Automated tests now cover a production-style chain through Human body semantic refinement, animation refinement, editable checkpoint save, stable identity preservation, and Godot export. They intentionally do not execute a real `open_mainfile` mid-test because Blender replaces the active session.

The final acceptance test is therefore hands-on:

`Generate -> save .blend -> reopen -> export model inspection -> external body request -> import -> preview -> apply -> visual review -> save -> reopen -> animation inspection -> external animation request -> import -> preview -> apply -> play -> save -> reopen -> destination export`

If that passes in the real sidebar UI without confusing state or lost ownership, the editable-continuity phase can be closed.

## Tonight's production-character test notes

For the first named-character pass, keep the first round intentionally simple:

- establish broad height/weight/body type and major torso/shoulder/head/face/jaw/cheek shape;
- use Preview before Apply;
- send a Blender viewport screenshot with the inspection/result when judging visual character quality;
- save a new editable checkpoint after each approved milestone rather than overwriting the only known-good file;
- refine one generated animation at a time;
- export a fresh animation inspection after any successful animation Apply before asking for another refinement;
- treat engine export as delivery/testing output, never as the source file to resume from.

## Deferred follow-up after the checkpoint

Once the manual continuity test passes, the next major product phase can begin with real reusable component providers/catalogs: hair, clothing, accessories, and later portable physics intent. Animation can evolve in parallel as concrete production needs expose useful provider-specific tuning controls.
