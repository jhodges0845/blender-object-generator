# Asset Assistant Roadmap

This document is the working source of truth for upcoming development. Keep it synchronized with implemented and verified behavior, while distinguishing automated coverage, manual smoke checks, and full destination certification.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It accelerates repetitive and technical work around 3D asset creation while keeping artists in control of the creative result.

Generation is a starting point, not finished art. Generated geometry, rigs, materials, animations, and scene structures should remain editable and understandable where practical.

The product is broader than a humanoid generator. Over time it should support humans, creatures, robots, static props, environmental objects, printable assets, and other providers that fit the capability model.

Intended architecture:

`Host-independent asset core -> provider -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> artist review`

Conceptual workflow:

`Define -> Generate -> Rig (if supported) -> Animate (if supported) -> Surface -> Validate -> Target Prepare -> Export -> Artist Review`

Current target families: Godot (GLB/glTF), Unity (FBX), Unreal Engine (FBX), and Cura/3D printing (STL).

## Engineering direction

- `object_core` remains independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific source package.
- The packaged add-on retains the historical `humanoid_blender` module ID and legacy `humanoid.*` identifiers for compatibility unless a future migration provides a safe replacement.
- Generic infrastructure must not assume humanoid/biped anatomy; anatomy-specific behavior belongs in the relevant provider or reusable anatomy component.
- Workflow requirements follow explicit provider/asset capabilities, including rig, idle-animation, and skin-weight/deformation support.
- Validation reports real limitations rather than hiding them to produce a green result.
- Generated output should remain editable and useful as an artist starting point.
- A non-empty export file is not proof of production readiness; destination review still matters.

## Completed foundation

- [x] Asset Assistant product identity and `asset_assistant.zip` release packaging, with compatibility identifiers preserved.
- [x] Host-independent `object_core`, canonical `blender_adapter`, and clarified `core_gateway.py` bridge.
- [x] Provider registry/input/capability foundation and declaration validation.
- [x] Explicit provider deformation capability contract (`uses_skin_weights`) with required `skin_weights()` behavior for deforming providers.
- [x] Parameterized humanoid blockout plus Box static-provider proof.
- [x] Basic humanoid rigging and idle animation.
- [x] Core and Blender-side validation.
- [x] Godot, Unity, Unreal, and Cura target profiles/export adapters.
- [x] GLB/glTF, FBX, and STL output paths with gated export and basic missing-material preparation.
- [x] Generator, Rigging, Animations, Validation, and Export sidebar workflow.
- [x] Core unit tests, Blender integration tests, and isolated packaged-add-on smoke tests.
- [x] CI on standalone Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Blender 5.2 layered-action support and active-scene glTF export scoping.
- [x] Provider-aware rig/idle workflow gating.
- [x] Generic `part_name` rigid binding with legacy `body_part` fallback.
- [x] Non-humanoid rotor architecture proof for shared rigging, animation, validation, and GLB export.
- [x] Provider contract and current adapter limits documented.
- [x] Bounded architecture/flexibility checkpoint completed before further Human 1.0 feature work.

## P0 - Verify the existing target pipeline

Initial destination smoke checks exist for all four targets. They are useful evidence, not full production certification.

- [x] Repeatable target-verification checklist in `target-verification.md`.
- [x] Godot smoke verification, including Blender 5.2.1 GLB export/import and animation playback.
- [x] Unity smoke verification of generated FBX model/idle behavior.
- [x] Unreal smoke verification of generated FBX model/animation.
- [x] Cura smoke verification of Box STL import/slicing.
- [x] Packaged add-on automated export smoke coverage for all four target paths.
- [ ] Formal Godot pass: exact version, hierarchy, skinning, materials/textures, orientation, scale, and expected edit/scene workflow.
- [ ] Detailed Unity pass: importer/version, hierarchy, rig/avatar, skinning, materials/textures, axes, and scale.
- [ ] Detailed Unreal pass: skeleton/deformation, materials/textures, axes, scale, and broader FBX compatibility.
- [ ] Detailed Cura pass: physical dimensions, orientation, layer review, warnings, and representative printable output.
- [ ] Convert reproducible target-specific defects into tests or validation rules when practical.

Definition of done: each supported destination has a documented successful end-to-end import plus known limitations and appropriate detailed checks.

## P0 - Modern Blender compatibility

Blender 5.2.1 LTS is the primary modern test target; Blender 2.92.0 remains a tested legacy runtime.

- [x] Blender 5.2.1 selected and covered alongside Blender 2.92.0 in CI.
- [x] Blender 5.2 layered-action and glTF scene-scoping compatibility fixed.
- [x] Automated/headless and isolated-package workflows cover generation, rigging, animation, validation, and all four export paths.
- [x] Interactive Blender 5.2.1 generation-to-GLB workflow verified.
- [x] Blender 5.2.1-generated GLB imported into Godot with animation playback confirmed.
- [x] Modern installation path and tested versions documented.
- [ ] Complete detailed destination review of Blender 5.2.1 exports beyond the Godot animation smoke check.

Blender 5.2.1 runtime compatibility itself is verified; detailed downstream certification remains target-verification work.

## P0 - Provider/capability architecture hardening

The bounded architecture checkpoint is complete for the current Human 1.0 milestone. Further capability expansion should be driven by real workflow needs rather than speculative abstraction.

