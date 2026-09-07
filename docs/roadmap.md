# Asset Assistant Roadmap

This document is the working source of truth for upcoming development. Keep it synchronized with implemented and verified behavior, while distinguishing automated coverage, manual smoke checks, and full destination certification.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It accelerates repetitive and technical work around 3D asset creation while keeping artists in control of the creative result.

Generation is a starting point, not finished art. Generated geometry, rigs, materials, animations, and scene structures should remain editable and understandable where practical.

The product is broader than a humanoid generator. Over time it should support humans, creatures, robots, static props, environmental objects, printable assets, and other providers that fit the capability model.

The intended architecture is:

`Host-independent asset core -> provider -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> artist review`

The conceptual workflow is:

`Define -> Generate -> Rig (if supported) -> Animate (if supported) -> Surface -> Validate -> Target Prepare -> Export -> Artist Review`

Current target families are enough to prove the abstraction:

- Godot: GLB by default, glTF alternative.
- Unity: FBX.
- Unreal Engine: FBX.
- Cura / 3D printing: STL.

## Engineering direction

- `object_core` must remain independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific source package.
- The packaged add-on retains the historical `humanoid_blender` module ID and legacy `humanoid.*` operator/settings identifiers for compatibility unless a future migration provides a safe replacement.
- Blender scene manipulation belongs in the Blender adapter.
- Generic infrastructure must not assume humanoid/biped anatomy.
- Workflow requirements should follow provider/asset capabilities.
- Anatomy-specific skeleton, proportion, and animation behavior belongs in the relevant provider or reusable anatomy component.
- Validation must report real limitations rather than hiding them to produce a green result.
- Preserve source scene state and prefer explicit, undoable preparation where practical.
- Generated output should remain editable and useful as an artist starting point.
- A non-empty export file is not proof of production readiness; destination review still matters.
- Do not add providers or destinations merely to increase counts while quality and verification remain the bottleneck.

## Completed foundation

- [x] Product identity renamed to **Asset Assistant** in Blender-facing metadata, documentation, and release packaging.
- [x] Release artifact renamed to `asset_assistant.zip` while preserving the historical installed Blender module ID for compatibility.
- [x] Host-independent `object_core` architecture.
- [x] Canonical `blender_adapter` source package separated from the core.
- [x] Blender/core import bridge clarified as `core_gateway.py` while preserving the historical `.core` import path.
- [x] Provider registry/input/capability foundation.
- [x] Parameterized humanoid blockout generation.
- [x] Box provider proving a non-character/static workflow.
- [x] Basic humanoid rigging.
- [x] Idle animation generation and preview.
- [x] Core and Blender-side validation.
- [x] Target profiles and Blender export adapters for Godot, Unity, Unreal, and Cura.
- [x] GLB/glTF, FBX, and STL output paths.
- [x] Gated export based on live validation/readiness.
- [x] Basic missing-material preparation for game assets.
- [x] Generator, Rigging, Animations, Validation, and Export sidebar workflow.
- [x] Compact export readiness/status UI.
- [x] Core unit tests plus Blender integration tests.
- [x] GitHub Actions CI covering standalone Python plus Blender 5.2.1 and legacy Blender 2.92.0 integration tests.
- [x] Isolated packaged-add-on CI verifies `asset_assistant.zip` can load, register, generate, rig, animate, validate, and exercise all four export paths in a fresh headless Blender process.
- [x] Blender 5.2 layered-action support and active-scene glTF export scoping.
- [x] Provider-aware rig/idle workflow gating based on the selected asset.
- [x] Generic `part_name` rigid binding with legacy `body_part` fallback.
- [x] Test-only non-humanoid rotor proving shared rigging, animation, validation, and GLB export without humanoid bone names.
- [x] Provider declaration validation for identity, boolean capability flags, required methods, parameter definitions, and registry-key consistency before generation.
- [x] Provider contract and current rigid-adapter limits documented in `docs/providers.md`.
- [x] Remote GitHub Actions run confirmed successful after the Blender 5.2.1/provider-hardening work.
- [x] Remote GitHub Actions run confirmed successful after the architecture naming cleanup and Asset Assistant product rename.

## P0 - Verify the existing target pipeline

Initial destination smoke checks exist for all four targets. These are useful evidence, not full production certification. Automated export checks prove that Asset Assistant can create the files; destination certification still requires reviewing those files in the destination application.

