# Asset Assistant Roadmap

This is the working source of truth for current development priorities. Keep implemented behavior, automated coverage, manual verification, and future work clearly separated.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It should remove repetitive and technical friction without replacing the artist. Generated assets are starting points, not mandatory session roots: artists should be able to generate or reopen an editable asset, attach reusable assets, work on animations independently, save checkpoints, and continue later.

The intended architecture is:

`Host-independent asset core -> provider/source -> Blender adapter -> editable working state -> validation/preparation -> target adapter -> exported asset -> artist review`

The project is broader than Human generation. The provider/capability model supports characters, creatures, props, printable assets, reusable components, and animation assets without making shared workflow code assume humanoid anatomy.

See `docs/editable-asset-workflow.md`, `docs/production-character-roundtrip.md`, and `docs/editable-continuity-audit.md` for the current production workflow and checkpoint criteria.

## Engineering guardrails

- `object_core` remains independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific implementation.
- `humanoid_blender` remains only as a compatibility entry point/module ID where required.
- Generic workflow code follows explicit provider capabilities rather than anatomy assumptions.
- Shared Modify code owns transport/planning/preservation, while providers own anatomy and semantic interpretation.
- Validation reports real limitations instead of manufacturing a green result.
- A successful file write is not equivalent to destination certification.
- Generated Blender data should remain editable by artists.
- Generation is one asset source; imported/reopened assets enter through explicit validation/adoption rather than guessed ownership.
- Editable working state is separate from destination export. `.blend` is the initial canonical working/checkpoint format; GLB/FBX/STL/3MF remain delivery formats.
- Provider names and keys are canonical architecture identifiers; saved legacy identifiers are handled only through explicit compatibility mapping.
- Unsupported Modify operations remain explicit blockers rather than silent no-ops.
- Artist/imported curves, materials, rigs, NLA, drivers, and unrelated scene objects are never silently claimed.

## Completed platform foundation

- [x] Asset Assistant identity and GPL release packaging.
- [x] Host-independent `object_core` and canonical `blender_adapter` boundary.
- [x] Provider registry, parameter fields, and capability declaration validation.
- [x] Canonical Human, Quadruped, Avian, and Box providers.
- [x] Static, rigid animated, and skin-weight deforming provider paths.
- [x] Core validation plus Blender-specific inspection.
- [x] Godot, Unity, Unreal, and Cura target profiles/adapters.
- [x] GLB/glTF, FBX, and STL export paths.
- [x] Provider-aware rigging and capability-driven Idle / Walk / Run / Flight workflows where supported.
- [x] Blender 5.2 layered-action support and Blender 2.92 compatibility.
- [x] CI on Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Branch protection requiring all six CI checks before merge.
- [x] Godot, Unity, Unreal, and Cura smoke verification.
- [x] Redraw-time validation caching plus fresh export safety preflight.
- [x] Cura Human print preparation plus selectable print-scale presets.
- [x] Unified Asset Assistant sidebar organized around Generate / Modify / Rig / Animate / Validate / Export.
- [x] Reproducible tagged-release packaging automation implemented; no release/tag without explicit approval.

## Provider status

### Human — foundation complete, visual quality refinement active

Human has connected deformable geometry, dedicated skeleton and skin weights, editable UV/material/texture data, Idle/Walk/Run, automated deformation coverage, destination evidence, and rich topology-preserving semantic Modify.

Implemented semantic targets include body, torso, shoulders, head, face, jaw, cheeks, arms, and legs. Human is the primary proof target for production-character continuity.

Remaining Human work is quality, not architecture:

- [ ] visually review the latest base-face landmark pass;
- [ ] refine body/hand silhouette where real production review exposes limitations;
- [ ] grow animation semantics beyond global duration/strength when production use shows which controls matter.

### Quadruped — foundation complete

Quadruped proves the architecture with genuinely non-Human terrestrial anatomy: connected geometry, dedicated skeleton/weights, deformation coverage, Idle/Walk/Run, deterministic UVs, portable material intent, and generic Blender workflow/export coverage.

