# Asset Assistant Roadmap

This is the working source of truth for current development priorities. Keep implemented behavior, automated coverage, manual verification, and future work clearly separated.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It should remove repetitive and technical friction without replacing the artist. Generated assets are starting points that remain editable and understandable.

The intended architecture is:

`Host-independent asset core -> provider -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> artist review`

The project is broader than Human generation. The provider/capability model is intended to support characters, creatures, props, printable assets, and future asset families without making shared workflow code assume humanoid anatomy.

## Engineering guardrails

- `object_core` remains independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific implementation.
- `humanoid_blender` remains only as a compatibility entry point/module ID where required.
- Generic workflow code follows explicit provider capabilities rather than anatomy assumptions.
- Validation reports real limitations instead of manufacturing a green result.
- A successful file write is not equivalent to destination certification.
- Generated Blender data should remain editable by artists.

## Completed platform foundation

- [x] Asset Assistant identity and GPL release packaging.
- [x] Host-independent `object_core` and canonical `blender_adapter` boundary.
- [x] Provider registry, input fields, and capability declaration validation.
- [x] Static, rigid animated, and skin-weight deforming provider paths.
- [x] Human parameter/proportion foundation and Box static-provider proof.
- [x] Core validation plus Blender-specific inspection.
- [x] Godot, Unity, Unreal, and Cura target profiles/adapters.
- [x] GLB/glTF, FBX, and STL export paths.
- [x] Provider-aware rigging and animation workflow gating.
- [x] Blender 5.2 layered-action support and active-scene glTF scoping.
- [x] CI on standalone Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Cached Blender runtimes in CI.
- [x] Branch protection requiring all six CI checks before merge.
- [x] Initial Godot, Unity, Unreal, and Cura smoke verification.

## Human Provider 1.0

Human 1.0 is the current P0 milestone. The target is an editable, deformable, UV'd, basically surfaced and animated character foundation that exports successfully and is ready for artist refinement.

### Implemented Human foundation

- [x] Opt-in connected Human mesh replacing the disconnected deformation path.
- [x] Shoulder and hip branches stitched into the torso.
- [x] Feet integrated into the leg surface.
- [x] Support geometry around shoulders, elbows, wrists, hips, knees, ankles, foot bends, and neck transition.
- [x] Dedicated deforming skeleton separate from the legacy rigid part-binding path.
- [x] Deterministic normalized skin weights with bounded influences and left/right isolation.
- [x] Connected-joint influence localization plus deliberate same-side hip bridge.
- [x] Softer torso/neck and torso/shoulder weight transitions.
- [x] Blender armature and skin-weight application.
- [x] Provider-aware rigging UI for the deforming Human path.
- [x] Automated deformation movement coverage for shoulder, elbow, wrist, hip, knee, ankle, and neck.
- [x] Automated transition-spread/collapse guards for all seven representative deformation joints.
- [x] Manual deformation inspection harness for milestone-level review.
- [x] Improved blockout hands with palm, knuckle, and tapered fingertip sections.
- [x] Improved blockout feet with heel, midfoot, ball, and tapered toe sections.
- [x] Geometry regressions across all five body presets and supported height extremes.
- [x] Deterministic face-corner UV generation with an editable Blender `UVMap` layer.
- [x] Portable provider material contract plus an editable Human 1.0 Principled base surface.
- [x] Portable generated-image texture contract with Human UV-driven base texture and editable Blender Image Texture translation.
- [x] Portable Human in-place walk cycle with shared Blender clip-to-action translation and automated core/Blender coverage.
- [x] Explicit Idle/Walk selection with separate editable generated actions and safe clip switching.
- [x] Generated Human textures are packed automatically for self-contained export while artist-supplied external textures remain untouched.
- [x] Generated Idle/Walk clips can be created and switched from an evaluated generated pose without being mistaken for artist pose edits.
- [x] Milestone visual/deformation review in Blender 5.2.1 covering neck, shoulder, elbow, wrist, hip, knee, ankle, silhouette, and connected deformation. No blocking separation or catastrophic collapse observed; angular low-poly joint transitions remain acceptable for the editable 1.0 foundation.
- [x] Completed Human 1.0 validates and exports successfully through the Godot GLB path with generated rig, skinning, material/texture and generated animation library.
- [x] Godot destination verification confirmed connected hierarchy, Skeleton3D, generated texture, AnimationPlayer, upright orientation and working Idle/Walk motion.
- [x] Unity generated-animation FBX export now carries Idle and Walk together, with automated regression coverage and manual destination confirmation that both generated clips are exposed.
- [x] Unreal animated export now writes one model/skeleton/material FBX plus one armature-only FBX per generated clip, with regression coverage proving animation data is present and render assets are not duplicated into the sidecars.

### Remaining Human 1.0 work

- [ ] Perform one final Unreal destination verification using the corrected bundle: import the model FBX first, then import Idle and Walk sidecars against its skeleton and confirm both sequences play correctly.
- [ ] Run the Human Provider 1.0 closeout checkpoint: final test coverage, documentation, architecture, compatibility, target-verification evidence, and remaining-risk review.

Definition of done: supported Human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion, truthful validation, successful game-engine export/import, and a clear handoff to an artist.

## Cleanup gate before UV work

The pre-UV cleanup gate is complete:

- [x] Test-coverage audit and targeted Human geometry coverage expansion.
- [x] Documentation sync/cleanup.
- [x] Architecture audit/cleanup.

Future architecture cleanup should remain evidence-driven: remove concrete duplication/confusion and strengthen dependency boundaries only when a real feature exposes the need.

## Target verification

Initial smoke checks exist for all four destinations. Human 1.0 now has direct Godot evidence, completed Unity multi-clip validation, and corrected Unreal animation-bundle behavior awaiting one final destination playback check.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [x] Human 1.0 Godot pass covering hierarchy, skinning integrity, generated texture transfer, orientation and Idle/Walk playback evidence. Measured scale and destination edit/reimport workflow remain broader certification work, not blockers for the Human 1.0 game-character milestone.
- [x] Human 1.0 Unity pass confirming model/rig import and generated Idle/Walk clip availability after the multi-clip export fix. Broader Humanoid-avatar retargeting, exact scale measurement, and edit/reimport remain certification follow-ups rather than 1.0 blockers.
- [ ] Human 1.0 Unreal final pass using the corrected model + animation-sidecar workflow; confirm both Idle and Walk sequences play against the imported skeleton without duplicated render assets.
- [ ] Detailed Cura pass covering dimensions, orientation, slicing warnings, and representative printable output.

## After Human 1.0

### P1

- Dog/quadruped provider as the next major architecture proof.
- Reusable UV/material/validation infrastructure driven by real provider needs.
- Watertight print-preparation work for providers that support 3D printing.
- Bird provider as an additional anatomy/animation proof.

### P2

- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- UI/usability polish, including reviewing the **Animations** sidebar name against Blender 5.x's built-in **Animation** category.
- Additional static/prop providers, LOD/collision work, and other artist-assistance stages when real workflows justify them.

## Suggested implementation order

1. Perform the final corrected Unreal Human 1.0 import/playback check.
2. Close the Human Provider 1.0 checkpoint across tests, docs, architecture, compatibility, verification evidence, and remaining risks.
3. Move to Dog/quadruped and revisit architecture only where it exposes concrete limitations.

## Near-term release milestone

> Give Asset Assistant supported Human parameters and receive an editable, deformable, basically surfaced, animated character foundation that validates, exports, works in a supported game engine with minimal technical repair, and remains ready for an artist to refine creatively.
