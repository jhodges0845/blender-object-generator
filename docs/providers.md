# Provider implementation contract

Providers live in `object_core/objects.py`; they must not import Blender APIs.
Add a provider instance to `OBJECT_TYPES` before the Blender UI is registered.
The registry is currently built in, not a dynamic third-party plugin API.
Call `validate_provider(provider)` before adding a new instance. Built-in providers
are validated at registry construction, and `get_provider()` rechecks declarations
and registry-key agreement before an operation can use them. Validation checks
nonempty identity, boolean capability flags, required callable methods, and unique
parameter keys. It does not invoke generation or certify returned geometry.

## Required members

- Unique string `key` and user-facing `label`.
- `parameters`: a tuple of `Parameter` definitions used to build the input UI.
- `mesh(values)`: return an immutable `ObjectMesh` with named `MeshPart` entries.
  Validate input values in the provider. Geometry coordinates are centimetres;
  the Blender adapter converts them using scene unit scale.
- Boolean `supports_rig` and `supports_idle`. A static provider sets both false
  and need not implement skeleton or idle methods. Current idle generation
  requires a rig, so providers supporting idle must also support rigging.

When `supports_rig` is true, implement `skeleton(values)` returning `Skeleton`.
The generated root retains parameter values so rigging can happen later without
using the currently selected Generator type or its current input values.
The current rigid adapter requires one binding per mesh part, with bones in
parent-before-child order. It does not yet support smooth multi-bone skin weights.

When `supports_idle` is true, implement `idle(duration, strength)` returning
`IdleClip` with `RotationTrack` entries. Track bone names must exist in the
provider skeleton. Tracks use rest-armature-space axes and seconds/radians;
keep anatomy and motion design in the provider. The shared adapter does not
require head, torso, arm or leg bones.

## Blender workflow and compatibility

Mesh objects use `part_name` for rigid binding; `body_part` remains a fallback
for older saved assets. Existing root tags, package names and operator IDs are
retained for saved-file/script compatibility, including the historical humanoid
fallback when no `object_type` is stored. New generated assets must store their
actual provider key.

Rig and idle operator polls inspect the selected asset's provider capabilities.
Rigging requires no existing armature; idle requires exactly one. Static assets
cannot invoke these operators through search or Python merely because a
character type is selected for future generation. The execution methods retain
state validation and preserve existing rig/animation data.

Shared material preparation, target validation and export operate on actual asset
state. Provider flags do not certify materials, UVs, connected geometry or Cura
printability. The Box can pass Cura checks; the multipart humanoid cannot.
The rig/idle declaration contract is enforced; a broader surface/UV/print
capability contract remains roadmap work and should
only describe implemented operations, not bypass output validation.

## Minimum verification

1. Test deterministic valid mesh generation and invalid inputs in ordinary Python.
2. Test static providers without requesting rig or animation stages.
3. For animated providers, test actual evaluated motion, saved parameter use,
   validation, and scoped export in Blender. Test failure preservation as needed.
4. Confirm unsupported operations are unavailable and legacy saved assets still work.

`tests/blender/test_workflow.py` includes a test-only non-humanoid rotor with a
single `spindle` bone. It exercises the shared rigid rig, sampled animation,
validation and GLB export without body-part metadata or humanoid bone names.
This is regression coverage, not a shipped Rotor provider or proof that arbitrary
smooth characters already fit the current rigid adapter.
