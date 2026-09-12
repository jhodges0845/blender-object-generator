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
- Shared Modify code owns transport/planning/preservation, while providers own anatomy and semantic interpretation.
- Validation reports real limitations instead of manufacturing a green result.
- A successful file write is not equivalent to destination certification.
- Generated Blender data should remain editable by artists.
- Provider names and keys are canonical architecture identifiers; saved legacy identifiers are handled only through explicit compatibility mapping.
- Unsupported Modify operations remain explicit blockers rather than silent no-ops.

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
- [x] Idle, Walk, Flight, and Run capability-driven animation workflow where supported by each provider.
- [x] Blender 5.2 layered-action support and active-scene glTF scoping.
- [x] CI on standalone Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Cached Blender runtimes in CI.
- [x] Branch protection requiring all six CI checks before merge.
- [x] Initial Godot, Unity, Unreal, and Cura smoke verification.
- [x] Redraw-time validation caching plus fresh export safety preflight.
- [x] Cura Human print preparation plus selectable print-scale presets without changing the source/game asset.
- [x] Legacy Humanoid hidden from new generation while retaining compatibility resolution for existing generated assets.
- [x] Canonical generation providers named Human, Quadruped, Avian, and Box.
- [x] Unified Asset Assistant sidebar organized around Generate / Modify / Rig / Animate / Validate / Export.
- [x] Reproducible tagged-release packaging automation implemented; no release/tag should be created until explicitly approved.

## Human provider — foundation complete, quality refinement active

Human completed the original provider foundation: connected deformable geometry, dedicated skeleton and skin weights, editable UV/material/texture data, Idle/Walk/Run actions, automated deformation coverage, Blender visual review, and direct Godot/Unity/Unreal destination evidence.

The current Run clip remains a first-pass game-animation foundation and is a quality-polish item rather than an architectural blocker.

The Human provider is now also the main proof target for rich semantic Modify. Executable topology-preserving region targets include body, torso, shoulders, head, face, jaw, cheeks, arms, and legs.

Recent Human quality work:

- [x] first external inspection -> ChatGPT/external edit -> returned Modify file -> Blender apply round trip manually confirmed;
- [x] persistent semantic patch recipe preserved on the generated root;
- [x] Human semantic profiles for torso, shoulders, head, face, jaw, cheeks, arms, and legs;
- [x] increased generated head profile resolution;
- [x] neutral facial planes for chin, mouth, nose, eye recess, brow, and forehead;
- [x] front/side Blender review confirming the head and face foundation is improving;
- [ ] strengthen reusable facial landmarks enough for recognizable character shaping without hard-coding a named character;
- [ ] continue body/hand silhouette refinement where visual review shows a real limitation.

## Quadruped provider — foundation complete

Quadruped is the first genuine non-Human deforming-provider architecture proof. It has connected four-legged geometry, a dedicated skeleton and normalized weights, deformation coverage, Idle/Walk/Run, deterministic UVs, portable textured material intent, and generic Blender workflow coverage.

Interactive Blender review confirmed generation, rigging, animation, and surfacing. Quadruped semantic execution remains a follow-up provider milestone.

## Avian provider — foundation complete plus first rich semantic executor

Avian covers both airborne and ground locomotion and is the first provider with executable rich semantic geometry Modify.

Completed Avian foundation includes:

- [x] canonical `avian` / Avian provider identity and parameter contract;
- [x] connected body with integrated wings, tail, legs, and feet;
- [x] dedicated spine/neck/head, wing, tail, leg, and foot skeleton;
- [x] normalized local skin weights and deformation coverage;
- [x] deterministic UVs and portable textured plumage material intent;
- [x] provider-specific Idle, Walk, and Flight;
- [x] distinct Walk and Flight identities; Run intentionally unsupported;
- [x] automated game-target packaging coverage and interactive Blender walk/leg review;
- [x] persistent topology-preserving semantic shape/scale operations for body, chest, head, beak, wings, tail, legs, and feet.

The semantic executor is deliberately provider-owned; shared Modify code does not know what a beak or wing is.

## Modify workflow — transport and geometry semantics implemented

The current workflow is:

`Select generated asset -> Export Inspection File -> edit externally -> Import Change File -> review plan -> Apply Imported Changes -> revalidate`

Implemented:

