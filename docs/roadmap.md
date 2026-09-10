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
- [x] Redraw-time validation caching so Blender UI polling uses the latest explicit validation snapshot while export execution still performs a fresh safety preflight.
- [x] Cura Human print preparation plus selectable print-scale presets without changing the source/game asset.

## Human Provider 1.0 — complete

Human 1.0 completed the P0 milestone: an editable, deformable, UV'd, basically surfaced and animated character foundation that exports successfully and remains ready for artist refinement.

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
- [x] Unity generated-animation FBX export carries Idle and Walk together, with automated regression coverage and manual destination confirmation that both generated clips are exposed.
- [x] Unreal animated export writes one model/skeleton/material FBX plus one Interchange-recognizable sidecar FBX per generated clip. Sidecars retain the skinned hierarchy needed by Unreal 5.8 while animation-only import avoids creating duplicate destination render assets.
- [x] Unreal destination verification confirmed the corrected model plus Idle/Walk sidecar workflow and playback after generated clip-pose isolation removed cross-clip contamination.
- [x] Human Provider 1.0 closeout checkpoint completed across test coverage, documentation, architecture, compatibility, destination evidence, performance/UI readiness, and remaining-risk review.

Definition of done: supported Human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion, truthful validation, successful game-engine export/import, and a clear handoff to an artist.

## Cleanup gate before UV work

The pre-UV cleanup gate is complete:

- [x] Test-coverage audit and targeted Human geometry coverage expansion.
- [x] Documentation sync/cleanup.
- [x] Architecture audit/cleanup.

Future architecture cleanup should remain evidence-driven: remove concrete duplication/confusion and strengthen dependency boundaries only when a real feature exposes the need.

## Target verification

Initial smoke checks exist for all four destinations. Human 1.0 now has direct Godot, Unity, and Unreal destination evidence. Cura has automated Human print-preparation coverage and earlier Box slicing evidence; broader print certification remains separate from the Human game-character milestone.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [x] Human 1.0 Godot pass covering hierarchy, skinning integrity, generated texture transfer, orientation and Idle/Walk playback evidence. Measured scale and destination edit/reimport workflow remain broader certification work, not blockers for the Human 1.0 game-character milestone.
- [x] Human 1.0 Unity pass confirming model/rig import and generated Idle/Walk clip availability after the multi-clip export fix. Broader Humanoid-avatar retargeting, exact scale measurement, and edit/reimport remain certification follow-ups rather than 1.0 blockers.
- [x] Human 1.0 Unreal pass using the corrected model + animation-sidecar workflow, including destination playback of both generated clips after clip-pose isolation.
- [ ] Detailed Cura certification pass covering representative Human dimensions, orientation, slicing warnings, and physical-print considerations. This is not a blocker for starting additional providers.

## Next provider milestones

### P1 — Dog/quadruped

Dog is the next major architecture proof. It should exercise the existing provider/capability model with genuinely different anatomy rather than introducing speculative abstractions first.

Near-term goals:

- define a Dog/quadruped provider contract and parameters;
- generate an editable quadruped blockout through the host-independent core;
- add quadruped-specific skeleton, skinning, UV/surface, validation, Idle and locomotion behavior as the provider requires;
- reuse shared Blender workflow and target adapters wherever the existing contracts genuinely fit;
- add new shared abstractions only when Dog exposes a concrete cross-provider requirement; and
- validate representative export behavior before declaring the provider complete.

### P1 — Bird

Bird follows Dog as an additional anatomy and animation proof. Its purpose is to test another non-Human body plan and motion model after the quadruped path has exercised the first real provider expansion.

### Shared follow-ups

- Reusable UV/material/validation infrastructure driven by real provider needs.
- Watertight print-preparation work for providers that explicitly support 3D printing.

### P2

- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- UI/usability polish, including reviewing the **Animations** sidebar name against Blender 5.x's built-in **Animation** category.
- Additional static/prop providers, LOD/collision work, and other artist-assistance stages when real workflows justify them.

## Suggested implementation order

1. Start Dog/quadruped with the smallest provider/core slice that proves generation through the existing capability architecture.
2. Grow Dog through rigging, deformation, surfacing, animation, validation and representative target export without pre-building unused framework layers.
3. Run a Dog closeout checkpoint across tests, docs and architecture.
4. Build Bird as the second non-Human anatomy proof.
5. Run release-hardening/publish readiness after the Human, Dog and Bird provider milestones are complete.

## Near-term release milestone

> Asset Assistant can create useful editable starting assets across Human, Dog and Bird body plans, route each through only the workflow capabilities it actually supports, validate truthfully, export through supported targets, and leave the result ready for an artist to refine.
