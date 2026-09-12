# Semantic Modify foundation

Asset Assistant's external Modify handoff must support more than generation parameters. The design target is a provider-aware but host-independent operation language capable of describing rich edits such as turning a generic Avian into an eagle or a generic Human into a named character design.

## Boundary

Shared Modify code owns transport, validation, planning, preservation checks, and stable operation structure. Providers own anatomy and component meaning. Blender remains responsible for applying approved plans to Blender data.

The shared layer must not contain special cases for eagle anatomy, Human anatomy, or any named character. Instead, providers expose semantic targets such as `beak`, `face`, `wing.left`, `hair`, or `clothing` and declare which generic operation families they support on each target.

## Semantic operation

A semantic operation contains:

- `operation`: a generic operation family such as `shape`, `scale`, `surface`, `add_detail`, `add_component`, or `remove_component`;
- `target`: a provider-declared semantic region/component key; and
- `arguments`: JSON-safe provider-interpreted values.

Example request fragment:

```json
{
  "operation": "shape",
  "target": "beak",
  "arguments": {
    "profile": "hooked",
    "amount": 0.8
  }
}
```

The shared planner validates that the selected provider exposes `beak`, allows `shape`, and declares that pair executable. It does not decide what a hooked beak means geometrically.

## Provider manifests

The semantic target manifest describes the provider's editable vocabulary. Inspection export now distinguishes declared operations from `executable_operations`, so an external editor can avoid returning operations the installed provider cannot yet apply.

The first concrete semantic geometry executor is Avian. It supports topology-preserving `shape` and `scale` operations over generated body, chest, head, beak, wings, tail, legs, and feet. Provider-owned shape profiles currently include hooked beak, powerful chest, broad wings, and fan tail. Surface/plumage operations remain declared but explicitly blocked until their apply path exists.

Human and Quadruped retain their semantic manifests but remain blocked for semantic mutation until their own provider executors are implemented. Shared Modify code does not infer anatomy for them.

## Persistent patch state

Applied semantic edits are stored on the generated root as an Asset Assistant semantic operation recipe. The procedural provider parameters remain unchanged. Inspection replays the stored recipe over the provider's generated base before verifying geometry ownership, so a successfully applied semantic asset remains recognized as generated rather than becoming an unexplained artist edit.

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

## Current implementation boundary

Avian geometry semantic edits can now complete the full inspection -> external request -> preview -> apply -> re-inspect round trip. Unsupported operations remain explicit blockers rather than silent no-ops.

This is not yet the full rich-asset goal. Human character shaping, hair, clothing/accessory components, detailed materials, and Quadruped semantic execution remain follow-up provider work. The architecture is intentionally set up so those capabilities can be added provider-by-provider without adding named-character or species logic to the shared Modify engine.
