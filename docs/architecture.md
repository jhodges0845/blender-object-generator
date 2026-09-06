# Architecture

## Core

`object_core` owns object generation and has no host application dependency.
Its `models` package defines shared data contracts. Proportions, geometry,
rigging, and animation packages will implement their respective generation
steps using those contracts. Shared models must not import generation code or
adapters. No core module may import `humanoid_blender` or `bpy`.

`objects.py` registers providers with parameter definitions, mesh generation,
and explicit rig/idle capabilities. Humanoid wraps the existing proportion,
geometry, skeleton and idle generators; Box supplies a static mesh. Blender
constructs input controls from provider fields and dispatches using saved
object_type metadata. Unsupported types fail explicitly. Add a provider and
register it to add a type; no Blender body-generation rules are needed.

The shared mesh contract is ObjectMesh. Python imports now use object_core;
the former humanoid_core package was renamed. Blender's internal module ID and
operator names remain stable for saved-file compatibility. New roots use
object_generator metadata; legacy humanoid_blockout roots remain recognized.

Keep the public entry points in `object_core/__init__.py` small. They currently
export `BodyType`, `HumanoidSpec`, `HumanoidProportions`, `MeshPart`,
`ObjectMesh`, `generate_proportions`, and `generate_mesh`, so callers do not need to know where their
implementation lives. The specification now lives in `models/spec.py`.

## Adapters

`humanoid_blender` translates core data into Blender objects and provides
Blender UI integration. Blender-specific code belongs here. It may import the
core; the core must never import it. Future software adapters should be sibling
packages with the same dependency direction.

Importing the core must never require Blender or initialize a scene. The Blender
package provides an add-on entry point and sidebar operator. Its ZIP bundles
the independent core automatically, without a manually maintained second copy.

## Tests

Tests mirror the code boundaries: `tests/core/models` currently covers the input
contract. Add tests alongside each future core component under `tests/core`.
Nested test folders contain `__init__.py` so Python 3.9 unittest discovery finds
them. Keep Blender-dependent integration tests under `tests/blender`; when those
are introduced, run them with Blender and ensure ordinary Python discovery skips
them explicitly when Blender is unavailable.

From the repository root, run all current tests with:

```shell
python -m unittest discover -s tests -v
```

Run just core tests with:

```shell
python -m unittest discover -s tests/core -v
```

The input contract, proportion generator, and blockout mesh generator are implemented. Shared proportion
data lives in `models/proportions.py`; calibration and calculation live in the
`proportions` package. Mesh data lives in `models/mesh.py`; mesh construction
lives in `geometry`. Geometry consumes proportions and does not recalculate
them from the input specification. Rigging generates independent bone data and rigid part assignments. Animation
generates time-based rotation tracks in rest armature coordinates. Blender translation lives in
`humanoid_blender/adapter.py`; its sidebar lives in `ui.py`.

The mesh and skeleton share joint coordinates from `proportions/landmarks.py`.
The Blender rig adapter turns core bone data into an armature and full weights;
it does not calculate body dimensions or joint placement.

Readiness policy lives in `object_core/validation`, operating on an
`AssetSnapshot` data contract. Blender-specific inspection of material slots,
image nodes, modifiers, and actions lives in `humanoid_blender/validation.py`.
The UI stores validation snapshots separately from generated mesh data.
`workflow.py` operates on an existing chosen character; rigging rolls back its
own partial resources on failure without deleting that character.


## Target adapters

`Generate -> Rig -> Animate -> Core Validation -> Target Profile -> Blender Target Adapter -> Prepare -> Export -> Target Review`

`object_core/targets.py` owns destination profiles and `validate_for_target()`.
`humanoid_blender/targets.py` owns a shared `BlenderOutputAdapter` lifecycle,
Godot, Unity, Unreal and Cura adapters, registry lookup, and immutable
`ExportResult`. Unity and Unreal share FBX option construction while keeping
separate axis configurations. Cura reads evaluated geometry and writes binary
STL through `printing.py`, converting scene units to millimetres. `PRINT_3D`
remains an alias for the Cura core profile so existing callers keep working.

Game adapters snapshot the exact root hierarchy through `inspect_objects()`.
Cura builds a geometry-only `AssetSnapshot` from the evaluated current pose;
materials, rigs and clips are not requirements for its STL payload. It checks
closed oriented geometry, volume, connected components and non-adjacent face
intersections. It does not claim a complete printability proof. All adapters run
core validation before host-specific checks, without importing Blender into core.

`prepare()` remains read-only. The UI exposes a separate undoable material
preparation operator, which fills missing assignments and copies shared mesh data
when needed. It preserves existing materials. Export temporarily selects the
hierarchy and restores selection, active object and frame in `finally`.

The Export tab evaluates current readiness, and the operator checks again on
execution after file selection. Stored Validation results do not authorize an
export. ERROR and WARN block export; INFO contains design notes and destination
review guidance, never false PASS claims. Missing game materials are now errors.
Blockout metadata only produces an informational note for actual multipart
blockouts; the Box is not flagged as a multipart character.

The UI's Static/Rigged/Animated selection creates a local profile copy. Cura
always uses static geometry validation. The bundled-core import bridge supports
both checkout and ZIP installations. No core generator changes are needed to add
another target adapter.

The five workflow panels share a layout mixin with a fixed stage per panel.
Each registers its own Blender sidebar category (Generator, Rigging, Animations,
Validation, Export). The old workflow_tab setting remains for saved-file/script
compatibility but no longer controls visible navigation.
