# Human Provider 1.0 closeout audit

Audit performed against `main` after PR #80.

## Result

**Code/architecture: pass for moving to the Quadruped provider.**

The Human 1.0 implementation exercises the provider/capability architecture deeply enough to begin the next anatomy family without another speculative refactor. Shared Blender workflow remains capability-driven, deforming providers own their skin-weight generation, target-specific behavior stays in target adapters, and Human-specific geometry/rigging/animation behavior remains in provider-focused code.

PR #80 also closed the cross-clip pose-contamination regression by making generated actions self-contained poses and resetting evaluated pose state during generated-clip activation. Its CI run passed the standalone Python matrix and both Blender integration targets.

## Architecture findings

- `object_core` remains host-independent and does not depend on Blender APIs.
- Provider declarations remain the source of truth for rigging, idle, locomotion, skin weights, and generated materials.
- `blender_adapter.workflow` resolves the selected asset provider and follows provider capabilities rather than Human anatomy.
- Skin-weight generation remains provider-owned; the Blender adapter only applies the returned weights.
- Target-specific packaging remains isolated to target adapters.
- The historical `humanoid_blender` and `humanoid` fallbacks are compatibility surfaces, not the direction for new provider code.
- No additional abstraction was justified before Quadruped. Quadruped was used as the next architecture proof and drove new shared contracts only where a concrete requirement appeared.

## Test-coverage findings

The Human coverage was sufficient to begin Quadruped without adding another Human-only test layer first. The suite covered:

- provider declaration/capability validation;
- static, rigid animated, and skin-weight deforming provider paths;
- Human topology, proportions, UVs, materials, generated textures, rigging, weights, and representative joint deformation;
- Idle/Walk coexistence, switching, preservation boundaries, and complete generated bone rotation curves;
- Godot multi-clip GLB export;
- Unity multi-clip FBX export;
- Unreal model + per-clip FBX packaging, including recognizable skinned hierarchy and animation data;
- packaged add-on/runtime coverage in Blender 2.92.0 and 5.2.1.

Quadruped subsequently added provider-specific geometry, skeleton, skin-weight, deformation, animation, and Blender workflow tests rather than duplicating Human tests wholesale.

## Documentation drift found

The Unreal implementation changed after an earlier documentation sync. Current behavior is:

- the main Unreal FBX carries the model/skeleton/material/texture payload;
- each generated animation sidecar carries the same recognizable skinned mesh + armature hierarchy plus exactly one active generated action;
- sidecars do not embed generated textures;
- Unreal should import the main model first, then import each sidecar with **Import Only Animations** against the model skeleton;
- generated clips own a complete pose so an Idle export cannot inherit Walk transforms.

## Historical closeout gate

The Human code milestone was closed after local Blender/destination sanity checks confirmed generation, rigging, Idle/Walk, clip switching, deformation, and Unreal model/animation-sidecar behavior.

## Provider sequence

The architecture sequence established by this audit is:

1. Human establishes the connected deforming provider foundation.
2. Quadruped proves a genuinely different deforming anatomy and locomotion model through the same shared workflow.
3. Avian is the next anatomy/motion proof and should begin directly with canonical Avian naming.

Flight-specific semantics may justify extending animation capabilities later, but only when actual Avian requirements demonstrate the need.
