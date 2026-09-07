# Asset Assistant

**Asset Assistant** is an open-source, artist-first 3D workflow tool for creating and preparing editable assets. It helps artists generate starting points, rig, animate, surface, validate, prepare, and export characters, creatures, props, and other 3D assets while keeping the artist in control of the creative result.

Asset Assistant is **not intended to replace artists**. Its purpose is to remove repetitive and technical friction so artists can spend more time designing, sculpting, refining, and making creative decisions. Generated and prepared assets should remain editable, understandable, and practical to continue working on in Blender and downstream tools.

The project uses an independent Python core with a thin Blender adapter. The first mature generator is a stylized humanoid built from height, weight, and artistic body-type parameters. A Box provider demonstrates the same workflow for static props. These are starting providers, not the boundary of the system: the architecture should support many asset families over time, including humans, dogs, birds, other creatures, robots, props, and environmental objects.

Licensed under **GPL-3.0-or-later**. Redistribution and modification are permitted under [the license](LICENSE); see [notices](NOTICE). Generated models do not need to use the GPL merely because they were created with this program.

> **Development roadmap:** Contributors and Codex should use [docs/roadmap.md](docs/roadmap.md)
> as the working source of truth for current priorities, TODOs, milestone definitions and
> engineering guardrails.

## Blender workflow

Blender 5.2.1 LTS is the primary test target; Blender 2.92.0 remains a tested legacy runtime.
Both pass headless workflow tests. Other versions and interactive UI review are not yet verified.
The 3D Viewport sidebar (N) has five vertical tabs:

| Generator | Rigging | Animations | Validation | Export |
| --- | --- | --- | --- | --- |
| Choose Humanoid or Box | Rig supported objects and enter Pose Mode | Generate idle and preview motion | Inspect geometry, weights, clips, materials, UVs, and texture references | Choose Godot, Cura, Unity or Unreal; prepare materials and export when ready |

The current humanoid model has 15 separate parts and an optional 16-bone rigid rig.
See [idle animation instructions](docs/animation.md). A preparation button adds missing neutral materials. Smooth joints, UV generation,
and texture authoring remain future work. [Workflow and validation scope](docs/workflow.md) explains what a
static, rigged, or animated game asset needs and what is actually checked today.

## Install from source

Clone or download this repository, then run in its root folder:

```powershell
python -m scripts.build_blender_addon
```

In Blender, open Edit > Preferences > Add-ons > Install and select the generated
`dist/object_generator.zip`. Enable **Add Mesh: Object Generator**. In Object
Mode, press N in the 3D Viewport, then open **Generator**.

Generate your asset, then use the workflow tabs appropriate to that provider and target. For the current humanoid, switch to **Rigging** and click **Add Basic Rig**. Click **Enter Pose Mode** to try the bones. Validation checks the Object shown in its field. [Installation, update, and uninstall guide](docs/blender.md).

## Independent Python core

Supports Python 3.7 or newer; tested with standalone Python 3.9 and Blender 2.92's
Python 3.7.7. There are no third-party runtime dependencies.

```python
from object_core import BodyType, HumanoidSpec
from object_core import generate_proportions, generate_mesh, generate_skeleton

spec = HumanoidSpec(height_cm=180, weight_kg=95, body_type=BodyType.OVERWEIGHT)
proportions = generate_proportions(spec)
mesh = generate_mesh(proportions)
skeleton = generate_skeleton(proportions)
```

Presets are slim, average, muscular, overweight, and obese. They are artistic
controls, not medical classifications. The initial proportion generator supports
120–240 cm and 30–300 kg. [Proportion rules](docs/proportions.md).

## Tests

```powershell
python -m unittest discover -s tests -v
```

This runs core tests and explicitly skips Blender integration tests. See the
[Blender guide](docs/blender.md) for the full Blender suite and isolated ZIP check.

## Structure

```text
object_core/
    objects.py       Provider registry, input fields and type capabilities
    targets.py       Host-independent output profiles and target validation
    models/          Independent data contracts
    proportions/     Dimensions and shared joint locations
    geometry/        Mesh generation
    rigging/         Skeleton generation
    animation/       Portable animation tracks and generation
    validation/      Host-independent readiness rules
humanoid_blender/    Blender adapter, UI, rigging, and scene inspection
tests/              Core and Blender tests
scripts/            Add-on build and Blender test runners
examples/           Standalone core examples
docs/               Architecture, measurements, workflow, installation, and roadmap
dist/               Generated ZIP; ignored by Git
artifacts/          Generated previews; ignored by Git
```

Core code must never import Blender APIs. [Architecture](docs/architecture.md),
[mesh conventions](docs/geometry.md), and [rigging](docs/rigging.md).

The repository uses `main` and tracks
[jhodges0845/blender-object-generator](https://github.com/jhodges0845/blender-object-generator).

## Output targets

`Define -> Generate -> Rig (if supported) -> Animate (if supported) -> Surface -> Validate -> Target Prepare -> Export -> Artist Review`

Not every provider needs every stage. A static prop may have no rig or animation, while a human, dog, bird, robot, or other creature may expose different rigging and animation capabilities. Shared infrastructure should operate on provider capabilities rather than assuming a humanoid or even an animated asset.

Choose a destination in **Export**:

| Destination | File |
| --- | --- |
| Godot | GLB (default), glTF alternative |
| Cura | STL in millimetres, evaluated current pose |
| Unity | FBX with rig/animation and supported textures |
| Unreal Engine | FBX with rig/animation and supported textures |

In **Validation**, click **Add Missing Materials** for game assets and resolve the checklist, then
open **Export**. **Export Asset** opens Blender's file browser. No console commands or custom
engine import scripts are needed. The button remains disabled while requirements
are unmet and export revalidates after the file browser closes. Blockout design
notes and post-import reminders are informational; missing materials, geometry,
and other actionable problems must be resolved. Cura requires a connected solid,
so the separate humanoid parts need mesh preparation before STL export.

See [export workflow and supported scope](docs/targets.md). Blender 2.92 tests
verify the export operators and file contents; destination-application import and
visual quality still require manual verification.
