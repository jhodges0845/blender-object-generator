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
- [x] Idle, Walk, Flight, and Run capability-driven animation workflow where supported by each provider.
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

Avian is the second non-Human deforming-provider proof and now covers both airborne and ground locomotion.

The completed Avian foundation includes:

- [x] canonical `avian` / Avian provider identity and parameter contract
- [x] deterministic connected low-poly body with integrated wings, tail, legs, and feet
- [x] Avian spine/neck/head, upper/lower wing, tail, upper/lower leg, and foot skeleton
- [x] normalized local skin weights plus wing, neck/head, tail, leg, and foot deformation coverage
- [x] deterministic face-corner UVs and portable textured plumage material intent
- [x] provider-specific Idle, Walk, and Flight motion using the shared editable Blender action pipeline
- [x] distinct Walk and Flight clip identities; choosing Walk no longer creates Flight
- [x] Run intentionally unsupported for Avian
- [x] representative automated Godot GLB and Unity FBX export coverage for Avian skinning plus Idle/Walk/Flight packaging
- [x] interactive Blender 5.2.1 visual confirmation of Avian leg placement and Walk motion
- [x] documentation and architecture closeout confirming Avian anatomy stays provider-specific and target adapters remain provider-neutral

Broader destination import/playback certification is tracked under release hardening.

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
- [x] Avian interactive Blender visual-quality checkpoint for leg placement and Walk motion.
- [ ] Detailed Cura certification pass covering representative Human dimensions, orientation, slicing warnings, and physical-print considerations.
- [ ] Broader Quadruped and Avian destination certification across Godot/Unity/Unreal during release hardening.

## Current checkpoint — pre-release scope reopened

The provider foundation is stable enough to checkpoint. Release hardening had begun, but two product features are now explicit blockers for the first public alpha: **Modify** and a **UI overhaul**.

See `docs/pre-release-scope-checkpoint.md` for the checkpoint details.

### P0 — Modify workflow

Asset Assistant needs a first-class modification path for an existing generated asset instead of requiring regeneration for every meaningful change.

Target workflow:

`Select existing Asset Assistant asset -> Inspect / capture current state -> prepare requested changes -> apply targeted modification -> revalidate -> continue editing/exporting`

Requirements:

1. [ ] Define a structured inspection/snapshot contract for the current generated asset state.
2. [ ] Define the supported first-release modification set and preservation boundaries before wiring UI behavior.
3. [ ] Apply targeted changes without silently overwriting unrelated artist-authored animation, materials, or other edits.
4. [ ] Reuse host-independent/provider contracts where practical rather than embedding provider anatomy rules in generic Blender code.
5. [ ] Revalidate after modification and report unsupported/unsafe changes truthfully.
6. [ ] Add ordinary Python and Blender integration coverage for inspect -> modify -> preserve -> validate behavior.
7. [ ] Document the workflow and limitations clearly enough that an artist can use it without understanding internal scene metadata.

### P0 — UI overhaul

The current Blender UI grew incrementally with each capability. Before release it should be reorganized around the artist's workflow rather than the implementation history.

Requirements:

1. [ ] Establish a clear hierarchy around **Generate / Modify / Rig / Animate / Validate / Export**.
2. [ ] Make the current asset and current workflow step obvious.
3. [ ] Show provider-relevant actions and avoid presenting unsupported operations as normal choices.
4. [ ] Reduce repeated explanatory copy and visual clutter while retaining discoverability.
5. [ ] Keep advanced controls available without making the default workflow feel engineering-centric.
6. [ ] Review panel/category names against Blender's built-in UI to reduce naming confusion.
7. [ ] Preserve existing operator/data compatibility where required while allowing the visible UI to change substantially.
8. [ ] Run an interactive usability pass in Blender 5.2.1 before release.

## Revised pre-release order

1. [x] Checkpoint provider state and update documentation after Avian legs/Walk validation.
2. [ ] Design and implement the Modify workflow.
3. [ ] Design and implement the UI overhaul around Generate / Modify / Rig / Animate / Validate / Export.
4. [ ] Run a full cross-provider regression, preservation, architecture, and test-coverage audit.
5. [ ] Resume release hardening: installation, packaging, tagged release automation, documentation, and reproducible artifacts.
6. [ ] Run a clean packaged-install smoke test in Blender 5.2.1.
7. [ ] Publish the first public alpha only after the above blockers are complete.

### Shared follow-ups

- Human Run animation-quality tuning: upper-arm swing, knee lift, torso pitch and timing/phase polish.
- Additional Avian gait/flight quality polish only if future visual review exposes a real issue.
- Reusable UV/material/validation infrastructure only when additional real provider needs justify it.
- Watertight print-preparation work for providers that explicitly support 3D printing.
- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- Broader destination certification beyond the evidence needed for the first alpha.

## Near-term release milestone

> Asset Assistant can create useful editable starting assets across Human, Quadruped and Avian body plans, inspect and modify an existing generated asset through a preservation-aware workflow, present the end-to-end process through a coherent artist-facing UI, validate truthfully, export through supported targets, and leave the result ready for an artist to refine.
