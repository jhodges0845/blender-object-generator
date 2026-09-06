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
`humanoid_blender/targets.py` owns the small `BlenderOutputAdapter` base,
registry, `GodotAdapter`, and immutable `ExportResult`. Lookup distinguishes
unknown core targets from known targets whose Blender adapter is unimplemented.
Unity, Unreal Engine, and 3D Print adapters are planned; no placeholder exporters
are registered. Adding an adapter does not change core generation.

Godot reuses `validation.inspect_objects()` to snapshot the exact root hierarchy
and calls core target validation before adding host export checks. The existing
UI inspector retains its direct-child scope. Preparation is read-only. Export
only temporarily selects the hierarchy and restores selection, active object,
and frame even when the exporter raises. Mesh/rig/animation data is not baked,
rescaled or destructively altered. The bundled-core import bridge supports both
checkout and installed ZIP imports. No Blender imports were added to the core.

The core Godot profile still defaults to animated assets. An explicit adapter
`asset_use` creates a local dataclass copy for static or rigged output and runs
the same core rules; it never changes the shared target registry. Target warnings
remain in export results. A successful file export is not proof of Godot readiness.
