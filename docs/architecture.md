# Architecture

Asset Assistant separates host-independent asset logic from Blender integration and from destination-specific export behavior.

The current high-level flow is:

`object_core -> provider -> blender_adapter -> validation/preparation -> target adapter -> exported asset`

The architecture is intentionally capability-driven. Shared workflow code should not assume that every asset is Human, rigged, animated, deforming, printable, or destined for the same application.

## Core boundary

`object_core` owns host-independent data contracts and generation logic. It must not import `bpy`, `blender_adapter`, or `humanoid_blender`.

Important areas include:

- `models/`: immutable shared contracts;
- `proportions/`: Human measurements and shared landmarks;
- `geometry/`: shared/legacy mesh generation;
- `rigging/`: shared/legacy skeleton and skin-weight generation;
- `animation/`: portable animation contracts/shared generation;
- `validation/`: host-independent readiness rules;
- `providers/`: concrete provider implementations and anatomy-specific geometry, rigging, surfacing and animation behavior;
- `objects.py`: provider declaration validation, registry construction, and lookup; and
- `targets.py`: destination profiles and target-level requirements.

The public `object_core` entry points should stay small. New implementation detail should not be promoted into the root API without a caller need.

## Provider boundary

Providers declare what operations they actually support. Current shared architecture has exercised three useful shapes:

- static assets with no rig/animation requirement;
- rigid animated assets; and
- skin-weight deforming assets across both Human and quadruped anatomy.

Concrete provider implementations live under `object_core/providers` rather than inside the shared registry. `object_core.objects` validates declarations and resolves registered providers without owning Human, quadruped, or Box generation behavior. Existing imports from `object_core.objects` remain available as compatibility re-exports.

Animation capabilities are explicit. Idle, Walk/locomotion, and Run each have independent provider flags. A provider declaring Run must also support rigging and implement `run(duration, strength)`. Shared Blender UI and operators consume those capabilities rather than checking anatomy or provider keys.

Deforming providers explicitly supply skin weights. Anatomy-specific geometry, bone names, landmarks, UV/surface choices, weighting heuristics and motion generation stay with their provider rather than leaking into generic workflow code. Shared contracts should grow only when more than one real implementation exposes the same need.

## Public names and compatibility identities

The artist-facing Generator exposes **Human**, **Quadruped**, and **Box**. Public labels are product/UI concepts; provider keys are persisted compatibility identities.

The current Human key remains `human_experimental`, and the current Quadruped implementation remains keyed as `dog`. The historical `humanoid` provider also remains registered internally so older generated assets can still resolve their provider even though Humanoid is no longer offered for new generation.

Changing or removing those internal keys is therefore a migration problem, not ordinary naming cleanup. New code should not leak compatibility identifiers into artist-facing UI merely because the stored keys remain stable.

## Quadruped architecture proof

The current Quadruped provider validated the provider boundary with genuinely non-Human anatomy. Its implementation is still dog-oriented and supplies connected quadruped geometry, skeleton, spatial skin weights, UVs, portable material/texture intent and Idle/Walk/Run clips entirely from the host-independent provider layer.

The existing generic Blender path generates the Quadruped, applies its armature and vertex groups, translates its animation clips, prepares its material/texture and exposes its workflow through the dynamic provider UI without a provider-specific Blender branch. This is the desired architectural result: new anatomy changes provider logic while the host adapter continues translating shared contracts.

The implementation also exposed useful concrete refinements without requiring a framework rewrite: hind-leg/tail parenting was corrected to blend through the deforming spine, and the material milestone exposed the need for quadruped UVs. Both fixes remained provider-specific because no new shared abstraction was required.

Bird should follow the same rule: reuse existing contracts where they fit, but keep avian geometry/rigging/motion concrete until a repeated cross-provider need is demonstrated.

## Blender adapter boundary

`blender_adapter` is the canonical Blender-specific source package. It translates core contracts into editable Blender objects and owns Blender scene inspection, UI, rigging application, animation application, material preparation, validation inspection, and export orchestration.

