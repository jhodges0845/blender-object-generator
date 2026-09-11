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
- [x] Idle, provider-named locomotion, and Run capability-driven animation workflow.
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

## Quadruped provider — foundation complete

Quadruped is the first genuine non-Human deforming-provider architecture proof. It has connected four-legged geometry, a dedicated skeleton and normalized weights, deformation coverage, Idle/Walk/Run, deterministic UVs, portable textured material intent, and generic Blender workflow coverage.

Interactive Blender review confirmed generation, rigging, animation, and surfacing. Broader per-engine certification remains release-hardening evidence rather than a provider-foundation blocker.

## Avian provider — foundation complete

Avian is the second non-Human deforming-provider proof and demonstrates that shared locomotion does not need to mean Walk.

The completed Avian foundation includes:

- [x] canonical `avian` / Avian provider identity and parameter contract
- [x] deterministic connected low-poly body with integrated wings and tail
- [x] Avian spine/neck/head, upper/lower wing, and tail skeleton
- [x] normalized local skin weights plus wing-root, wing-segment, neck/head, and tail deformation coverage
- [x] deterministic face-corner UVs and portable textured plumage material intent
- [x] provider-specific Idle and Flight motion using the shared editable Blender action pipeline
- [x] distinct `Flight` clip identity rather than disguising Avian motion as Walk
- [x] capability isolation so Human and Quadruped do not expose Flight
- [x] representative automated Godot GLB and Unity FBX export coverage for Avian skinning plus Idle/Flight packaging
- [x] documentation and architecture closeout confirming Avian anatomy stays provider-specific and target adapters remain provider-neutral

Manual visual review of Avian Idle/Flight motion remains desirable before release, because automated tests cannot judge animation aesthetics. Broader destination import/playback certification is tracked under release hardening.

## Target verification

Initial smoke checks exist for all four destinations. Human has direct Godot, Unity, and Unreal destination evidence. Quadruped and Avian use the same provider-neutral adapters with automated packaging coverage; additional destination-specific interactive evidence can be captured during release hardening.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [x] Human Godot, Unity and Unreal game-target checkpoints.
- [x] Quadruped Blender generation/rig/animation/material checkpoint.
- [x] Avian automated Godot GLB and Unity FBX animation-packaging checkpoint.
- [ ] Avian interactive Blender visual-quality checkpoint for Idle/Flight.
- [ ] Detailed Cura certification pass covering representative Human dimensions, orientation, slicing warnings, and physical-print considerations.
- [ ] Broader Quadruped and Avian destination certification across Godot/Unity/Unreal during release hardening.

## Current milestone — release hardening / publish readiness

Provider expansion is no longer the immediate priority. Human, Quadruped, and Avian now cover three meaningfully different deforming body/motion plans and have exercised the provider architecture enough to shift focus toward product readiness.

Near-term order:

1. [ ] Run a cross-provider test-coverage and architecture audit for release-severity gaps.
2. [ ] Complete the remaining manual Avian visual checkpoint and any motion-quality fixes it reveals.
3. [ ] Recheck representative Human / Quadruped / Avian exports and document destination evidence without treating a successful file write as full certification.
4. [ ] Review UI clarity, especially the Animations sidebar naming against Blender 5.x's built-in Animation category.
5. [ ] Review installation, version support, packaging, license/readme, and first-run instructions for publication.
6. [ ] Classify remaining Cura, destination-certification, and animation-polish work as blocker vs post-release follow-up.

### Shared follow-ups

- Human Run animation-quality tuning: upper-arm swing, knee lift, torso pitch and timing/phase polish.
- Avian Flight animation-quality tuning after visual review.
- Reusable UV/material/validation infrastructure only when additional real provider needs justify it.
- Watertight print-preparation work for providers that explicitly support 3D printing.
- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.

## Near-term release milestone

> Asset Assistant can create useful editable starting assets across Human, Quadruped and Avian body plans, route each through only the workflow capabilities it actually supports, validate truthfully, export through supported targets, and leave the result ready for an artist to refine.
