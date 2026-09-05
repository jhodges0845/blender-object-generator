# Humanoid core — pieces 1 through 3

A small, software-independent foundation for generating editable character
starting points for artists. The core defines validated inputs and calculates
stylized adult body proportions and a low-poly humanoid blockout mesh. Rigging,
animation, and the Blender adapter are not implemented yet.

## Use

Requires Python 3.9 or newer. From this folder:

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
humanoid_blender/         Blender adapter (reserved)
tests/
    core/
        models/           Input validation tests
        proportions/      Proportion generation tests
        geometry/         Mesh validity, symmetry, and scaling tests
    blender/              Adapter tests (reserved)
docs/
    architecture.md       Dependency rules and extension guidance
    proportions.md        Measurements, formulas, and supported inputs
    geometry.md           Mesh structure, axes, and blockout limitations
examples/                 Runnable core demonstrations
pyproject.toml            Package configuration
```

The public import remains `from humanoid_core import BodyType, HumanoidSpec`.
Both packages live at the repository root so the test command above still works
without installing the project. Reserved packages contain documentation only.

## Architecture direction

The core owns proportions and mesh data, and will own skeletons, skin weights,
and animation data. A future Blender adapter will translate those into Blender objects. Core
code must not import Blender's `bpy` module. Generated assets should remain
editable through ordinary artist workflows.

The next piece is the Blender adapter, so artists can view and edit the blockout.
