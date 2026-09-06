# Object Generator Roadmap

This document is the working source of truth for upcoming development. Codex and contributors should use it to choose and scope the next tasks rather than re-deriving priorities from the current implementation.

## Current position

Object Generator has moved beyond a humanoid-generation proof of concept and is becoming a target-aware asset-generation pipeline.

The intended architecture is:

`Host-independent object core -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> target review`

The current end-to-end workflow is:

`Generate -> Rig -> Animate -> Core Validation -> Target Profile -> Blender Target Adapter -> Prepare -> Export -> Target Review`

The repository already separates `object_core` from `humanoid_blender`. Preserve this boundary: core code must remain independent of `bpy`, and Blender-specific behavior belongs in the adapter/package.

Current target families are enough to prove the abstraction. Do not prioritize adding more destinations until the existing asset quality and target verification work below is substantially complete.

- Godot: GLB by default, glTF alternative.
- Unity: FBX.
- Unreal Engine: FBX.
- Cura / 3D printing: STL.

## Completed foundation

These items are already implemented and should not be treated as open work unless regression or follow-up work is required:

- [x] Host-independent `object_core` architecture.
- [x] Blender adapter/package separated from the core.
- [x] Parameterized humanoid blockout generation.
- [x] Basic humanoid rigging.
- [x] Idle animation generation and preview.
- [x] Core and Blender-side validation.
- [x] Target profiles for Godot, Unity, Unreal and Cura.
- [x] Target-specific Blender export adapters.
- [x] GLB/glTF, FBX and STL output paths.
- [x] Gated export based on live validation/readiness.
- [x] Material preparation for missing basic game materials.
- [x] Generator, Rigging, Animations, Validation and Export sidebar tabs.
- [x] Compact export readiness/status UI.
- [x] Core unit tests plus Blender integration tests.
- [x] GitHub Actions CI for standalone Python and Blender 2.92 integration tests.
- [x] Sidebar workflow branch merged into `main` (PR #9). This supersedes the earlier TODO to bring the completed sidebar branch into main.
- [x] Initial manual Godot smoke test: generated humanoid exported as GLB and imported with model hierarchy, skeleton/rig and animation visible. This is useful evidence but does **not** yet replace the formal target-verification task below.

## Immediate priorities

### P0 - Verify the existing target pipeline

Before expanding target support, verify that the files we produce actually behave correctly in their destination applications.

- [ ] Create a repeatable target-verification checklist and record application/version used.
- [ ] Godot: repeat the GLB import as a formal verification pass. Confirm hierarchy, mesh parts, skeleton, skinning behavior, animation playback, materials/textures, orientation, scale and expected edit/scene workflow.
- [ ] Unity: import generated FBX and verify hierarchy, rig/avatar behavior where applicable, animation playback, materials/textures, axes and scale.
- [ ] Unreal Engine: import generated FBX and verify skeleton, animation, materials/textures, axes, scale and compatibility with Unreal's expected FBX pipeline.
- [ ] Cura: import generated STL assets that pass validation and verify physical dimensions, orientation and slicer acceptance.
- [ ] Capture target-specific failures as tests or validation rules whenever practical instead of relying only on documentation.
- [ ] Document known target limitations and the exact manual checks that cannot yet be automated.

Definition of done: each supported destination has at least one documented successful end-to-end import using a generated asset, with known limitations recorded.

### P0 - Verify modern Blender compatibility

The current automated Blender contract is Blender 2.92. That is too old to remain the only verified runtime.

- [ ] Select a current supported Blender version as the primary development/runtime target.
- [ ] Run the add-on and complete workflow on that version.
- [ ] Fix API/exporter compatibility issues without breaking the core/adapter boundary.
- [ ] Update CI to test the supported modern Blender version.
- [ ] Decide whether Blender 2.92 remains supported or becomes legacy/unsupported.
- [ ] Update installation and compatibility documentation accordingly.

Definition of done: the add-on installs, generates, rigs, animates, validates and exports on the documented modern Blender version, with CI coverage where feasible.

### P0 - Humanoid 1.0: deformable game character

The current humanoid is a useful pipeline blockout, but it is still composed of separate parts with a basic rigid rig. The next major product milestone is one genuinely usable generated game character.

- [ ] Improve the humanoid from disconnected blockout pieces toward smooth/unified game-ready geometry.
- [ ] Develop smoother shoulders, elbows, hips, knees, neck and other joints.
- [ ] Establish topology suitable for deformation rather than rigid-part animation.
- [ ] Upgrade the skeleton/rig where needed for useful character deformation.
- [ ] Generate skin weights and validate deformation quality.
- [ ] Improve hands, feet and other obviously blockout-level regions enough for the first usable character milestone.
- [ ] Generate UVs.
- [ ] Provide at least a basic portable generated material/texture workflow.
- [ ] Preserve the existing body parameters/presets through the improved geometry pipeline.
- [ ] Add at least one locomotion animation in addition to idle.
- [ ] Ensure the resulting animated character passes validation and exports successfully to GLB.
- [ ] Verify the Humanoid 1.0 result in Godot, then Unity and Unreal.

Definition of done: given supported humanoid parameters, the system can generate a deformable, UV'd, basically surfaced character with a rig, idle plus locomotion animation, validation and successful game-engine export/import.

## High priorities after the immediate milestone

### P1 - Cura-ready humanoid geometry

Codex previously identified disconnected humanoid parts as the blocker for Cura. Do not weaken validation to make the current model pass. Fix the geometry/preparation instead.

- [ ] Produce or prepare a genuinely connected/watertight humanoid solid for print export.
- [ ] Ensure joints/gaps are bridged or unioned rather than merely joining Blender objects.
- [ ] Preserve correct physical dimensions in millimetres.
- [ ] Validate manifold/closed orientation, positive volume, connected components and intersection behavior.
- [ ] Add regression coverage for printable humanoid output.
- [ ] Manually verify the resulting STL in Cura.

Definition of done: a generated humanoid can pass the existing Cura solid checks and open in Cura as one correctly scaled printable solid.

### P1 - Materials, textures and surfacing

The current neutral Principled-material preparation is a good export baseline, not a finished art pipeline.

- [ ] Expand portable material preparation while keeping target constraints explicit.
- [ ] Generate UVs as part of asset preparation where appropriate.
- [ ] Support basic image-texture generation/assignment.
- [ ] Define a portable PBR subset that maps predictably to GLB and FBX workflows.
- [ ] Support normal maps where appropriate.
- [ ] Define/manualize baking for procedural Blender shaders and mappings that cannot travel directly.
- [ ] Improve texture-file handling for FBX and Godot requirements.
- [ ] Add validation for missing/invalid UVs, texture references and unsupported material graphs.
- [ ] Verify visual results after import rather than treating successful serialization as visual correctness.

### P1 - Joint and animation quality

- [ ] Replace rigid-looking joint behavior with deformation appropriate to the improved topology.
- [ ] Expand animation beyond the current idle proof of concept.
- [ ] Add locomotion first (walk/run as appropriate), then evaluate additional reusable clips.
- [ ] Improve clip/range management so exports are predictable across targets.
- [ ] Add deformation and animation regression checks where they can be automated.

## P2 - Target-native packaging and workflow improvements

These are useful, but should follow the asset-quality work above.

### Godot scene packaging

GLB should remain the portable asset format. Investigate an optional Godot-specific higher-level output for users who want a ready-to-use scene rather than only an imported model resource.

- [ ] Research and prototype optional `.tscn` generation/packaging around the exported GLB.
- [ ] Determine whether the generated scene can improve the default editability/workflow without misrepresenting what belongs in the GLB import itself.
- [ ] Keep GLB available as the portable/default Godot asset output.
- [ ] Do not attempt to encode Godot editor-only state into GLB when it is not part of the glTF asset model.

### Export usability

- [ ] Review whether common target preparation steps can safely become explicit one-click, undoable operations.
- [ ] Keep validation truthful: warnings/errors should not be silently downgraded merely to enable Export.
- [ ] Continue preserving user scene state and avoiding destructive source-asset changes.

## P2 - Broader asset-system evolution

Once Humanoid 1.0 and target verification are healthy, continue proving that the architecture is an object-generation system rather than a humanoid-only add-on.

- [ ] Expand static prop/object providers beyond the Box example.
- [ ] Define reusable contracts for provider capabilities: static, riggable, animatable, printable and target-specific constraints.
- [ ] Keep generators host-independent where practical so future non-Blender adapters remain possible.
- [ ] Evaluate LOD generation after base mesh quality is adequate.
- [ ] Evaluate collision-mesh generation for game targets.
- [ ] Evaluate reusable skeleton/animation conventions for interoperability.

## Engineering guardrails

Codex should preserve these constraints while implementing roadmap items:

1. `object_core` must not import Blender APIs.
2. Target-independent generation/validation logic belongs in the core when possible.
3. Blender scene manipulation belongs in `humanoid_blender`.
4. Do not make validation pass by hiding real incompatibilities; resolve the underlying asset/export issue or document a genuine limitation.
5. Add or update automated tests for behavior changes.
6. Preserve source scene state where export/preparation can reasonably be non-destructive.
7. Prefer explicit, undoable preparation operations over hidden destructive changes.
8. A non-empty export file is not proof of production readiness; target import/playback/visual checks matter.
9. Do not add more target destinations merely to increase the target count while the existing four are unverified or asset quality remains the bottleneck.
10. Keep documentation synchronized with actual verified behavior.

## Suggested implementation order

Use this order unless a blocking defect requires otherwise:

1. Formalize Godot verification based on the successful smoke test and verify Unity, Unreal and Cura.
2. Establish and test a modern Blender compatibility target.
3. Begin Humanoid 1.0 geometry/topology and smooth-joint work.
4. Implement deforming rig/weights against the improved mesh.
5. Add UV and basic material/texture generation.
6. Add locomotion animation and strengthen animation export handling.
7. Re-run formal Godot/Unity/Unreal verification using the Humanoid 1.0 asset.
8. Complete the connected/watertight Cura humanoid path and verify in Cura.
9. Consider optional Godot `.tscn` packaging and other target-native workflow conveniences.
10. Expand to richer providers, LOD/collision and additional production features.

## Release milestone: Humanoid 1.0

The near-term milestone is not "support more file formats." It is:

> Give Object Generator supported body parameters and receive a deformable, basically surfaced, animated character that validates, exports and works in a supported game engine with minimal manual repair.

That milestone should drive prioritization until it is achieved.