- [x] portable inspection/snapshot/request/plan contract;
- [x] asset/provider identity binding for returned files;
- [x] non-mutating import/preview followed by re-inspection/replanning on apply;
- [x] transactional provider-parameter regeneration with preservation blockers;
- [x] metadata-only generated animation export-name changes;
- [x] semantic target manifests and executable-operation reporting;
- [x] persistent/replayable semantic patch state;
- [x] Avian semantic geometry execution;
- [x] Human semantic geometry execution;
- [x] external requests can compose parameter, semantic, and animation-name changes through safe staged routing;
- [x] automated core/Blender coverage plus a real Human round-trip manual checkpoint.

Still required for the richer product goal:

- [ ] improve Human reusable base geometry enough that semantic edits can produce recognizable character identity;
- [ ] define first-class attachable component architecture for hair, clothing, and accessories;
- [ ] keep optional component physics as adapter-facing behavior rather than ordinary Human body semantics;
- [ ] add provider/component persistence, ownership, inspection, and safe apply rules before making those component operations executable;
- [ ] validate generic Avian -> specific bird and generic Human -> specific character workflows end-to-end at useful visual quality.

## Hair, clothing, accessories, and physics direction

Hair and clothing are not ordinary Human body-geometry edits. They should be separate attachable components because they can have their own geometry, materials, rigging/weights, collision, and optional dynamics.

Planned separation:

- Human: body/facial geometry, skin/material foundation, skeleton/weights, attachment context;
- Hair: hairstyle geometry/materials plus optional dynamic metadata;
- Clothing: garment geometry/materials plus rig/weight and optional cloth/collision metadata;
- Accessories: rigid or skinned attachment behavior;
- Host/engine adapters: translate optional physics intent into Blender/Godot/Unity/Unreal behavior.

No component operation should advertise itself as executable until the real ownership/persistence/apply path exists.

## Target verification

Initial smoke checks exist for all four destinations. Human has direct Godot, Unity, and Unreal destination evidence. Quadruped and Avian use the same provider-neutral adapters with automated packaging coverage; additional destination-specific interactive evidence can be captured during release hardening.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [x] Human Godot, Unity, and Unreal game-target checkpoints.
- [x] Quadruped Blender generation/rig/animation/material checkpoint.
- [x] Avian automated Godot GLB and Unity FBX animation-packaging checkpoint.
- [x] Avian interactive Blender visual-quality checkpoint for leg placement and Walk motion.
- [ ] Detailed Cura certification pass covering representative Human dimensions, orientation, slicing warnings, and physical-print considerations.
- [ ] Broader Quadruped and Avian destination certification across Godot/Unity/Unreal during release hardening.

## Current checkpoint — rich Modify quality before public alpha

The original Modify transport/preservation workflow and structural UI overhaul are complete. The scope expanded after the external Modify proof demonstrated that the first public version should support genuinely useful provider-aware edits rather than parameter changes alone.

The current blocker is therefore not Modify transport; it is **useful semantic/structural edit quality**.

Current order:

1. [x] Complete provider foundations for Human, Quadruped, and Avian.
2. [x] Complete preservation-aware Modify transport, external file handoff, and persistent semantic patch architecture.
3. [x] Complete structural Asset Assistant UI organization.
4. [x] Implement Avian semantic geometry apply and Human semantic geometry apply.
5. [ ] Finish the current Human reusable facial/base-geometry refinement checkpoint.
6. [ ] Define and implement first-class component architecture for hair/clothing/accessories without baking physics into Human body semantics.
7. [ ] Re-run end-to-end Avian and Human external Modify proofs at the intended visual-quality bar.
8. [ ] Run full cross-provider regression, preservation, architecture, docs, and test-coverage audit.
9. [ ] Resume final release hardening and clean packaged-install smoke test in Blender 5.2.1.
10. [ ] Make an explicit version/tag decision and publish a public alpha only when approved.

### Shared follow-ups

- Human Run animation-quality tuning: upper-arm swing, knee lift, torso pitch, and timing/phase polish.
- Additional Avian gait/flight quality polish only if future visual review exposes a real issue.
- Quadruped semantic executor.
- Reusable UV/material/validation infrastructure only when additional real provider needs justify it.
- Watertight print-preparation work for providers that explicitly support 3D printing.
- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- Broader destination certification beyond the evidence needed for the first alpha.

## Near-term release milestone

> Asset Assistant can create useful editable starting assets across Human, Quadruped, and Avian body plans; inspect and richly modify a generated asset through a preservation-aware external handoff; keep anatomy/provider logic out of shared workflow code; present the workflow through a coherent artist-facing UI; validate truthfully; export through supported targets; and leave the result ready for continued artist or game-engine refinement.
