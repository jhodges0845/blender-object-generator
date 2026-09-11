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
- Provider names and keys are canonical architecture identifiers; saved legacy identifiers are handled only through explicit compatibility mapping.

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
- [x] Idle, Walk, and Run capability-driven animation workflow.
- [x] Blender 5.2 layered-action support and active-scene glTF scoping.
- [x] CI on standalone Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Cached Blender runtimes in CI.
- [x] Branch protection requiring all six CI checks before merge.
- [x] Initial Godot, Unity, Unreal, and Cura smoke verification.
- [x] Redraw-time validation caching so Blender UI polling uses the latest explicit validation snapshot while export execution still performs a fresh safety preflight.
- [x] Cura Human print preparation plus selectable print-scale presets without changing the source/game asset.
- [x] Legacy Humanoid hidden from new generation while retaining compatibility resolution for existing generated assets.
- [x] Canonical generation providers named Human, Quadruped, Avian, and Box.

## Human provider — foundation complete

Human completed the P0 milestone: an editable, deformable, UV'd, basically surfaced and animated character foundation that exports successfully and remains ready for artist refinement.

The completed Human path includes connected deformable geometry, dedicated skeleton and skin weights, editable UV/material/texture data, Idle/Walk/Run actions, automated deformation coverage, Blender 5.2.1 visual review, and direct Godot/Unity/Unreal destination evidence. Cura has automated preparation/scale coverage with detailed physical-print certification tracked separately.

The current Run clip is a first-pass game-animation foundation and remains a quality-polish item rather than an architectural blocker.

Definition of done: supported Human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion/run, truthful validation, successful game-engine export/import, and a clear handoff to an artist.

## Quadruped provider — foundation complete

Quadruped is the first genuine non-Human deforming-provider architecture proof. It was implemented without introducing a parallel Blender workflow or speculative cross-provider framework.

### Implemented Quadruped foundation

- [x] Host-independent Quadruped provider with validated body-length, shoulder-height, width, head-length and tail-length parameters.
- [x] One deterministic connected quadruped surface rather than the initial multipart blockout.
- [x] Quadruped skeleton and normalized spatial skin weights behind generic skeleton/skinning contracts.
- [x] Parent-child influence blending through shoulder, hip, neck and tail junctions, including corrected spine attachment for hind legs and tail base.
- [x] Automated Blender deformation checks that bend shoulder, hip, neck and tail and verify localized surface movement.
- [x] Portable Idle, Walk, and Run clips using quadruped-specific motion generation and the shared Blender clip/action translator.
- [x] Walk gait uses opposing diagonal limb phase relationships with spine, neck and tail follow-through.
- [x] Deterministic face-corner UVs on the connected surface.
- [x] Portable textured PBR base coat translated through the generic Blender material path while preserving artist-authored material data.
- [x] Generic Blender Generator/Rigging/Animations workflow exercised through capability declarations; no provider-specific Blender workflow branch required.
- [x] Automated core and Blender coverage for generation, rigging, skinning, deformation, animation, UVs and materials on both supported Blender CI runtimes.
- [x] Interactive Blender 5.2.1 checkpoint confirmed the generated connected Quadruped, armature and generated animations work in Blender.
- [x] Architecture audit confirmed quadruped anatomy remains provider-specific while shared Blender and target adapters remain provider-neutral.
- [x] Provider implementation, generated part names, material names, tests, and stored key standardized on `quadruped` / Quadruped.

The current implementation remains an editable low-poly four-legged starting point rather than an exhaustive all-species generator, finished anatomy, fur simulation, or exhaustive destination certification. Broader morphology presets should be driven by real requirements rather than speculative abstraction.

Definition of done: supported Quadruped parameters produce an editable connected four-legged asset with a deforming rig, localized weights, UV'd/textured base surface, Idle/Walk/Run, truthful capability-driven workflow behavior, automated Blender coverage and a successful interactive Blender milestone review.

## Target verification

Initial smoke checks exist for all four destinations. Human has direct Godot, Unity, and Unreal destination evidence. Quadruped has completed the generic Blender-side generation/rig/animation/surface checkpoint and uses the same provider-neutral target adapters. Detailed per-destination Quadruped certification is release-hardening evidence rather than a blocker for beginning Avian.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [x] Human Godot, Unity and Unreal game-target checkpoints.
- [x] Quadruped Blender generation/rig/animation/material checkpoint.
- [ ] Detailed Cura certification pass covering representative Human dimensions, orientation, slicing warnings, and physical-print considerations. This is not a blocker for additional providers.
- [ ] Broader Quadruped destination certification across Godot/Unity/Unreal can be captured during release hardening; generic target adapters already have Human destination evidence and Quadruped exercises the same provider-neutral paths.

## Next provider milestone

### P1 — Avian — active

Avian is the next architecture proof. It tests another genuinely different body plan and, importantly, a different motion model after Quadruped proved the first non-Human deforming expansion.

Avian now has a deterministic connected low-poly surface with integrated wings and tail, an Avian-specific spine/neck/head/wing/tail skeleton, normalized local skin weights, and Blender rigging through the existing provider-driven workflow. Focused Blender deformation coverage exercises both wing segments, tail segments, neck and head, verifies left/right wing isolation, and checks that the wing root blends across the spine/wing junction rather than acting like a rigid seam. Animation and surfacing remain intentionally disabled until their provider-specific implementations exist.

Implementation order:

1. [x] Define the smallest host-independent Avian provider contract and useful generation parameters.
2. [x] Prove Avian generation through the existing dynamic provider UI and generic Blender asset path before adding new shared abstractions.
3. [x] Add Avian-specific connected geometry, skeleton and skinning while keeping anatomy out of shared Blender code.
4. [x] Add wing/tail deformation coverage driven by actual avian motion needs.
5. [ ] Add Avian surface/UV/material intent through existing portable contracts where they fit.
6. [ ] Add appropriate Avian Idle and locomotion/flight behavior; do not force quadruped or Human gait assumptions onto the provider.
7. [ ] Exercise representative target export and run the same tests/docs/architecture closeout before release hardening.

### Shared follow-ups

- Human Run animation-quality tuning: upper-arm swing, knee lift, torso pitch and timing/phase polish.
- Reusable UV/material/validation infrastructure driven by real provider needs.
- Watertight print-preparation work for providers that explicitly support 3D printing.

### P2

- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- UI/usability polish, including reviewing the **Animations** sidebar name against Blender 5.x's built-in **Animation** category.
- Additional static/prop providers, LOD/collision work, and other artist-assistance stages when real workflows justify them.

## Suggested implementation order

1. Build Avian as the second non-Human anatomy/motion proof, using the Quadruped lessons but not its anatomy.
2. Run Avian closeout across tests, docs, architecture and representative target evidence.
3. Run release-hardening/publish readiness across Human, Quadruped and Avian.
4. Capture remaining destination-certification and usability work according to release severity rather than expanding provider scope indefinitely.

## Near-term release milestone

> Asset Assistant can create useful editable starting assets across Human, Quadruped and Avian body plans, route each through only the workflow capabilities it actually supports, validate truthfully, export through supported targets, and leave the result ready for an artist to refine.
