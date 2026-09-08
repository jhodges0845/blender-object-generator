# Asset Assistant Roadmap

This is the working source of truth for current development priorities. Keep implemented behavior, automated coverage, manual verification, and future work clearly separated.

## Product vision

**Asset Assistant** is an open-source, artist-first 3D workflow assistant. It should remove repetitive and technical friction without replacing the artist. Generated assets are starting points that remain editable and understandable.

The intended architecture is:

`Host-independent asset core -> provider -> Blender adapter -> validation/preparation -> target adapter -> exported asset -> artist review`

The project is broader than Human generation. The provider/capability model is intended to support characters, creatures, props, printable assets, and future asset families without making shared workflow code assume humanoid anatomy.

## Engineering guardrails

- `object_core` remains independent of Blender APIs.
- `blender_adapter` is the canonical Blender-specific implementation.
- `humanoid_blender` remains only as a compatibility entry point/module ID where required.
- Generic workflow code follows explicit provider capabilities rather than anatomy assumptions.
- Validation reports real limitations instead of manufacturing a green result.
- A successful file write is not equivalent to destination certification.
- Generated Blender data should remain editable by artists.

## Completed platform foundation

- [x] Asset Assistant identity and GPL release packaging.
- [x] Host-independent `object_core` and canonical `blender_adapter` boundary.
- [x] Provider registry, input fields, and capability declaration validation.
- [x] Static, rigid animated, and skin-weight deforming provider paths.
- [x] Human parameter/proportion foundation and Box static-provider proof.
- [x] Core validation plus Blender-specific inspection.
- [x] Godot, Unity, Unreal, and Cura target profiles/adapters.
- [x] GLB/glTF, FBX, and STL export paths.
- [x] Provider-aware rigging and animation workflow gating.
- [x] Blender 5.2 layered-action support and active-scene glTF scoping.
- [x] CI on standalone Python 3.9-3.12 plus Blender 2.92.0 and 5.2.1.
- [x] Cached Blender runtimes in CI.
- [x] Branch protection requiring all six CI checks before merge.
- [x] Initial Godot, Unity, Unreal, and Cura smoke verification.

## Human Provider 1.0

Human 1.0 is the current P0 milestone. The target is an editable, deformable, UV'd, basically surfaced and animated character foundation that exports successfully and is ready for artist refinement.

### Implemented Human foundation

- [x] Opt-in connected Human mesh replacing the disconnected deformation path.
- [x] Shoulder and hip branches stitched into the torso.
- [x] Feet integrated into the leg surface.
- [x] Support geometry around shoulders, elbows, wrists, hips, knees, ankles, foot bends, and neck transition.
- [x] Dedicated deforming skeleton separate from the legacy rigid part-binding path.
- [x] Deterministic normalized skin weights with bounded influences and left/right isolation.
- [x] Connected-joint influence localization plus deliberate same-side hip bridge.
- [x] Softer torso/neck and torso/shoulder weight transitions.
- [x] Blender armature and skin-weight application.
- [x] Provider-aware rigging UI for the deforming Human path.
- [x] Automated deformation movement coverage for shoulder, elbow, wrist, hip, knee, ankle, and neck.
- [x] Automated transition-spread/collapse guards for all seven representative deformation joints.
- [x] Manual deformation inspection harness for milestone-level review.
- [x] Improved blockout hands with palm, knuckle, and tapered fingertip sections.
- [x] Improved blockout feet with heel, midfoot, ball, and tapered toe sections.
- [x] Geometry regressions across all five body presets and supported height extremes.
- [x] Deterministic face-corner UV generation with an editable Blender `UVMap` layer.
- [x] Portable provider material contract plus an editable Human 1.0 Principled base surface.

### Remaining Human 1.0 work

- [ ] Perform a milestone visual pass of accumulated deformation/geometry changes and refine any reproducible issues.
- [ ] Extend the Human UV/material foundation with a basic portable image-texture workflow.
- [ ] Add at least one locomotion animation in addition to idle.
- [ ] Ensure the completed Human 1.0 animated character validates and exports successfully to GLB.
- [ ] Verify the completed Human 1.0 character in Godot, then Unity and Unreal.

Definition of done: supported Human parameters produce an editable, deformable, UV'd, basically surfaced character foundation with a rig, idle plus locomotion, truthful validation, successful game-engine export/import, and a clear handoff to an artist.

## Cleanup gate before UV work

The pre-UV cleanup gate is complete:

- [x] Test-coverage audit and targeted Human geometry coverage expansion.
- [x] Documentation sync/cleanup.
- [x] Architecture audit/cleanup.

Future architecture cleanup should remain evidence-driven: remove concrete duplication/confusion and strengthen dependency boundaries only when a real feature exposes the need.

## Target verification

Initial smoke checks exist for all four destinations. Formal certification remains future work.

- [x] Repeatable target-verification checklist.
- [x] Godot GLB import and animation smoke check.
- [x] Unity FBX model/animation smoke check.
- [x] Unreal FBX model/animation smoke check.
- [x] Cura Box STL import/slicing smoke check.
- [ ] Formal Godot pass covering hierarchy, skinning, materials/textures, orientation, scale, and edit workflow.
- [ ] Detailed Unity pass covering importer/version, rig/avatar, skinning, materials/textures, axes, and scale.
- [ ] Detailed Unreal pass covering skeleton/deformation, materials/textures, axes, scale, and FBX compatibility.
- [ ] Detailed Cura pass covering dimensions, orientation, slicing warnings, and representative printable output.

## After Human 1.0

### P1

- Dog/quadruped provider as the next major architecture proof.
- Reusable UV/material/validation infrastructure driven by real provider needs.
- Watertight print-preparation work for providers that support 3D printing.
- Bird provider as an additional anatomy/animation proof.

### P2

- Optional Godot `.tscn` packaging research while retaining GLB as the portable default.
- UI/usability polish, including reviewing the **Animations** sidebar name against Blender 5.x's built-in **Animation** category.
- Additional static/prop providers, LOD/collision work, and other artist-assistance stages when real workflows justify them.

## Suggested implementation order

1. Add a basic portable image-texture workflow on top of the Human UV/material foundation.
2. Add locomotion and strengthen animation export handling.
3. Run a meaningful Human 1.0 visual/deformation milestone pass rather than per-PR visual checks.
4. Complete GLB validation/export and formal Godot/Unity/Unreal verification.
5. Move to Dog/quadruped and revisit architecture only where it exposes concrete limitations.

## Near-term release milestone

> Give Asset Assistant supported Human parameters and receive an editable, deformable, basically surfaced, animated character foundation that validates, exports, works in a supported game engine with minimal technical repair, and remains ready for an artist to refine creatively.
