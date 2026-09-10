# Human Provider 1.0 closeout audit

Audit performed against `main` after PR #80.

## Result

**Code/architecture: pass for moving to the Dog provider.**

The Human 1.0 implementation now exercises the provider/capability architecture deeply enough to begin the next anatomy family without another speculative refactor. Shared Blender workflow remains capability-driven, deforming providers own their skin-weight generation, target-specific behavior stays in target adapters, and Human-specific geometry/rigging/animation behavior remains in provider-focused code.

PR #80 also closes the cross-clip pose-contamination regression by making generated actions self-contained poses and resetting evaluated pose state during generated-clip activation. Its CI run passed the standalone Python matrix and both Blender integration targets.

## Architecture findings

- `object_core` remains host-independent and does not depend on Blender APIs.
- Provider declarations remain the source of truth for rigging, idle, locomotion, skin weights, and generated materials.
- `blender_adapter.workflow` resolves the selected asset provider and follows provider capabilities rather than Human anatomy.
- Skin-weight generation remains provider-owned; the Blender adapter only applies the returned weights.
- Target-specific packaging remains isolated to target adapters.
- The historical `humanoid_blender` and `humanoid` fallbacks are compatibility surfaces, not the direction for new provider code.
- No additional abstraction is justified before Dog. Dog should be used as the next architecture proof and should drive any new shared contract only when a concrete requirement appears.

## Test-coverage findings

Current coverage is sufficient to begin Dog without adding another Human-only test layer first. The suite covers:

- provider declaration/capability validation;
- static, rigid animated, and skin-weight deforming provider paths;
- Human topology, proportions, UVs, materials, generated textures, rigging, weights, and representative joint deformation;
- Idle/Walk coexistence, switching, preservation boundaries, and complete generated bone rotation curves;
- Godot multi-clip GLB export;
- Unity multi-clip FBX export;
- Unreal model + per-clip FBX packaging, including recognizable skinned hierarchy and animation data;
- packaged add-on/runtime coverage in Blender 2.92.0 and 5.2.1.

Dog should add provider-specific geometry, skeleton, skin-weight, deformation, animation, and export tests rather than duplicating Human tests wholesale.

## Documentation drift found

The latest Unreal implementation changed after the most recent documentation sync. Several documents still describe the generated Unreal animation sidecars as **armature-only** and/or say they exclude mesh data. That is no longer correct after PR #79.

Current behavior is:

- the main Unreal FBX carries the model/skeleton/material/texture payload;
- each generated animation sidecar carries the same recognizable skinned mesh + armature hierarchy plus exactly one active generated action;
- sidecars do not embed generated textures;
- Unreal should import the main model first, then import each sidecar with **Import Only Animations** against the model skeleton;
- PR #80 additionally ensures generated clips own a complete pose so an Idle export cannot inherit Walk transforms.

The final documentation sync should update `README.md`, `docs/roadmap.md`, `docs/animation.md`, and `docs/target-verification.md` together so they describe the same Unreal workflow.

## Remaining Human 1.0 closeout gate

Do not mark Human 1.0 fully closed until the current `main` build receives a final local sanity pass after PR #80. The important checks are:

1. Generate a fresh Human 1.0 asset in Blender 5.2.1.
2. Confirm rigging, Idle, Walk, clip switching, and basic deformation still behave normally.
3. Export the Unreal bundle and confirm the model plus Idle/Walk sidecars are produced.
4. Import the model in Unreal, then import Idle and Walk with **Import Only Animations** against that skeleton.
5. Confirm Idle remains neutral/subtle, Walk remains locomotion, and neither clip inherits the other's pose.

If that passes, the Human 1.0 code milestone can be closed and the roadmap can move directly to Dog/quadruped.

## Dog readiness

The recommended next implementation sequence is deliberately narrow:

1. Add a Dog provider with its own parameter contract and deterministic base mesh.
2. Add the quadruped skeleton and provider-owned skin weights.
3. Add a simple quadruped Idle and locomotion proof using the existing generic animation contract where it fits.
4. Validate deformation and engine export through the existing shared Blender/target adapters.
5. Refactor shared contracts only if the Dog implementation exposes a real Human assumption.

Bird should follow Dog as the next anatomy/animation proof. Flight-specific semantics may justify extending the animation capability model later, but that should be decided from the actual Bird requirements rather than added speculatively during Dog work.