- [x] Gate rig/idle operations using selected-provider capability and asset state.
- [x] Prove static Box and non-humanoid animated-provider workflows do not require identical stages.
- [x] Remove identified shared rigid-binding and animation-error assumptions requiring humanoid names.
- [x] Validate current provider declarations and document the provider contract.
- [x] Complete the bounded shared-code humanoid-assumption audit; remaining anatomy-specific Human work stays provider/local-component scoped.
- [x] Formalize skin-weight deformation as a validated provider capability and require deforming providers to supply `skin_weights()`.
- [x] Exercise the deformation capability contract with a generic non-Human provider test so the shared contract does not depend on Human anatomy.
- [ ] Add future capabilities such as surface/UV/print operations only when implementation requires them.
- [ ] Keep capability declarations separate from truthful asset validation.

Current conclusion: adding a static, rigid animated, or skin-weight deforming provider has a supported architectural path without rewriting the shared workflow or pretending every asset is a humanoid. Revisit this checkpoint when a genuinely different provider or workflow operation exposes a concrete limitation.

## P0 - Human Provider 1.0: deformable game character

Human 1.0 has moved beyond the original disconnected rigid blockout. A deformation-oriented path now exists alongside the legacy rigid path. The current implementation provides one connected Human surface, joint-support topology, a deforming skeleton, generated skin weights, Blender deformation, provider-aware rigging UI, connected-joint weight localization, a deliberate hip bridge, and representative Blender deformation regressions. This is a **tested deformation foundation**, not a claim that production-quality deformation is finished.

### Implemented foundation

- [x] Add an opt-in connected Human mesh instead of 15 disconnected blockout pieces.
- [x] Stitch shoulder and hip branches into the torso and integrate feet into the leg surface.
- [x] Add support loops around elbows, wrists, knees, ankles, and foot bends.
- [x] Add topology validation/regression coverage for the deformation-oriented mesh.
- [x] Add a Human deforming skeleton separate from the legacy rigid part-binding contract.
- [x] Generate deterministic normalized skin weights with bounded influences and left/right isolation.
- [x] Apply the deforming rig and weights in Blender.
- [x] Make the Blender rigging workflow provider-aware for the Human deforming path.
- [x] Restrict skin-weight blends to a nearest connected-joint neighborhood instead of unrelated nearby bones.
- [x] Add deliberate torso-to-same-side-upper-leg blending across the non-deforming hip/root junction.
- [x] Add representative Blender pose/deformation regressions for shoulder, elbow/forearm, hip, knee, and neck.
- [x] Preserve the existing parameter/proportion foundation through the new Human geometry path.

### Remaining Human 1.0 work

- [ ] Visually inspect and refine deformation quality at shoulders, elbows, hips, knees, neck, wrists, and ankles; add wrist/ankle regression coverage and convert other reproducible failures into focused tests where practical.
- [ ] Improve hands, feet, and other blockout-level regions enough for the first usable milestone.
- [ ] Generate UVs.
- [ ] Provide a basic portable generated material/texture workflow.
- [ ] Add at least one locomotion animation in addition to idle.
- [ ] Ensure the resulting Human 1.0 animated character validates and exports successfully to GLB.
- [ ] Verify the completed Human 1.0 character in Godot, then Unity and Unreal.

Definition of done: supported human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion, validation, and successful game-engine export/import, ready for an artist to continue refining.

## P1 - Architecture proofs and production quality

### Dog / quadruped provider

- [ ] Define useful quadruped parameters and editable geometry.
- [ ] Generate an appropriate skeleton and skin weights.
- [ ] Support idle plus basic locomotion.
- [ ] Reuse shared material/UV/validation/export infrastructure rather than copying the Human pipeline.
- [ ] Use implementation to expose any remaining anatomy assumptions.

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
- [ ] Continue provider-appropriate deformation quality refinement.
- [ ] Expand animation beyond idle and improve clip/range handling.
- [ ] Keep surfacing and animation output editable for artists.

## P2 - Target-native packaging and UI/usability

### Godot scene packaging

- [ ] Research optional `.tscn` packaging around portable GLB output.
- [ ] Determine whether it improves the Godot edit workflow without pretending editor-only state belongs in GLB.
- [ ] Keep GLB as the portable/default Godot output.

### Export and UI usability

- [ ] Review whether common target-preparation steps can become explicit one-click, undoable operations.
- [ ] Continue preserving source scene state and truthful validation.
- [ ] Review/rename Asset Assistant's **Animations** sidebar category to avoid confusion with Blender 5.x's built-in **Animation** category; consider **Motion** or **Asset Motion**.

## P2 - Broader asset ecosystem

- [ ] Expand static prop/object providers beyond Box when real use cases justify them.
- [ ] Evaluate LOD generation, collision meshes, and reusable skeleton/animation conventions after base asset quality is adequate.
- [ ] Add further artist-assistance stages only when they remove demonstrated workflow bottlenecks.

## Suggested implementation order

1. Refine Human 1.0 deformation quality, beginning with wrist/ankle coverage and representative Blender pose inspection while preserving the existing shoulder/elbow/hip/knee/neck regressions.
2. Improve remaining Human geometry details needed for the first usable character foundation.
3. Add UV and basic material/texture generation.
4. Add human locomotion and strengthen animation export handling.
5. Re-run formal Godot/Unity/Unreal verification using Human Provider 1.0.
6. Use Dog/quadruped as the second character architecture proof and revisit shared architecture only for concrete limitations it exposes.
7. Complete connected/watertight print preparation for providers that support Cura.
8. Use Bird as a further anatomy/animation architecture proof.
9. Consider optional Godot `.tscn` packaging and UI/usability polish.

## Near-term release milestone: Human Provider 1.0

The near-term milestone is not "support more file formats" and it is not "replace character artists." It is:

> Give Asset Assistant supported human parameters and receive an editable, deformable, basically surfaced, animated character foundation that validates, exports, works in a supported game engine with minimal technical repair, and remains ready for an artist to refine creatively.

Human Provider 1.0 proves the character pipeline. Later providers prove that the architecture is genuinely multi-asset.
