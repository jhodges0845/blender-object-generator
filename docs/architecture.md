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
- `geometry/`: generated mesh data, including legacy and Human 1.0 deformable geometry;
- `rigging/`: skeleton and skin-weight generation;
- `animation/`: portable animation tracks/generators;
- `validation/`: host-independent readiness rules;
- `providers/`: concrete provider implementations plus shared provider parameter contracts;
- `objects.py`: provider declaration validation, registry construction, and lookup; and
- `targets.py`: destination profiles and target-level requirements.

The public `object_core` entry points should stay small. New implementation detail should not be promoted into the root API without a caller need.

## Provider boundary

Providers declare what operations they actually support. Current shared architecture has exercised three useful shapes:

- static assets with no rig/animation requirement;
- rigid animated assets; and
- skin-weight deforming assets.

Concrete provider implementations live under `object_core/providers` rather than inside the shared registry. `object_core.objects` validates declarations and resolves registered providers without owning Human or Box generation behavior. Existing imports from `object_core.objects` remain available as compatibility re-exports.

Deforming providers explicitly supply skin weights. Human-specific geometry, bone names, landmarks, and weighting heuristics stay in Human-focused implementation rather than leaking into generic workflow code.

Future capabilities such as UV generation or provider-specific surfacing should be added only when implementation requires them, not predeclared speculatively.

## Blender adapter boundary

`blender_adapter` is the canonical Blender-specific source package. It translates core contracts into editable Blender objects and owns Blender scene inspection, UI, rigging application, animation application, material preparation, validation inspection, and export orchestration.

`humanoid_blender` remains as a compatibility entry point/module ID for historical Blender/add-on identifiers. New Blender implementation should live in `blender_adapter`; compatibility code should stay thin and should not become a second implementation.

The adapter may import `object_core`; the core may never import the adapter.

## Generated-data principle

Asset Assistant should create ordinary editable Blender data wherever practical. Removing the add-on should not make generated meshes, armatures, materials, actions, or vertex groups unusable.

Generation parameters are inputs to generation, not a requirement that artists continue editing through Asset Assistant afterward.

## Human 1.0 architecture

Human currently has two paths:

- a legacy multipart/rigid path kept for compatibility and pipeline smoke testing; and
- an opt-in connected deforming path used for Human 1.0.

The deforming path reuses the existing Human proportion foundation, generates one connected mesh, creates a separate deforming skeleton, generates deterministic localized skin weights, and lets `blender_adapter` apply those results to Blender.

This split is intentional while Human 1.0 is being completed. Shared provider/workflow code should depend on capabilities and contracts rather than branching on Human anatomy.

## Validation boundary

Core validation operates on host-independent snapshot/contracts. Blender-specific inspection reads real Blender state such as objects, materials, image references, modifiers, actions, and vertex groups, then maps that state into validation data.

Validation must remain truthful. Stored validation results are informational snapshots; export revalidates current scene state rather than treating an old green result as authorization.

## Target adapters

The destination flow is:

`Generate -> optional Rig -> optional Animate -> Surface -> Validate -> Target Profile -> Blender Target Adapter -> Export -> Destination Review`

`object_core/targets.py` owns destination profiles and target-independent requirements. `blender_adapter/targets.py` owns Blender-side Godot, Unity, Unreal, and Cura export behavior.

Current defaults are:

- Godot: GLB/glTF;
- Unity: FBX;
- Unreal: FBX; and
- Cura: STL.

Target adapters should preserve source scene state where practical, scope exports to the intended hierarchy, and avoid turning a successful file write into a claim of production readiness.

## Tests and compatibility

Tests mirror the boundaries:

- standalone/core tests under `tests/core`;
- Blender integration tests under `tests/blender`;
- CI on Python 3.9-3.12; and
- Blender integration on 2.92.0 and 5.2.1.

Blender-dependent tests explicitly skip during ordinary Python discovery. CI additionally runs inside both Blender versions and exercises packaged-add-on/export paths.

The historical `humanoid.*` operator identifiers and `humanoid_blender` module compatibility exist because saved Blender data/scripts may reference them. Renaming those compatibility identifiers is a migration problem, not ordinary cleanup.

## Architecture rule of thumb

When adding a feature, ask in this order:

1. Is this host-independent asset behavior? Put it in `object_core`.
2. Is this Human/provider-specific behavior? Keep it with that provider/component rather than generic workflow code.
3. Is this Blender translation or scene behavior? Put it in `blender_adapter`.
4. Is this destination-specific behavior? Keep it in the relevant target adapter/profile.
5. Is a new abstraction required by more than one real implementation? If not, prefer the simpler concrete boundary.

Future architecture cleanup should remain evidence-driven: remove concrete duplication or boundary confusion when a real feature exposes it, rather than building speculative framework layers ahead of need.
