# Architecture

Asset Assistant separates host-independent asset logic from Blender integration and from destination-specific export behavior.

The current high-level flow is no longer only one-shot generation/export. It is:

`object_core -> provider/component contracts -> blender_adapter -> editable .blend working state -> validation/preparation -> target adapter -> destination export`

An editable `.blend` checkpoint is the authoritative resumable working state. GLB/glTF, FBX, STL and other target formats are delivery formats, not replacements for the editable project state.

The architecture is intentionally capability-driven. Shared workflow code should not assume that every asset is Human, rigged, animated, deforming, printable, or destined for the same application.

## Core boundary

`object_core` owns host-independent data contracts and generation logic. It must not import `bpy`, `blender_adapter`, or `humanoid_blender`.

Important areas include:

- `models/`: immutable shared contracts;
- `proportions/`: Human measurements and shared landmarks;
- `geometry/`: shared/legacy mesh generation;
- `rigging/`: shared/legacy skeleton and skin-weight generation;
- `animation/` and `animations.py`: portable animation generation/record contracts;
- `components.py`: portable component identity, ownership, attachment and physics intent;
- `modification.py` and `modify_exchange.py`: host-independent Modify snapshots, plans and JSON transport;
- `validation/`: host-independent readiness rules;
- `providers/`: concrete provider implementations and anatomy-specific geometry, rigging, surfacing, semantic Modify and animation behavior;
- `objects.py`: provider declaration validation, registry construction, lookup, and narrow saved-key compatibility mapping; and
- `targets.py`: destination profiles and target-level requirements.

The public `object_core` entry points should stay small. New implementation detail should not be promoted into the root API without a caller need.

## Provider boundary

Providers declare what operations they actually support. Current shared architecture has exercised static, rigid/deforming, Human, quadruped and avian shapes rather than assuming a single anatomy.

Concrete provider implementations live under `object_core/providers` rather than inside the shared registry. `object_core.objects` validates declarations and resolves registered providers without owning Human, Quadruped, Avian, or Box generation behavior. Existing imports from `object_core.objects` remain available as compatibility re-exports.

Animation capabilities are explicit. Idle, locomotion/Walk, Run, and Flight are independent provider capabilities. Shared Blender UI and operators consume those capabilities rather than checking anatomy or provider keys.

Deforming providers explicitly supply skin weights. Anatomy-specific geometry, bone names, landmarks, UV/surface choices, weighting heuristics, semantic Modify rules and motion generation stay with their provider rather than leaking into generic workflow code. Shared contracts should grow only when more than one real implementation exposes the same need.

## Provider identities and compatibility

The canonical generation providers are **Human**, **Quadruped**, **Avian**, and **Box**. Canonical provider keys are the identities stored by new assets and used by new code.

The historical `humanoid` provider remains registered internally so older generated assets can still resolve their provider even though Humanoid is no longer offered for new generation. Earlier saved identifiers from provider renames are handled through a narrow compatibility mapping at lookup time rather than by preserving obsolete implementation names throughout the codebase.

## Cross-provider architecture proofs

Quadruped validated the provider boundary with genuinely non-Human terrestrial anatomy. It supplies connected quadruped geometry, skeleton, spatial skin weights, UVs, portable material/texture intent and Idle/Walk/Run clips entirely from the host-independent provider layer.

Avian extended the same architecture with another non-Human anatomy and a distinct capability set, including Flight while intentionally omitting Run. Its geometry, rigging, deformation, materials and animation remain provider-owned while the Blender adapter reuses the same generic workflow and export boundaries.

These are the desired architectural results: new anatomy changes provider logic while the host adapter continues translating shared contracts. Shared abstractions are added only where repeated needs are proven.

## Blender adapter boundary

`blender_adapter` is the canonical Blender-specific source package. It translates core contracts into editable Blender objects and owns Blender scene inspection, UI, rigging application, animation application, component adoption, checkpoint persistence/reopen validation, Modify transport integration, material preparation, validation inspection, and export orchestration.

`humanoid_blender` remains as a compatibility entry point/module ID for historical Blender/add-on identifiers. New Blender implementation and primary tests should use `blender_adapter`; compatibility code should stay thin and should not become a second implementation. Historical import paths get focused regression coverage rather than serving as the canonical API in new tests.

The adapter may import `object_core`; the core may never import the adapter.

## Generated-data and ownership principles

Asset Assistant should create ordinary editable Blender data wherever practical. Removing the add-on should not make generated meshes, armatures, materials, Actions, or vertex groups unusable.

Generation parameters are reproducible inputs, not a requirement that artists continue editing only through Asset Assistant. Ownership metadata exists so destructive automation knows what it may safely replace.

Artist/imported data is preservation-first. Asset Assistant must not silently claim artist materials, curves, rigs, NLA, drivers, or unrelated scene objects. Explicit adoption/registration records the ownership boundary before lifecycle operations become available.

## Components

Hair, clothing and accessories are independent attachable components rather than Human body semantics. Portable component records live in the core; Blender owns the actual object parenting, Armature modifiers, weights and persistence metadata.

Rigid and parent-rig-skinned imported component adoption are implemented. Adoption transfers geometry ownership explicitly while preserving artist material ownership. Remove/replace paths are transactional and must preserve the parent character rig and unrelated scene data.

