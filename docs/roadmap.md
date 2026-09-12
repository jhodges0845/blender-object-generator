# Asset Assistant Roadmap

This is the working source of truth for current development priorities. Keep implemented behavior, automated coverage, manual verification, and future work clearly separated.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It should remove repetitive and technical friction without replacing the artist. Generated assets are starting points, not mandatory session roots: artists should be able to generate or reopen/import an editable asset, attach reusable assets, work on animations independently, save checkpoints, and continue later.

The intended architecture is:

`Host-independent asset core -> provider/source -> Blender adapter -> editable working state -> validation/preparation -> target adapter -> exported asset -> artist review`

The project is broader than Human generation. The provider/capability model is intended to support characters, creatures, props, printable assets, reusable components, and animation assets without making shared workflow code assume humanoid anatomy.

See `docs/editable-asset-workflow.md` for the working-state/import/component/animation direction.

## Engineering guardrails

- `object_core` remains independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific implementation.
- `humanoid_blender` remains only as a compatibility entry point/module ID where required.
- Generic workflow code follows explicit provider capabilities rather than anatomy assumptions.
- Shared Modify code owns transport/planning/preservation, while providers own anatomy and semantic interpretation.
- Validation reports real limitations instead of manufacturing a green result.
- A successful file write is not equivalent to destination certification.
- Generated Blender data should remain editable by artists.
- Generation is one asset source; imported/reopened assets must be supported through explicit validation/adoption rather than guessed ownership.
- Editable working state is separate from destination export. `.blend` is the initial canonical working/checkpoint format; GLB/FBX/STL/3MF remain delivery formats.
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
- [x] strengthened neutral facial landmarks for nose bridge/tip, mouth/lips, eye recess, brow, chin, jaw taper, and cheek breadth;
- [x] front/side Blender review confirming the earlier head and face passes improved the base;
- [ ] visually review the strengthened landmark pass before deciding whether further base-face geometry is justified;
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
- [x] component inspection/request transport and validated single-component removal through external Modify;
- [x] automated core/Blender coverage plus a real Human round-trip manual checkpoint.

Still required for the richer product goal:

- [ ] improve Human reusable base geometry enough that semantic edits can produce recognizable character identity;
- [x] define first-class attachable component architecture for hair, clothing, and accessories;
- [x] keep optional component physics as adapter-facing behavior rather than ordinary Human body semantics;
- [x] add component persistence, ownership, inspection, rigid/skinned lifecycle, and safe Modify removal rules;
- [ ] add editable working-asset save/reopen and imported component adoption before building real component catalogs;
- [ ] promote animations to first-class assets and add preservation-aware animation Modify;
- [ ] validate generic Avian -> specific bird and generic Human -> specific character workflows end-to-end at useful visual quality.

## Component foundation — complete, real component catalogs intentionally paused

Hair, clothing, and accessories are first-class attachable components rather than Human body semantics. The foundation now includes portable records, rigid and parent-rig-skinned attachment, stable ownership metadata, inspection/tamper detection, safe remove/replace lifecycle operations with rollback, component state in Modify exchange, and safe external Modify removal.

Real hair/clothing/accessory providers are intentionally paused until the editable asset/import/animation foundation below is complete. Components should be reusable imported assets as well as generated assets; the architecture must not force a generate-only workflow.

## Editable asset persistence, import, and animation stage — active next stage

Goal: allow artists to stop and resume work without regeneration, build characters from reusable imported assets, and tune animations through the same preservation-aware workflow used for model Modify.

Current order:

1. [ ] Add explicit editable working-asset save/checkpoint with `.blend` as the initial canonical format while keeping destination export separate.
2. [ ] Add reopen/import validation for Asset Assistant `.blend` working assets and restore/inspect provider, ownership, component, rig, animation, and Modify state.
3. [ ] Add imported component registration/adoption so artist-authored reusable hair/clothing/accessory assets can enter the existing component lifecycle without being generated by a provider.
4. [ ] Define first-class portable animation records: stable ID, name/export name, provenance, rig compatibility, frame/FPS/loop/root-motion intent, and ownership.
5. [ ] Add animation import/add/remove/replace lifecycle operations without regenerating the base asset.
6. [ ] Add animation inspection/request transport and preservation-aware Modify planning.
7. [ ] Implement a narrow first set of executable animation tuning semantics through provider/capability-owned interpretation rather than Human assumptions.
8. [ ] Run a manual and automated save -> reopen -> component edit -> animation edit -> save -> engine export checkpoint.
9. [ ] Resume real hair/clothing/accessory catalogs/providers only after this checkpoint.