`humanoid_blender` remains as a compatibility entry point/module ID for historical Blender/add-on identifiers. New Blender implementation and primary tests should use `blender_adapter`; compatibility code should stay thin and should not become a second implementation. Historical import paths get focused regression coverage rather than serving as the canonical API in new tests.

The adapter may import `object_core`; the core may never import the adapter.

## Generated-data principle

Asset Assistant should create ordinary editable Blender data wherever practical. Removing the add-on should not make generated meshes, armatures, materials, actions, or vertex groups unusable.

Generation parameters are inputs to generation, not a requirement that artists continue editing through Asset Assistant afterward.

## Human architecture

Human retains a legacy multipart/rigid compatibility path plus the connected deforming public Human path. The deforming path reuses the Human proportion foundation, generates one connected mesh, creates a dedicated skeleton and deterministic localized skin weights, and lets `blender_adapter` apply those portable results. UV, material, generated-image texture, Idle, Walk, and Run intent remain outside Blender and are translated into ordinary editable Blender data by the adapter.

Shared provider/workflow code depends on capabilities and contracts rather than branching on Human anatomy.

## Validation boundary

Core validation operates on host-independent snapshot/contracts. Blender-specific inspection reads real Blender state such as objects, materials, image references, modifiers, actions, and vertex groups, then maps that state into validation data.

Validation must remain truthful. Stored validation results are informational snapshots; export revalidates current scene state rather than treating an old green result as authorization.

## Target adapters

The destination flow is:

`Generate -> optional Rig -> optional Animate -> Surface -> Validate -> Target Profile -> Blender Target Adapter -> Export -> Destination Review`

`object_core/targets.py` owns destination profiles and target-independent requirements. `blender_adapter/targets.py` owns Blender-side Godot, Unity, Unreal, and Cura export behavior, including Blender-version-specific exporter options when required.

Current defaults are Godot GLB/glTF, Unity FBX, Unreal FBX, and Cura STL. Target adapters should preserve source scene state where practical, scope exports to the intended hierarchy, and avoid turning a successful file write into a claim of production readiness. Version-specific Blender behavior belongs at this adapter boundary rather than in `object_core` or provider logic.

## Tests and compatibility

Tests mirror the boundaries:

- standalone/core tests under `tests/core`;
- canonical Blender integration tests under `tests/blender`;
- focused compatibility-import coverage for `humanoid_blender`;
- CI on Python 3.9-3.12; and
- Blender integration on 2.92.0 and 5.2.1.

Quadruped adds focused Blender coverage for generic provider generation/rigging, evaluated surface deformation, animation and material/UV translation. This complements Human's deeper geometry/export coverage and demonstrates that the shared Blender path is not accidentally Human-only.

Blender 5.2.x is the primary current runtime target. Older Blender compatibility is valuable and should be retained while it remains reasonably small, clean, and testable. Current-version correctness and a clean architecture take precedence over preserving an old runtime indefinitely. If an older Blender version begins forcing duplicated implementations, awkward cross-layer workarounds, or weaker current-version behavior, raise the minimum supported Blender version deliberately and document the migration rather than degrading the design.

Blender-dependent tests explicitly skip during ordinary Python discovery. CI additionally runs inside both Blender versions and exercises packaged-add-on/export paths. A version difference is acceptable only when the user-visible contract remains correct; tests should verify the contract rather than incidental exporter naming or implementation details.

The historical `humanoid.*` operator identifiers and `humanoid_blender` module compatibility exist because saved Blender data/scripts may reference them. Renaming those compatibility identifiers is a migration problem, not ordinary cleanup.

## Architecture rule of thumb

When adding a feature, ask in this order:

1. Is this host-independent asset behavior? Put it in `object_core`.
2. Is this provider-specific behavior? Keep it with that provider/component rather than generic workflow code.
3. Is this Blender translation or scene behavior? Put it in `blender_adapter`.
4. Is this destination-specific behavior? Keep it in the relevant target adapter/profile.
5. Is a new abstraction required by more than one real implementation? If not, prefer the simpler concrete boundary.

Future architecture cleanup should remain evidence-driven: remove concrete duplication or boundary confusion when a real feature exposes it, rather than building speculative framework layers ahead of need.