Future component physics belongs on top of these portable component/ownership contracts rather than being baked into Human generation.

## Animation architecture

Animations are first-class assets with stable IDs independent of Blender Action names. Portable records describe provenance, rig compatibility, timing/FPS, looping, root-motion intent and curve ownership.

Generated clips are Asset Assistant-owned and reproducible from provider capability + generation parameters. Artist/imported Actions can be registered without transferring curve ownership. Managed Actions are scoped to both rig compatibility and the owning Asset Assistant rig identity; rig shape alone is insufficient because multiple characters may share the same skeleton topology.

External animation Modify uses a dedicated inspection/request workflow. The first executable tuning surface regenerates one owned generated clip from explicit duration/strength inputs while preserving stable identity and every other Action. Arbitrary artist curve editing remains outside that ownership boundary.

## Editable working-state boundary

`.blend` is currently the canonical editable checkpoint format because it preserves objects, armatures, Actions, modifiers, vertex groups, materials, ownership metadata, component records and future physics state.

Saving an editable checkpoint uses Blender's copy-save behavior so the active session path does not change. Reopening a checkpoint validates the saved Asset Assistant marker/version, re-inspects recognizable assets, restores the active target when unambiguous, and reports unsupported/tampered state instead of silently accepting it.

Generation is therefore one entry path, not the session root. The intended workflow is:

`Generate OR reopen checkpoint -> inspect/modify -> attach/replace components -> add/refine animations -> save checkpoint -> destination export -> reopen later and continue`

## Human architecture

Human retains a legacy multipart/rigid compatibility path plus the connected deforming public Human path. The deforming path reuses the Human proportion foundation, generates one connected mesh, creates a dedicated skeleton and deterministic localized skin weights, and lets `blender_adapter` apply those portable results. UV, material, generated-image texture, Idle, Walk, Run and semantic body/face refinement intent remain outside Blender and are translated into ordinary editable Blender data by the adapter.

Shared provider/workflow code depends on capabilities and contracts rather than branching on Human anatomy.

## Validation boundary

Core validation operates on host-independent snapshot/contracts. Blender-specific inspection reads real Blender state such as objects, materials, image references, modifiers, Actions, component metadata, ownership and vertex groups, then maps that state into validation data.

Validation must remain truthful. Stored validation results are informational snapshots; export revalidates current scene state rather than treating an old green result as authorization. Returned external Modify requests are also revalidated against current asset identity/state before mutation.

## Target adapters

The destination flow is:

`Editable working state -> Validate -> Target Profile -> Blender Target Adapter -> Export -> Destination Review`

Generation/rigging/animation may have happened earlier in the session or in a previous session reopened from `.blend`.

`object_core/targets.py` owns destination profiles and target-independent requirements. `blender_adapter/targets.py` owns Blender-side Godot, Unity, Unreal, and Cura export behavior, including Blender-version-specific exporter options when required.

Current defaults are Godot GLB/glTF, Unity FBX, Unreal FBX, and Cura STL. Target adapters should preserve source scene state where practical, scope exports to the intended hierarchy, and avoid turning a successful file write into a claim of production readiness. Version-specific Blender behavior belongs at this adapter boundary rather than in `object_core` or provider logic.

## Tests and compatibility

Tests mirror the boundaries:

- standalone/core tests under `tests/core`;
- canonical Blender integration tests under `tests/blender`;
- focused compatibility-import coverage for `humanoid_blender`;
- CI on Python 3.9-3.12; and
- Blender integration on 2.92.0 and 5.2.1.

Cross-provider tests exercise Human, Quadruped and Avian generation/rigging/deformation/animation/material/export behavior. Editable-continuity tests additionally cover component adoption/lifecycle, animation lifecycle/Modify, checkpoint save contracts and a production-style Human refinement-to-engine-export round trip.

Blender 5.2.x is the primary current runtime target. Older Blender compatibility is valuable and should be retained while it remains reasonably small, clean, and testable. Current-version correctness and a clean architecture take precedence over preserving an old runtime indefinitely. If an older Blender version begins forcing duplicated implementations, awkward cross-layer workarounds, or weaker current-version behavior, raise the minimum supported Blender version deliberately and document the migration rather than degrading the design.

Blender-dependent tests explicitly skip during ordinary Python discovery. CI additionally runs inside both Blender versions and exercises packaged-add-on/export paths. A version difference is acceptable only when the user-visible contract remains correct; tests should verify the contract rather than incidental exporter naming or implementation details.

The historical `humanoid.*` operator identifiers and `humanoid_blender` module compatibility exist because saved Blender data/scripts may reference them. Renaming those compatibility identifiers is a migration problem, not ordinary cleanup.

## Architecture rule of thumb

When adding a feature, ask in this order:

1. Is this host-independent asset behavior? Put it in `object_core`.
2. Is this provider-specific behavior? Keep it with that provider/component rather than generic workflow code.
3. Is this Blender translation, persistence, inspection, scene behavior or UI? Put it in `blender_adapter`.
4. Is this destination-specific behavior? Keep it in the relevant target adapter/profile.
5. Is a new abstraction required by more than one real implementation? If not, prefer the simpler concrete boundary.

Future architecture cleanup should remain evidence-driven: remove concrete duplication or boundary confusion when a real feature exposes it, rather than building speculative framework layers ahead of need.
