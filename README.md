# Humanoid core — pieces 1 through 4

A small, software-independent foundation for generating editable character
starting points for artists. The core defines validated inputs and calculates
stylized adult body proportions and a low-poly humanoid blockout mesh. The Blender adapter creates editable scene objects. Rigging and animation are
not implemented yet.

## Use

Supports Python 3.7 or newer (tested with standalone Python 3.9 and Blender 2.92's Python 3.7.7). From this folder:

```python
from humanoid_core import BodyType, HumanoidSpec, generate_proportions, generate_mesh

character = HumanoidSpec(
    height_cm=180,
    weight_kg=95,
    body_type=BodyType.OVERWEIGHT,
)

dimensions = generate_proportions(character)
print(dimensions.waist_width_cm)
print(dimensions.standing_height_cm)
mesh = generate_mesh(dimensions)
print(mesh.vertex_count, mesh.face_count)
```

The five artistic presets are `slim`, `average`, `muscular`, `overweight`, and
`obese`. Body type is selected explicitly and is not inferred from measurements.
An adapter can convert a UI string using `BodyType("overweight")`.

Height and weight accept positive, finite Python integers or floats and are
stored as floats. Invalid types raise `TypeError`; invalid numeric values raise
`ValueError`. Specifications are immutable. The initial proportion generator
supports 120–240 cm and 30–300 kg. See [the proportion rules](docs/proportions.md)
for measurement conventions and limitations. To compare all five presets, run
`python -m examples.proportions` from this folder.

Generate and inspect a blockout with
`python -m examples.mesh --body-type overweight`. It contains 15 separate,
closed parts in an A-pose; it is not yet suitable for skinning. See
[mesh conventions and limitations](docs/geometry.md) for details and JSON output.

## Blender add-on

The ready-to-install archive is `dist/humanoid_blockout.zip`. In Blender 2.92,
use Edit > Preferences > Add-ons > Install, select the ZIP, and enable
**Add Mesh: Object Generator**. In Object Mode, open the 3D Viewport sidebar
with N, open **Generator**, choose **Object Type: Humanoid**, set the inputs,
and click **Generate Blockout**.

See [installation, updating, uninstalling, and Blender testing](docs/blender.md)
for details. Rebuild with
`python -m scripts.build_blender_addon`.

## Test

No Blender installation or third-party test dependencies are needed:

```shell
python -m unittest discover -s tests -v
```

## Folder structure

```text
humanoid_core/             Independent generation library
    models/               Input and future output data contracts
        spec.py           HumanoidSpec and BodyType
    proportions/          Measurement-to-proportion rules and generator
    geometry/             Blockout generator and mesh primitives
    rigging/              Skeletons and skin weights (reserved)
    animation/            Motion generation (reserved)
humanoid_blender/         Blender translation, sidebar, and add-on entry point
tests/
    core/
        models/           Input validation tests
        proportions/      Proportion generation tests
        geometry/         Mesh validity, symmetry, and scaling tests
    blender/              Real Blender integration tests
docs/
    architecture.md       Dependency rules and extension guidance
    proportions.md        Measurements, formulas, and supported inputs
    geometry.md           Mesh structure, axes, and blockout limitations
    blender.md            Installation and integration testing
examples/                 Runnable core demonstrations
scripts/                  Add-on packaging and Blender test runners
dist/                     Generated add-on ZIP (ignored by Git)
artifacts/                Generated previews (ignored by Git)
pyproject.toml            Package configuration
```

The public import remains `from humanoid_core import BodyType, HumanoidSpec`.
Both packages live at the repository root so the test command above still works
without installing the project. Reserved packages contain documentation only.

## Architecture direction

The core owns proportions and mesh data, and will own skeletons, skin weights,
and animation data. The Blender adapter translates mesh data into Blender objects. Core
code must not import Blender's `bpy` module. Generated assets should remain
editable through ordinary artist workflows.

The next step is reviewing the blockout in Blender before starting basic rigging.

## Git

The local Git repository uses `main`. Generated archives, previews, and caches
are ignored. No remote is configured. Use `git status` and `git log --oneline`
to inspect changes and commit history.
