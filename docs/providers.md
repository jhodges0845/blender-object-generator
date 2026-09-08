# Provider implementation contract

Concrete providers live under `object_core/providers`; `object_core/objects.py` owns declaration validation, registry construction, and lookup. Providers must not import Blender APIs. Add a provider instance to `OBJECT_TYPES` before the Blender UI is registered. The registry is currently built in, not a dynamic third-party plugin API.

Call `validate_provider(provider)` before adding a new instance. Built-in providers are validated at registry construction, and `get_provider()` rechecks declarations and registry-key agreement before an operation can use them. Validation checks nonempty identity, boolean capability flags, required callable methods, and unique parameter keys. It does not invoke generation or certify returned geometry/materials.

## Required members

- Unique string `key` and user-facing `label`.
- `parameters`: a tuple of `Parameter` definitions used to build the input UI.
- `mesh(values)`: return an immutable `ObjectMesh` with named `MeshPart` entries. Validate input values in the provider. Geometry coordinates are centimetres; the Blender adapter converts them using scene unit scale.
- Boolean `supports_rig`, `supports_idle`, `uses_skin_weights`, and `supports_materials` capability declarations.

A static provider may set all four capabilities false and only implement `mesh(values)`.

When `supports_rig` is true, implement `skeleton(values)` returning `Skeleton`. When `uses_skin_weights` is also true, implement `skin_weights(mesh, values)`. The generated root retains parameter values so rigging can happen later without using the currently selected Generator type or its current input values.

When `supports_idle` is true, implement `idle(duration, strength)`. Idle support requires rig support. Animation tracks use rest-armature-space axes and seconds/radians; anatomy and motion design belong with the provider rather than shared Blender workflow code.

When `supports_materials` is true, implement `materials(values)` returning portable `MaterialSpec` entries. Each spec identifies the mesh part or parts it owns and supplies a conservative base-color/metallic/roughness PBR intent. The Blender adapter translates that intent into ordinary editable Principled materials. This capability describes generation intent only; actual material state is still inspected by validation before export.

Human 1.0 is the first provider using this material capability. Its generated surface is intentionally a simple neutral warm base that artists can replace rather than a claim of final skin or finished texturing.

## Blender workflow and compatibility

Mesh objects use `part_name` for shared binding/material assignment; `body_part` remains a fallback for older saved assets. Existing root tags, package names, and operator IDs are retained for saved-file/script compatibility, including the historical humanoid fallback when no `object_type` is stored. New generated assets must store their actual provider key.

Rig and idle operator polls inspect the selected asset's provider capabilities. Rigging requires no existing armature; idle requires exactly one. Static assets cannot invoke these operators merely because a different Generator type is selected for future generation.

Material preparation is explicit and undoable. If a provider declares generated materials and the relevant mesh is completely unsurfaced, the preparation step uses that provider's portable material spec. Existing artist assignments are preserved. Providers without generated material support continue to receive the conservative neutral fallback only when material slots are missing.

Provider capabilities do not certify current asset state. UVs, materials, rigging, animation, connected geometry, and destination-specific readiness are all validated from the generated/edited asset itself.

## Minimum verification

1. Test deterministic valid mesh generation and invalid inputs in ordinary Python.
2. Test each declared capability contract without requiring unrelated operations.
3. For generated materials, test portable `MaterialSpec` data plus actual Blender Principled translation and preservation of artist assignments.
4. For animated providers, test actual evaluated motion, saved parameter use, validation, and scoped export in Blender.
5. Confirm unsupported operations remain unavailable and legacy saved assets still work.

`tests/blender/test_workflow.py` includes a test-only non-humanoid rotor that exercises shared rigid rig/animation behavior. Human 1.0 separately exercises weighted deformation, UV, and generated-material paths. These tests protect shared architecture boundaries without claiming arbitrary providers are automatically production-ready.