- [ ] provider-owned rich semantic executor remains a follow-up milestone.

### Avian — foundation complete plus rich semantic executor

Avian adds non-Human airborne anatomy and a distinct capability set: connected wings/tail/legs/feet, dedicated rig/weights, UV/material intent, Idle/Walk/Flight, no Run, and persistent topology-preserving semantic operations for body/chest/head/beak/wings/tail/legs/feet.

The shared workflow remains unaware of beaks/wings; those semantics stay provider-owned.

## Model Modify — implemented

Current workflow:

`Select Asset Assistant asset -> Export Inspection -> external edit -> Import Change File -> Preview/Review -> Apply -> revalidate`

Implemented:

- [x] portable inspection/snapshot/request/plan contracts;
- [x] stable asset/provider identity binding;
- [x] non-mutating preview followed by fresh revalidation on apply;
- [x] transactional provider-parameter regeneration with preservation blockers;
- [x] generated animation export-name metadata changes;
- [x] provider-owned semantic target manifests/execution;
- [x] persistent/replayable semantic patches;
- [x] Human and Avian semantic geometry execution;
- [x] safe composition/routing of parameter, semantic, and animation-name changes;
- [x] component state in external inspection plus validated component removal;
- [x] real Human external inspection -> returned request -> Blender apply proof.

Important limitation: machine-readable inspection describes procedural/ownership state, not rendered appearance. Production-character aesthetic refinement should pair JSON inspection with Blender viewport review/screenshots.

## Component foundation — implemented; real catalogs intentionally paused

Hair, clothing, and accessories are first-class attachable components rather than Human body semantics.

Implemented:

- [x] portable component records and physics intent;
- [x] rigid root/bone attachment;
- [x] parent-rig-skinned attachment;
- [x] stable ownership metadata and tamper detection;
- [x] safe remove/replace lifecycle with rollback;
- [x] component state in Modify exchange and safe external removal;
- [x] imported rigid artist mesh adoption;
- [x] imported parent-rig-skinned mesh adoption;
- [x] artist material ownership preservation.

Real generated/import catalogs remain paused until the editable-continuity manual checkpoint is accepted.

## Editable working state — implemented, manual acceptance pending

`.blend` is the canonical editable checkpoint format; destination exports remain separate.

Implemented:

- [x] **Save Editable Checkpoint (.blend)** in the existing Export workflow using copy-save so the current session path is unchanged;
- [x] checkpoint kind/version metadata;
- [x] **Open Editable Checkpoint (.blend)** entry path;
- [x] post-load reinspection/target restoration;
- [x] marked checkpoints now auto-validate even when opened through Blender File/Open or Recent Files;
- [x] component/Modify/rig/animation state survives ordinary `.blend` persistence through Blender data + Asset Assistant metadata.

Manual acceptance still required:

- [ ] real save -> reopen -> visual review through the installed sidebar workflow.

## First-class animation assets — implemented

Animations are no longer only one-shot generated clips.

Implemented:

- [x] portable `AnimationRecord` with stable ID, display/export name, provenance, rig signature, frame range, FPS, loop/root-motion intent, ownership, provider/capability;
- [x] generated Action persistence/inspection;
- [x] artist/imported Action registration without claiming curves;
- [x] preservation-aware add/register/remove/replace lifecycle;
- [x] managed animation scoping by compatibility **and owning Asset Assistant rig identity**;
- [x] rich animation state in external Modify inspection;
- [x] dedicated Animations-panel external refinement workflow;
- [x] non-mutating animation request preview;
- [x] executable generated-clip tuning for cycle duration/speed, motion strength, and export name;
- [x] stable animation ID preserved across regeneration;
- [x] other generated/artist Actions preserved when one clip is refined.

Future animation tuning should be provider/capability-specific and evidence-driven: gait/body-language controls, root motion, torso lean, arm swing, knee lift, contact timing, etc. Do not implement arbitrary shared quaternion-curve surgery.