## Performance and test-health checkpoint

A dedicated performance/test audit was opened after the recent rich-Modify and Human geometry growth. See `docs/performance-test-audit.md`.

Current findings/actions:

- [x] identified duplicated CI discovery/execution: Python jobs were discovering Blender tests and Blender jobs were re-running the complete core suite;
- [x] scope standalone Python jobs to `tests/core` and Blender jobs to `tests/blender` while retaining all six required matrix checks;
- [x] add an `object_core` line-coverage report on Python 3.12 to establish a quantitative baseline without imposing an arbitrary threshold;
- [x] confirm rich Modify inspection remains operator-triggered rather than Blender panel redraw-triggered;
- [ ] compare CI durations across several PRs after the suite split;
- [ ] profile representative Human/Avian generation and Modify inspection/apply latency before changing preservation checks;
- [ ] add informational performance instrumentation only where measurements are stable enough to avoid flaky CI.

## Hair, clothing, accessories, and physics direction

Hair, clothing, and accessories should be reusable assets that can be imported and attached to a base asset later. Generation may be offered as one source, but it must not be required.

Planned separation:

- Human: body/facial geometry, skin/material foundation, skeleton/weights, attachment context;
- Hair: independent hairstyle asset geometry/materials plus optional dynamic metadata;
- Clothing: independent garment asset geometry/materials plus rig/weight and optional cloth/collision metadata;
- Accessories: independent rigid or skinned assets;
- Host/engine adapters: translate optional physics intent into Blender/Godot/Unity/Unreal behavior.

No component operation should advertise itself as executable unless the required geometry/weight source and ownership/preservation path exist.

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

## Current checkpoint — editable continuity before component catalogs

The component architecture foundation is complete enough to support rigid and parent-rig-skinned assets safely, but the product should not move directly into generated hair/clothing catalogs. The next architectural checkpoint is continuity: save/reopen an editable Asset Assistant working state, adopt reusable imported component assets, and make animation a first-class editable/Modify-able asset.

Current order:

1. [x] Complete provider foundations for Human, Quadruped, and Avian.
2. [x] Complete preservation-aware model Modify transport, external handoff, and persistent semantic patch architecture.
3. [x] Complete structural Asset Assistant UI organization.
4. [x] Implement Avian and Human semantic geometry apply.
5. [x] Define and implement first-class rigid/skinned component architecture and safe lifecycle/Modify-removal foundation.
6. [ ] Implement editable `.blend` save/checkpoint and validated reopen/import workflow.
7. [ ] Implement reusable imported component adoption/registration.
8. [ ] Promote animations to first-class portable assets with independent lifecycle and Modify workflow.
9. [ ] Complete save/reopen/component/animation continuity regression and manual checkpoint.
10. [ ] Return to Human visual-quality refinement and real hair/clothing/accessory providers.
11. [ ] Re-run end-to-end Avian and Human external Modify proofs at the intended visual-quality bar.
12. [ ] Run full cross-provider regression, preservation, architecture, docs, and final test-coverage audit.
13. [ ] Resume final release hardening and clean packaged-install smoke test in Blender 5.2.1.
14. [ ] Make an explicit version/tag decision and publish a public alpha only when approved.

### Shared follow-ups

- Human Run animation-quality tuning should move through the first-class animation Modify workflow where practical: upper-arm swing, knee lift, torso pitch, and timing/phase polish.
- Additional Avian gait/flight quality polish only if future visual review exposes a real issue.
- Quadruped semantic executor.
- Reusable UV/material/validation infrastructure only when additional real provider needs justify it.
- Watertight print-preparation work for providers that explicitly support 3D printing.
- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- Broader destination certification beyond the evidence needed for the first alpha.

## Near-term release milestone

> Asset Assistant can create or reopen useful editable starting assets across supported body plans; preserve reusable attached assets and independent animations across working sessions; inspect and richly modify model and animation state through preservation-aware workflows; keep provider/source logic out of shared workflow code; validate truthfully; export through supported targets without sacrificing the editable working state; and leave the result ready for continued artist or game-engine refinement.
