# Asset Assistant

**Asset Assistant** is an open-source, artist-first 3D workflow tool for creating and preparing editable assets. It helps artists generate starting points, rig, animate, surface, validate, prepare, and export characters, creatures, props, and other 3D assets while keeping the artist in control of the creative result.

Asset Assistant is **not intended to replace artists**. Its purpose is to remove repetitive and technical friction so artists can spend more time designing, sculpting, refining, and making creative decisions. Generated and prepared assets should remain editable, understandable, and practical to continue working on in Blender and downstream tools.

The project uses an independent Python core with a thin Blender adapter. Human is the current primary character provider, while Box and a small non-Human animated proof exercise the shared capability architecture. These are starting providers, not the boundary of the system.

Licensed under **GPL-3.0-or-later**. Redistribution and modification are permitted under [the license](LICENSE); see [notices](NOTICE). Generated models do not need to use the GPL merely because they were created with this program.

> **Development roadmap:** use [docs/roadmap.md](docs/roadmap.md) as the working source of truth for priorities, TODOs, milestone definitions, and engineering guardrails.

## Blender workflow

Blender 5.2.1 LTS is the primary modern test target; Blender 2.92.0 remains a tested legacy runtime. CI covers both, plus standalone Python 3.9-3.12.

The 3D Viewport sidebar has five workflow tabs:

| Generator | Rigging | Animations | Validation | Export |
| --- | --- | --- | --- | --- |
| Choose a provider and generate an editable asset | Add the provider-supported rig and enter Pose Mode | Generate/select supported motion such as Idle and Walk | Inspect geometry, weights, clips, materials, UVs, and texture references | Choose a target, prepare as needed, and export when ready |

Not every provider needs every stage. Shared workflow behavior follows explicit provider capabilities.

## Human status

Asset Assistant currently retains two Human paths:

- the original 15-part rigid blockout, kept for compatibility and pipeline smoke tests; and
- the opt-in **Human 1.0 deforming path**, which generates one connected skinned Human surface.

Human 1.0 now includes the connected torso/limb surface and integrated feet, dedicated deforming skeleton, generated normalized skin weights, editable UVs, a portable Principled base material with generated image texture, improved blockout hands/feet, and separate editable Idle/Walk actions. Generated textures are packed for self-contained export, and the selected generated clip is exported without silently combining the other stored actions.

The Blender 5.2.1 visual/deformation milestone has passed at foundation quality, and the completed Human has been verified through the Godot GLB path with its connected hierarchy, Skeleton3D, generated texture and separate active-clip Idle/Walk animation exports. Unity and Unreal verification remain before Human 1.0 closeout.

It remains a generated blockout foundation rather than finished anatomy. Individual fingers/toes, facial detail and higher-fidelity joint deformation are future refinement; current low-poly shoulder/armpit and other joint transitions are intentionally angular. See [Human geometry](docs/geometry.md), [rigging](docs/rigging.md), [animation](docs/animation.md), [deformation quality](docs/deformation-quality.md), and [target verification](docs/target-verification.md).

## Install from source

Clone or download this repository, then run in its root folder:

```powershell
python -m scripts.build_blender_addon
```

In Blender, open Edit > Preferences > Add-ons > Install and select the generated `dist/asset_assistant.zip`. Enable **Asset Assistant**. In Object Mode, press N in the 3D Viewport, then open **Generator**.

The packaged add-on uses Asset Assistant branding while retaining historical `humanoid_blender` / `humanoid.*` compatibility identifiers where required by existing Blender data and scripts. [Installation, update, and uninstall guide](docs/blender.md).

## Independent Python core

There are no third-party runtime dependencies. Core code must never import Blender APIs.

```python
from object_core import BodyType, HumanoidSpec
from object_core import generate_proportions, generate_mesh, generate_skeleton

spec = HumanoidSpec(height_cm=180, weight_kg=95, body_type=BodyType.OVERWEIGHT)
proportions = generate_proportions(spec)
mesh = generate_mesh(proportions)
skeleton = generate_skeleton(proportions)
```

Presets are slim, average, muscular, overweight, and obese. They are artistic controls, not medical classifications. The current proportion generator supports 120-240 cm and 30-300 kg. [Proportion rules](docs/proportions.md).

## Tests

```powershell
python -m unittest discover -s tests -v
```

Ordinary Python discovery runs core tests and skips Blender-only integration tests. CI additionally runs the suite inside Blender 2.92.0 and 5.2.1, including deforming Human, workflow, validation, export, and isolated packaged-add-on coverage. Blender runtimes are cached between CI runs.

Recent Human coverage verifies deformable topology across all five body presets and supported height extremes, representative joint deformation, generated surface/texture preparation, Idle/Walk coexistence and switching, and selected-clip GLB export behavior.

## Structure

```text
object_core/
    objects.py       Provider registry, input fields and type capabilities
    targets.py       Host-independent output profiles and target validation
    models/          Independent data contracts
    proportions/     Dimensions and shared joint locations
    geometry/        Mesh generation
    rigging/         Skeleton and skin-weight generation
    animation/       Portable animation tracks and generation
    validation/      Host-independent readiness rules
blender_adapter/     Canonical Blender adapter, UI, rigging, scene inspection, and export
humanoid_blender/    Historical compatibility entry point/module ID
tests/               Core and Blender tests
scripts/             Add-on build, CI helpers, and Blender inspection/test runners
examples/            Standalone core examples
docs/                Architecture, workflow, provider, target, geometry, and roadmap docs
```

See [Architecture](docs/architecture.md), [providers](docs/providers.md), and [workflow](docs/workflow.md).

## Output targets

`Define -> Generate -> Rig (if supported) -> Animate (if supported) -> Surface -> Validate -> Target Prepare -> Export -> Artist Review`

| Destination | File |
| --- | --- |
| Godot | GLB (default), glTF alternative |
| Cura | STL in millimetres, evaluated current pose |
| Unity | FBX with supported rig/animation/material data |
| Unreal Engine | FBX with supported rig/animation/material data |

Initial smoke verification exists for Godot, Unity, Unreal, and Cura. Human 1.0 now also has direct Godot destination evidence; Unity and Unreal remain in the current closeout. These checks are scoped evidence rather than broad production certification. See [target verification](docs/target-verification.md) and [supported target scope](docs/targets.md).
