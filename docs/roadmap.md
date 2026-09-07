# Asset Assistant Roadmap

This document is the working source of truth for upcoming development. Codex and contributors should use it to choose and scope the next tasks rather than re-deriving priorities from the current implementation.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It exists to accelerate repetitive and technical work around 3D asset creation while keeping artists in control of the creative result.

Asset Assistant is **not intended to replace artists**. Generation is a starting point, not the finished creative act. The system should empower artists by producing editable foundations and by assisting with repetitive tasks such as rigging, animation setup, surfacing preparation, validation, target preparation, and export.

The project is intentionally broader than either an object generator or a humanoid generator. It should support multiple asset families over time, including:

- humans and humanoids;
- dogs and other quadrupeds;
- birds and other creatures;
- robots and non-organic characters;
- static props and environmental objects;
- printable assets;
- additional asset categories that fit the provider/capability model.

A human is one provider. A dog is another. A bird is another. A box is another. No single provider defines the product boundary.

### Artist-first design principles

These principles are product requirements, not just messaging:

1. Keep the artist in control of the creative result.
2. Prefer useful starting points over pretending generated output is automatically finished art.
3. Keep generated geometry, rigs, materials, animations, and scene structures editable and understandable where practical.
4. Prefer non-destructive and undoable assistance over hidden destructive operations.
5. Expose meaningful parameters and preparation steps rather than hiding decisions that an artist may want to change.
6. Automate repetitive and technical friction while leaving aesthetic decisions available to the artist.
7. Preserve interoperability: artists should be able to continue working in Blender and downstream tools without being trapped in an Asset Assistant-specific workflow.
8. Validation should tell the truth about an asset. Do not hide defects merely to produce a green status or an export file.

## Current position

Asset Assistant has moved beyond a humanoid-generation proof of concept and is becoming a target-aware, provider-driven asset workflow.

The intended architecture is:

`Host-independent asset core -> provider -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> artist review`

The conceptual workflow is:

`Define -> Generate -> Rig (if supported) -> Animate (if supported) -> Surface -> Validate -> Target Prepare -> Export -> Artist Review`

Not every asset requires every stage. A static prop may have no skeleton or animation. A dog, bird, human, or robot may each require fundamentally different skeletons, proportions, controls, and animation sets. Shared systems must operate on declared capabilities instead of assuming humanoid anatomy or even assuming that an asset is animated.

The repository currently separates `object_core` from `humanoid_blender`. Preserve the host-independent/core boundary while evolving naming and provider abstractions carefully; do not perform a broad package rename merely for branding unless it has clear engineering value and migration coverage.

Current target families are enough to prove the abstraction. Do not prioritize adding more destinations until the existing asset quality and target verification work below is substantially complete.

- Godot: GLB by default, glTF alternative.
- Unity: FBX.
- Unreal Engine: FBX.
- Cura / 3D printing: STL.

## Provider and capability direction

The architecture should make it possible to add new asset providers without duplicating the complete workflow or embedding species-specific assumptions in shared code.

Examples of future providers include Human/Humanoid, Dog, Bird, other creatures, Robot, Box, and richer prop/environment providers.

Providers should declare capabilities such as:

- static geometry;
- riggable/deformable geometry;
- animation support and available animation families;
- UV/material/texture support;
- printable preparation;
- collision generation when eventually supported;
- target-specific requirements or limitations.

Generic core concepts should describe meshes, skeletons, joints, skin weights, animation clips, materials, topology/readiness, and target capabilities. Human anatomy belongs in the human provider; quadruped anatomy belongs in appropriate quadruped providers/shared components; bird anatomy belongs in bird-specific code. Avoid generic functions or validation rules that silently assume two arms, two legs, a biped skeleton, or a humanoid hierarchy.

## Completed foundation

These items are already implemented and should not be treated as open work unless regression or follow-up work is required:

- [x] Host-independent `object_core` architecture.
- [x] Blender adapter/package separated from the core.
- [x] Provider registry/input/capability foundation.
- [x] Parameterized humanoid blockout generation.
- [x] Box provider proving a non-character/static workflow.
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
- [x] Sidebar workflow branch merged into `main` (PR #9).
- [x] Initial manual Godot smoke test: generated humanoid exported as GLB and imported with model hierarchy, skeleton/rig and animation visible. This does **not** yet replace formal target verification.

## Immediate priorities

### P0 - Verify the existing target pipeline

Before expanding target support, verify that the files we produce actually behave correctly in their destination applications.

Initial Godot import, Unity/Unreal model and idle checks, and Cura Box import/slicing have user-confirmed results. See the [verification record](target-verification.md) for evidence and version gaps. The detailed target checks below remain open; basic success does not establish full validation.

- [x] Create a repeatable target-verification checklist with available version evidence and explicit gaps: [verification record](target-verification.md).
- [ ] Godot: repeat the GLB import as a formal verification pass. Confirm hierarchy, mesh parts, skeleton, skinning behavior, animation playback, materials/textures, orientation, scale and expected edit/scene workflow.
- [ ] Unity: import generated FBX and verify hierarchy, rig/avatar behavior where applicable, animation playback, materials/textures, axes and scale.
- [ ] Unreal Engine: import generated FBX and verify skeleton, animation, materials/textures, axes, scale and compatibility with Unreal's expected FBX pipeline.
- [ ] Cura: import generated STL assets that pass validation and verify physical dimensions, orientation and slicer acceptance.
- [ ] Capture target-specific failures as tests or validation rules whenever practical instead of relying only on documentation.
- [x] Document current target limitations and outstanding manual checks in the [verification record](target-verification.md).

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

### P0 - Provider/capability architecture hardening

Before species-specific systems become deeply embedded, make the multi-asset intent explicit in the implementation.

- [ ] Review shared code for hidden humanoid/biped assumptions.
- [ ] Strengthen provider capability contracts for static, riggable, animatable, surfaced and printable assets.
- [ ] Ensure workflow stages can be enabled/disabled based on provider capabilities.
- [ ] Keep anatomy-specific skeleton/proportion/animation logic inside appropriate providers or reusable anatomy components rather than generic target/export code.
- [ ] Add tests proving that a static provider and an animated character provider can share the pipeline without requiring the same stages.
- [ ] Document the minimum contract for implementing a new provider.

Definition of done: adding a fundamentally different provider does not require rewriting the shared workflow or pretending that every asset is a humanoid.

### P0 - Human Provider 1.0: deformable game character

The current humanoid is a useful pipeline blockout, but it is still composed of separate parts with a basic rigid rig. The next major provider milestone is one genuinely usable generated game character. This milestone proves character-workflow capabilities; it does **not** define the scope of Asset Assistant.

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
- [ ] Verify the Human Provider 1.0 result in Godot, then Unity and Unreal.

Definition of done: given supported human parameters, Asset Assistant can produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion animation, validation and successful game-engine export/import, ready for an artist to continue refining.

## High priorities after the immediate milestone

### P1 - Second character provider: Dog / quadruped architecture proof

A dog is the preferred second character provider because it will expose hidden biped assumptions in proportions, geometry, skeleton generation, skinning, animation, UI, validation, and export.

- [ ] Define dog/quadruped parameters appropriate for a useful starting model.
- [ ] Generate editable quadruped geometry.
- [ ] Generate an appropriate quadruped skeleton and skin weights.
- [ ] Support at least idle plus basic locomotion.
- [ ] Reuse shared material/UV/validation/export infrastructure rather than copying the human pipeline.
- [ ] Record and remove any shared-code assumptions discovered during implementation.
- [ ] Verify export/import in at least the primary supported game-engine target.

Definition of done: the same shared Asset Assistant workflow supports both the human provider and a fundamentally different quadruped character without humanoid-specific hacks in generic infrastructure.

### P1 - Third character provider: Bird architecture proof

After quadrupeds, a bird is a useful test of wings, different anatomy, different locomotion, and animation capability differences.

- [ ] Define a basic bird provider and parameters.
- [ ] Support an appropriate skeleton/wing structure.
- [ ] Support provider-specific animation capabilities such as idle and flight where practical.
- [ ] Reuse shared surfacing, validation and export systems.
- [ ] Use discoveries to further generalize provider/capability contracts without over-generalizing prematurely.

### P1 - Cura-ready character geometry

Do not weaken validation to make disconnected geometry pass. Fix the geometry/preparation instead.

- [ ] Produce or prepare genuinely connected/watertight printable solids for providers that declare print support.
- [ ] Ensure joints/gaps are bridged or unioned rather than merely joining Blender objects.
- [ ] Preserve correct physical dimensions in millimetres.
- [ ] Validate manifold/closed orientation, positive volume, connected components and intersection behavior.
- [ ] Add regression coverage for printable output.
- [ ] Manually verify representative STL output in Cura.

Definition of done: a provider that declares printable output can pass the solid checks and open in Cura as one correctly scaled printable solid.

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
- [ ] Keep surfacing editable so artists can replace, repaint, or refine generated starting materials.

### P1 - Rigging, deformation and animation quality

- [ ] Replace rigid-looking joint behavior with deformation appropriate to each provider's topology.
- [ ] Expand animation beyond the current idle proof of concept.
- [ ] Support provider-specific locomotion rather than assuming one universal biped clip set.
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

## P2 - Broader asset ecosystem

Once the provider architecture, Human 1.0 and target verification are healthy, continue expanding the range of useful starting assets without turning provider count into a vanity metric.

- [ ] Expand static prop/object providers beyond the Box example.
- [ ] Add richer creature and character providers based on demonstrated artist needs.
- [ ] Keep generators host-independent where practical so future non-Blender adapters remain possible.
- [ ] Evaluate LOD generation after base mesh quality is adequate.
- [ ] Evaluate collision-mesh generation for game targets.
- [ ] Evaluate reusable skeleton/animation conventions for interoperability.
- [ ] Evaluate additional artist-assistance stages only when they remove a real workflow bottleneck.

## Engineering guardrails

Codex should preserve these constraints while implementing roadmap items:

1. `object_core` must not import Blender APIs.
2. Target-independent generation/validation logic belongs in the core when possible.
3. Blender scene manipulation belongs in the Blender adapter.
4. Generic infrastructure must not assume humanoid/biped anatomy; provider-specific anatomy belongs with the provider or appropriate reusable anatomy component.
5. Workflow requirements should follow declared provider/asset capabilities rather than forcing every asset through every stage.
6. Do not make validation pass by hiding real incompatibilities; resolve the underlying asset/export issue or document a genuine limitation.
7. Add or update automated tests for behavior changes.
8. Preserve source scene state where export/preparation can reasonably be non-destructive.
9. Prefer explicit, undoable preparation operations over hidden destructive changes.
10. Generated output should remain editable and understandable where practical; optimize for artist continuation rather than lock-in.
11. A non-empty export file is not proof of production readiness; target import/playback/visual checks and artist review matter.
12. Do not add target destinations or providers merely to increase counts while existing quality/verification remains the bottleneck.
13. Keep documentation synchronized with actual verified behavior.

## Suggested implementation order

Use this order unless a blocking defect requires otherwise:

1. Formalize Godot verification based on the successful smoke test and verify Unity, Unreal and Cura.
2. Establish and test a modern Blender compatibility target.
3. Harden provider/capability contracts and remove hidden humanoid assumptions from shared infrastructure.
4. Begin Human Provider 1.0 geometry/topology and smooth-joint work.
5. Implement deforming rig/weights against the improved human mesh.
6. Add UV and basic material/texture generation.
7. Add human locomotion and strengthen animation export handling.
8. Re-run formal Godot/Unity/Unreal verification using Human Provider 1.0.
9. Implement a Dog/quadruped provider as the second character architecture proof.
10. Complete connected/watertight print preparation for providers that support Cura.
11. Implement a Bird provider as a further anatomy/animation architecture proof.
12. Consider optional Godot `.tscn` packaging and other target-native workflow conveniences.
13. Expand richer props/providers, LOD/collision and additional artist-assistance features based on real workflow bottlenecks.

## Near-term release milestone: Human Provider 1.0

The near-term milestone is not "support more file formats" and it is not "replace character artists." It is:

> Give Asset Assistant supported human parameters and receive an editable, deformable, basically surfaced, animated character foundation that validates, exports, works in a supported game engine with minimal technical repair, and remains ready for an artist to refine creatively.

Human Provider 1.0 proves the character pipeline. The following Dog/quadruped and Bird providers prove that the architecture is genuinely multi-character, while the Box/static workflow and future prop providers ensure Asset Assistant remains broader than character generation alone.