- [x] Create a repeatable target-verification checklist and record known version gaps in `target-verification.md`.
- [x] Godot smoke verification: generated humanoid GLB imported with hierarchy, skeleton/rig, and animation visible.
- [x] Modern-path Godot smoke verification: complete the interactive Asset Assistant workflow in Blender 5.2.1, export GLB successfully, import that GLB into Godot, and confirm animation playback.
- [x] Unity smoke verification: generated FBX model/idle behavior confirmed from the earlier Blender 2.92 export.
- [x] Unreal smoke verification: generated FBX model/animation confirmed from the earlier Blender 2.92 export.
- [x] Cura smoke verification: Box STL imported and sliced successfully from the earlier Blender 2.92 export.
- [x] Packaged `asset_assistant.zip` automated export smoke coverage for Godot, Unity, Unreal, and Cura paths.
- [ ] Formal Godot pass: record exact destination version and confirm hierarchy, mesh parts, skinning behavior, materials/textures, orientation, scale, and expected edit/scene workflow.
- [ ] Detailed Unity pass: confirm importer/version, hierarchy, rig/avatar behavior, skinning, materials/textures, axes, and scale.
- [ ] Detailed Unreal pass: confirm skeleton/deformation, materials/textures, axes, scale, and broader FBX compatibility.
- [ ] Detailed Cura pass: confirm displayed physical dimensions, orientation, full layer review, warnings, and representative printable output where applicable.
- [ ] Convert reproducible target-specific defects into tests or validation rules when practical.

Definition of done: each supported destination has a documented successful end-to-end import plus known limitations, with the detailed checks appropriate to that target recorded.

## P0 - Modern Blender compatibility

Blender 5.2.1 LTS is the primary modern test target. Blender 2.92.0 remains a tested legacy runtime.

- [x] Select Blender 5.2.1 LTS as the primary development/runtime test target.
- [x] Fix Blender 5.2 layered-action and glTF scene-scoping compatibility issues.
- [x] Add Blender 5.2.1 alongside Blender 2.92.0 in the CI matrix.
- [x] Confirm remote GitHub Actions succeeds with the modern/legacy matrix.
- [x] Complete automated/headless and isolated-package workflow checks on Blender 5.2.1, including generation, rigging, animation, validation, and all four export paths.
- [x] Complete an interactive Blender 5.2.1 workflow smoke test through generation, rigging, animation, validation, and successful GLB export.
- [x] Import a Blender 5.2.1-generated GLB into Godot and confirm animation playback.
- [x] Retain Blender 2.92.0 as a tested legacy runtime.
- [x] Document the modern installation path and exact tested versions.
- [ ] Complete detailed destination review of Blender 5.2.1 exports beyond the confirmed Godot animation smoke check.

Definition of done for Blender compatibility itself is met. Detailed downstream destination certification remains part of target verification, not a blocker to calling Blender 5.2.1 a verified runtime.

## P0 - Provider/capability architecture hardening

The provider foundation is substantially stronger after the recent hardening PRs, but broader capability modeling and the final shared-code anatomy audit remain open.

- [x] Gate rig/idle operator availability using the selected asset provider and armature state.
- [x] Prove static Box and non-humanoid animated-provider paths can share the workflow without identical stages.
- [x] Remove known shared rigid-binding and animation-error assumptions that required humanoid naming.
- [x] Validate current rig/idle provider declarations before use.
- [x] Document the current minimum provider contract and rigid-adapter limits.
- [ ] Finish reviewing shared rigging, animation, validation, target/export, and workflow code for remaining concrete humanoid/biped assumptions.
- [ ] Keep any remaining anatomy-specific behavior inside the Human provider or appropriate reusable anatomy components.
- [ ] Strengthen capability contracts only when real workflow operations require them; surface/UV/print operation modeling remains pending.
- [ ] Do not let capability declarations substitute for truthful asset validation (for example, printable must not make disconnected geometry pass Cura checks).

Definition of done: adding a fundamentally different provider does not require rewriting the shared workflow or pretending every asset is a humanoid.

## P0 - Human Provider 1.0: deformable game character

The current humanoid proves the pipeline but remains a multipart blockout with a rigid rig. This is the next major product-quality milestone.

