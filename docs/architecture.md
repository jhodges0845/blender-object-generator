# Architecture

## Core

`humanoid_core` owns character generation and has no host application dependency.
Its `models` package defines shared data contracts. Proportions, geometry,
rigging, and animation packages will implement their respective generation
steps using those contracts. Shared models must not import generation code or
adapters. No core module may import `humanoid_blender` or `bpy`.

Keep the public entry points in `humanoid_core/__init__.py` small. They currently
export `BodyType`, `HumanoidSpec`, `HumanoidProportions`, `MeshPart`,
`HumanoidMesh`, `generate_proportions`, and `generate_mesh`, so callers do not need to know where their
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
remains reserved. Blender translation lives in
`humanoid_blender/adapter.py`; its sidebar lives in `ui.py`.

The mesh and skeleton share joint coordinates from `proportions/landmarks.py`.
The Blender rig adapter turns core bone data into an armature and full weights;
it does not calculate body dimensions or joint placement.
