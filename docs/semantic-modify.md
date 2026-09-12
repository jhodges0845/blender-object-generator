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

The shared planner validates that the selected provider actually exposes `beak` and allows `shape`. It does not decide what a hooked beak means geometrically.

## Provider manifests

The first semantic manifests expose useful editing surfaces without promising that every operation is executable yet:

- Human: body, torso, shoulders, head, face, left/right arms, left/right legs, hair, clothing, accessories.
- Quadruped: body, chest, head, muzzle, ears, four legs, tail, coat, accessories.
- Avian: body, chest, head, beak, left/right wings, tail, left/right legs, left/right feet, plumage.

These declarations are intentionally provider-owned and may evolve as concrete apply implementations become available.

## Exchange v2

Modify inspection JSON v2 includes the provider's semantic target manifest. Modify request JSON v2 adds `semantic_operations` while preserving the existing parameter and animation-name fields. Version-1 request files remain accepted for compatibility.

## Current safety state

This milestone validates, transports, and plans semantic operations, but intentionally blocks mutation with an explicit planner blocker until the Blender semantic apply layer exists. This avoids a dangerous failure mode where an imported semantic request appears accepted but is silently ignored or only partially applied.

## Next implementation milestone

The next milestone is a non-destructive semantic apply layer that can persist a provider-owned modification patch over generated geometry/material/component state. It must remain re-inspectable and composable so later requests can build on earlier ones instead of destroying the procedural source.