## Current checkpoint — production-character editable continuity

The automated architecture is ready for the real artist pass.

Automated coverage now proves:

- [x] Human model inspection and semantic refinement;
- [x] first-class animation inspection/refinement;
- [x] stable asset/animation identity through refinement;
- [x] editable `.blend` checkpoint save contract;
- [x] engine export after the refinement sequence;
- [x] Blender 2.92.0 and 5.2.1 CI coverage;
- [x] native Blender load handler for marked checkpoint validation.

Manual checkpoint to perform before closing this phase:

`Generate Human -> save .blend -> reopen -> export model inspection -> external body request -> import -> preview -> visual review -> apply -> save -> reopen -> generate/select animation -> export animation inspection -> external animation request -> import -> preview -> apply -> play -> save -> reopen -> destination export`

Acceptance criteria:

- [ ] no lost provider/asset identity;
- [ ] active target restored after reopen;
- [ ] model Preview/Apply understandable in the real sidebar;
- [ ] visual body refinement can be iterated with JSON + screenshot feedback;
- [ ] animation Preview/Apply understandable in the real sidebar;
- [ ] stable animation identity survives the round trip;
- [ ] final engine export contains the expected refined asset/animations;
- [ ] no unrelated/artist-owned data is overwritten.

## Next phase after manual checkpoint — production components

Once the continuity pass succeeds, begin real reusable components rather than more framework work.

Suggested order:

1. Hair provider/import workflow with rigid/skinned attachment as appropriate.
2. Clothing workflow using parent-rig skinning and explicit material ownership.
3. Accessories using the existing rigid/bone attachment path.
4. Portable collision/physics intent for hair/clothing only after static ownership/attachment is reliable.
5. Use a real production character to expose missing component controls before generalizing further.

The component core must remain game/project-agnostic; named game characters are production validation targets, not special cases in shared code.

## Performance and test health

Previous audit work removed duplicated CI discovery/execution and added Python 3.12 `object_core` coverage reporting. Modify snapshot reuse reduced repeated expensive scene/provider inspection.

Remaining evidence-driven follow-ups:

- [ ] profile representative production Human model inspection/preview/apply if the manual workflow feels slow;
- [ ] profile animation inspection/preview/apply only if interactive use exposes latency;
- [ ] add performance instrumentation only where stable enough not to create flaky CI.

## Target verification and release hardening

Completed evidence:

- [x] repeatable target-verification checklist;
- [x] Godot GLB import/animation smoke check;
- [x] Unity FBX model/animation smoke check;
- [x] Unreal FBX model/animation smoke check;
- [x] Cura Box/Human STL path evidence;
- [x] Human Godot/Unity/Unreal checkpoints;
- [x] Quadruped Blender generation/rig/animation/material checkpoint;
- [x] Avian automated Godot/Unity animation packaging plus Blender visual review.

Before public alpha:

- [ ] detailed Cura representative-Human slicing/physical-print review;
- [ ] broader Quadruped/Avian destination certification where useful;
- [ ] full cross-provider preservation/architecture/docs/test-coverage audit;
- [ ] clean packaged-install smoke test in Blender 5.2.1;
- [ ] explicit version/tag/release decision;
- [ ] publish only with explicit approval.

## Shared follow-ups

- richer Human Run/Walk body-language controls through provider-owned animation Modify;
- additional Avian gait/flight polish only if visual review exposes a real issue;
- Quadruped semantic executor;
- reusable UV/material/validation infrastructure only when another real provider requires it;
- watertight print-preparation work only for providers that explicitly support printing;
- optional Godot `.tscn` packaging research while retaining GLB as the portable default;
- broader destination certification during release hardening.

## Near-term milestone

> Asset Assistant can create or reopen useful editable starting assets across supported body plans; preserve reusable attached assets and independent animations across working sessions; inspect and richly modify model and animation state through preservation-aware workflows; validate truthfully; export through supported targets without sacrificing the editable working state; and leave the result ready for continued artist or game-engine refinement.
