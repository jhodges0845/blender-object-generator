# Provider implementation contract

Concrete providers live under `object_core/providers`; `object_core/objects.py` owns declaration validation, registry construction, and lookup. Providers must not import Blender APIs. Add a provider instance to `OBJECT_TYPES` before the Blender UI is registered. The registry is currently built in, not a dynamic third-party plugin API.

Call `validate_provider(provider)` before adding a new instance. Built-in providers are validated at registry construction, and `get_provider()` rechecks declarations and registry-key agreement before an operation can use them. Validation checks nonempty identity, boolean capability flags, required callable methods, and unique parameter keys. It does not invoke generation or certify returned geometry/materials.

## Required members

- Unique string `key` and user-facing `label`.
- `parameters`: a tuple of `Parameter` definitions used to build the input UI.
- `mesh(values)`: return an immutable `ObjectMesh` with named `MeshPart` entries. Validate input values in the provider. Geometry coordinates are centimetres; the Blender adapter converts them using scene unit scale.
- Boolean `supports_rig`, `supports_idle`, and `uses_skin_weights` capability declarations.
- `supports_locomotion` for providers that expose a locomotion clip. For backward compatibility, providers that omit it are treated as `False`.
- `supports_materials` for providers that participate in generated surfacing. For backward compatibility, providers that omit it are treated as `False`.

A static provider may set all capabilities false and only implement `mesh(values)`.

When `supports_rig` is true, implement `skeleton(values)` returning `Skeleton`. When `uses_skin_weights` is also true, implement `skin_weights(mesh, values)`. The generated root retains parameter values so rigging can happen later without using the currently selected Generator type or its current input values.

When `supports_idle` is true, implement `idle(duration, strength)`. Idle support requires rig support. When `supports_locomotion` is true, implement `locomotion(duration, strength)`; locomotion support also requires rig support. Animation tracks use rest-armature-space axes and seconds/radians; anatomy and motion design belong with the provider rather than shared Blender workflow code.

When `supports_materials` is true, implement `materials(values)` returning portable `MaterialSpec` entries. Each spec identifies the mesh part or parts it owns and supplies conservative base-color/metallic/roughness PBR intent. A material may also carry an `ImageTextureSpec` for generated RGBA base-color image data. The texture contract contains only a name, dimensions, and normalized pixels, so it remains host-independent and has no filesystem dependency.

The Blender adapter translates that intent into ordinary editable Principled materials and, when present, an editable Blender Image Texture node connected directly to Base Color. Existing artist assignments remain authoritative. Generated image data is intentionally simple foundation data; it is not destination certification or finished artwork.

Human 1.0 is the first provider using the material and generated-texture path. Its small warm base texture exists to prove the full UV-to-image workflow and give artists a replaceable starting surface, not to synthesize final skin detail.

## Blender workflow and compatibility

Mesh objects use `part_name` for shared binding/material assignment; `body_part` remains a fallback for older saved assets. Existing root tags, package names, and operator IDs are retained for saved-file/script compatibility, including the historical humanoid fallback when no `object_type` is stored. New generated assets must store their actual provider key.

Rig and animation operator polls inspect the selected asset's provider capabilities. Rigging requires no existing armature; generated animation requires exactly one. The Animation panel may expose Idle and/or Walk according to the selected provider's declared capabilities. Static assets cannot invoke these operators merely because a different Generator type is selected for future generation.

Generated clips are separate editable Blender actions. Selecting an existing generated clip activates it rather than overwriting its keys. Artist actions, NLA tracks, drivers, constraints, and manual pose work remain authoritative and are not silently replaced by generated animation.

Material preparation is explicit and undoable. If a provider declares generated materials and the relevant mesh is completely unsurfaced, the preparation step uses that provider's portable material/texture spec. Existing artist assignments are preserved. Providers without generated material support continue to receive the conservative neutral fallback only when material slots are missing.

Provider capabilities do not certify current asset state. UVs, materials, textures, rigging, animation, connected geometry, and destination-specific readiness are all validated from the generated/edited asset itself.

## Minimum verification

1. Test deterministic valid mesh generation and invalid inputs in ordinary Python.
2. Test each declared capability contract without requiring unrelated operations.
3. For generated surfacing, test `MaterialSpec`/`ImageTextureSpec` data plus actual Blender Principled/Image Texture translation and preservation of artist assignments.
4. For animated providers, test portable clip generation, actual evaluated Blender motion, generated-clip preservation/switching, validation, and scoped export.
5. Confirm unsupported operations remain unavailable and legacy saved assets still work.

`tests/blender/test_workflow.py` includes a test-only non-humanoid rotor that exercises shared rigid rig/animation behavior. Human 1.0 separately exercises weighted deformation, UV, generated-material, generated-image-texture, idle/locomotion selection, and active-clip export paths. These tests protect shared architecture boundaries without claiming arbitrary providers are automatically production-ready.
