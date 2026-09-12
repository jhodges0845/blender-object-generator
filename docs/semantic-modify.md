# Semantic Modify foundation

Asset Assistant's external Modify handoff supports more than generation parameters. The design target is a provider-aware but host-independent operation language capable of describing rich edits such as turning a generic Avian into an eagle or a generic Human into a specific character design.

## Boundary

Shared Modify code owns transport, validation, planning, preservation checks, and stable operation structure. Providers own anatomy and component meaning. Blender remains responsible for applying approved plans to Blender data.

The shared layer must not contain special cases for eagle anatomy, Human anatomy, or any named character. Providers expose semantic targets such as `beak`, `face`, `jaw`, `cheeks`, or `wing.left` and declare which generic operation families they support on each target.

## External round trip

The current file workflow is:

`Select generated asset -> Export Inspection File -> edit externally -> Import Change File -> review plan -> Apply Imported Changes -> revalidate`

The inspection document carries stable asset identity, provider identity, generated parameters, semantic targets, executable operations, applied semantic patch state, generated animation names, component ownership, and warnings. Returned Modify files are bound to `asset_id` plus provider key so a request for one generated asset cannot be applied accidentally to another.

Import is non-mutating. Apply re-inspects the current asset and replans before changing anything.

## Semantic operation

A semantic operation contains:

- `operation`: a generic operation family such as `shape`, `scale`, `surface`, `add_detail`, `add_component`, or `remove_component`;
- `target`: a provider-declared semantic region/component key; and
- `arguments`: JSON-safe provider-interpreted values.

Example:

```json
{
  "operation": "shape",
  "target": "face",
  "arguments": {
    "profile": "defined",
    "amount": 0.6
  }
}
```

The shared planner validates that the selected provider exposes `face`, allows `shape`, and declares that pair executable. It does not decide what a defined face means geometrically.

## Provider manifests

The semantic target manifest describes the provider's editable vocabulary. Inspection export distinguishes declared operations from `executable_operations`, so an external editor can avoid returning operations the installed provider cannot apply.

Avian supports topology-preserving `shape` and `scale` operations over generated body, chest, head, beak, wings, tail, legs, and feet. Provider-owned shape profiles include hooked beak, powerful chest, broad wings, and fan tail. Surface/plumage operations remain explicitly blocked until a real apply path exists.

Human supports topology-preserving `shape` and `scale` operations over body, torso, shoulders, head, face, jaw, cheeks, left/right arms, and left/right legs. Provider-owned profiles currently include athletic torso, broad shoulders, oval head, narrow/defined face, tapered/strong jaw, high/soft cheeks, lean arms, and athletic legs. These are reusable building blocks, not named-character presets.

The first real Human inspection -> external edit -> returned Modify file -> Blender apply round trip has been manually confirmed. That test successfully preserved the generated rig while activating the semantic patch recipe.

Quadruped retains a semantic manifest but does not yet have its own semantic executor.

## Persistent patch state

Applied semantic edits are stored on the generated root as an Asset Assistant semantic operation recipe. Procedural provider parameters remain unchanged. Inspection replays the stored recipe over the provider's generated base before verifying geometry ownership, so a successfully modified asset remains recognized as Asset Assistant-generated instead of becoming an unexplained artist edit.

This makes edits composable:

`generated base + existing semantic patch + newly requested semantic patch`

A later inspection exports `applied_semantic_operations`, allowing another external round trip to build on the current design rather than starting from the unmodified base.

Semantic geometry apply preserves topology. Blender updates generated vertex positions in place, leaves the existing root, rig, materials, animation identities, and skin-weight topology intact, then re-inspects the result. A failure rolls vertex positions and stored patch metadata back.

Parameter regeneration also reapplies the existing semantic patch to the newly generated base before swapping generated components, so manual parameter changes do not erase semantic design work.

## Exchange v2

Modify inspection JSON v2 includes:

- provider semantic targets;
- executable operation lists;
- currently applied semantic operations;
- generated parameters, animation names, ownership state, and warnings.

Modify request JSON v2 adds `semantic_operations` while preserving parameter and animation-name fields. Version-1 request files remain accepted for compatibility.

## Human base-mesh quality work

The Human semantic system exposed a separate limitation: richer operations are only useful when the generated mesh contains enough structure to manipulate.

Recent Human work therefore increased head profile resolution and added a neutral facial foundation with distinct chin, mouth, nose, eye-recess, brow, and forehead shaping. Manual front/side Blender review confirmed that this is a meaningful improvement, but the facial landmarks are still intentionally broad and need additional refinement before a generic Human can be shaped into a recognizable finished character.

This geometry work remains character-neutral. Named-character intent belongs in external Modify requests, not the shared core or Human provider.

## Hair, clothing, accessories, and physics

Hair and clothing should not be treated as ordinary Human body-geometry edits. They are better modeled as first-class attachable components because they may require their own geometry, materials, rigging/weights, collision, and optional physics behavior.

The intended separation is:

- Human owns body geometry, facial structure, skin/material foundation, skeleton, weights, and component attachment context;
- hair owns hairstyle geometry/materials plus optional dynamic behavior metadata;
- clothing owns garment geometry/materials plus rig/weight and optional cloth/collision behavior;
- accessories own rigid or skinned attachment behavior as appropriate;
- host/engine adapters translate optional physics intent into Blender, Godot, Unity, or Unreal behavior.

Hair, clothing, and accessory targets remain non-executable today. They should not be promoted to executable Modify operations until the component contract and persistence/ownership rules exist.

## Current implementation boundary

Avian and Human geometry semantic edits can complete the inspection -> external request -> preview -> apply -> re-inspect round trip for executable region targets. Unsupported operations remain explicit blockers rather than silent no-ops.

The immediate Human priority is still reusable base-geometry quality, especially readable facial landmarks and silhouette. First-class component architecture for hair, clothing, and accessories follows that geometry foundation; physics remains an adapter-facing layer rather than something baked directly into Human body semantics.