- [ ] Move from disconnected blockout pieces toward smooth/unified game-ready geometry.
- [ ] Develop smoother shoulders, elbows, hips, knees, neck, and other joints.
- [ ] Establish topology suitable for deformation.
- [ ] Upgrade the skeleton/rig where needed for useful deformation.
- [ ] Generate skin weights and validate deformation quality.
- [ ] Improve hands, feet, and other blockout-level regions enough for the first usable milestone.
- [ ] Generate UVs.
- [ ] Provide a basic portable generated material/texture workflow.
- [ ] Preserve existing body parameters/presets through the improved geometry pipeline.
- [ ] Add at least one locomotion animation in addition to idle.
- [ ] Ensure the resulting animated character validates and exports successfully to GLB.
- [ ] Verify Human Provider 1.0 in Godot, then Unity and Unreal.

Definition of done: supported human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion, validation, and successful game-engine export/import, ready for an artist to continue refining.

## P1 - Architecture proofs and production quality

### Dog / quadruped provider

- [ ] Define useful quadruped parameters and editable geometry.
- [ ] Generate an appropriate skeleton and skin weights.
- [ ] Support idle plus basic locomotion.
- [ ] Reuse shared material/UV/validation/export infrastructure rather than copying the Human pipeline.
- [ ] Use implementation to expose and remove any remaining biped assumptions.

### Bird provider

- [ ] Define a basic bird provider and parameters.
- [ ] Support appropriate skeleton/wing structure and provider-specific motion.
- [ ] Reuse shared surfacing, validation, and export systems.

### Printable geometry

- [ ] Produce genuinely connected/watertight solids for providers that support printing.
- [ ] Preserve correct physical dimensions in millimetres.
- [ ] Validate manifold/closed orientation, positive volume, connected components, and relevant intersection behavior.
- [ ] Add regression coverage and manually verify representative STL output in Cura.

### Materials, textures, deformation, and animation quality

- [ ] Expand portable material preparation and UV generation.
- [ ] Support basic image textures and a predictable portable PBR subset.
- [ ] Add validation for missing/invalid UVs, texture references, and unsupported material graphs.
- [ ] Replace rigid-looking character joints with provider-appropriate deformation.
- [ ] Expand animation beyond idle and improve clip/range handling.
- [ ] Keep surfacing and animation output editable for artists.

## P2 - Target-native packaging and UI/usability

### Godot scene packaging

- [ ] Research optional `.tscn` packaging around the portable GLB output.
- [ ] Determine whether it improves the default Godot edit workflow without pretending editor-only state belongs in GLB.
- [ ] Keep GLB as the portable/default Godot output.

### Export and UI usability

- [ ] Review whether common target-preparation steps can become explicit one-click, undoable operations.
- [ ] Continue preserving source scene state and truthful validation.
- [ ] Review/rename Asset Assistant's **Animations** sidebar category to avoid confusion with Blender 5.x's built-in **Animation** sidebar category. Consider a clearer name such as **Motion** or **Asset Motion** without changing functionality.

## P2 - Broader asset ecosystem

- [ ] Expand static prop/object providers beyond Box when real use cases justify them.
- [ ] Evaluate LOD generation, collision meshes, and reusable skeleton/animation conventions after base asset quality is adequate.
- [ ] Add further artist-assistance stages only when they remove demonstrated workflow bottlenecks.

## Suggested implementation order

1. Finish the bounded shared-code humanoid-assumption audit.
2. Begin Human Provider 1.0 geometry/topology and smooth-joint work.
3. Implement deforming rig/weights against the improved human mesh.
4. Add UV and basic material/texture generation.
5. Add human locomotion and strengthen animation export handling.
6. Re-run formal Godot/Unity/Unreal verification using Human Provider 1.0.
7. Use Dog/quadruped as the second character architecture proof.
8. Complete connected/watertight print preparation for providers that support Cura.
9. Use Bird as a further anatomy/animation architecture proof.
10. Consider optional Godot `.tscn` packaging and UI/usability polish.

## Near-term release milestone: Human Provider 1.0

The near-term milestone is not "support more file formats" and it is not "replace character artists." It is:

> Give Asset Assistant supported human parameters and receive an editable, deformable, basically surfaced, animated character foundation that validates, exports, works in a supported game engine with minimal technical repair, and remains ready for an artist to refine creatively.

Human Provider 1.0 proves the character pipeline. Later providers prove that the architecture is genuinely multi-asset.
