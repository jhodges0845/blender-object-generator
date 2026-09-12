# Modify Feature Design

## Goal

Modify lets Asset Assistant inspect an existing Asset Assistant-generated asset, describe its current structured state, accept targeted changes, apply only supported changes, preserve unrelated artist work, and revalidate the result.

Modify is not a second generator and it is not an unrestricted scene editor. The first release should prefer explicit, reversible, provider-owned edits over guessing how arbitrary Blender data should be rebuilt.

## Architecture

The feature follows the existing boundary:

`Blender scene -> Blender inspection adapter -> host-independent asset snapshot -> modification request -> provider planning -> Blender apply adapter -> validation -> artist review`

The host-independent core must not import Blender APIs. Blender is responsible for discovering scene objects and translating them into/from the portable contract. Providers remain responsible for understanding provider-specific parameters and regeneration consequences.

## Asset snapshot contract

A snapshot describes facts needed to reason about a generated asset without exposing Blender objects to the core. The initial contract should include:

- stable generated-asset identity
- canonical provider key and display label
- provider parameter values stored on the asset
- generated mesh parts and generated/artist ownership markers where available
- rig presence and generated-rig identity
- generated animation clips and artist-facing export names
- material/texture preparation state
- latest validation summary when available
- target/export metadata that belongs to Asset Assistant
- warnings when expected generated metadata is missing or inconsistent

Snapshots are observations, not commands. Reading a snapshot must not mutate the scene.

## Modification request contract

A modification request contains only explicit requested changes. Omitted fields mean preserve current state.

The first-release supported edit set is intentionally narrow:

1. provider parameter changes that the current provider already declares as editable generation parameters
2. generated animation export-name changes
3. regeneration of provider-owned generated geometry/rig/material/animation only when required by an accepted parameter change and only after preservation checks pass

Arbitrary mesh sculpting, arbitrary bone edits, arbitrary material-node editing, and modification of non-Asset-Assistant assets are outside the first-release contract.

## Planning before mutation

Every modification must produce a plan before scene mutation. A plan states:

- requested changes
- unchanged values
- generated components that must be rebuilt
- generated components that can be retained
- artist-owned or unknown data that would be at risk
- validation/precondition failures
- whether the operation is safe to apply automatically

If preservation cannot be demonstrated, Modify must stop and explain why instead of overwriting data.

## Preservation rules

- Never replace an artist-owned action, material, mesh, NLA track, driver, constraint, or unknown scene relationship silently.
- Generated components may be replaced only when Asset Assistant can prove ownership through its metadata.
- Unrequested provider parameters remain unchanged.
- Existing generated clip export names are preserved across compatible regeneration.
- Scene transforms and unrelated scene objects are preserved.
- Legacy generated assets may be inspected through explicit compatibility mappings, but ambiguous legacy ownership blocks destructive modification.
- Failure during apply must leave the previous usable asset intact whenever practical; implementation should stage replacements before swapping/removing generated data.

## Provider responsibilities

Providers declare which parameters are modifiable and can determine what a parameter change invalidates. Shared code must not contain Human/Quadruped/Avian anatomy rules.

A provider modification impact should be expressible in generic component terms such as geometry, rig/weights, materials/UVs, and generated animation. This lets a body-dimension change request a safe rebuild while an animation export-name change remains metadata-only.

## Blender adapter responsibilities

The Blender adapter:

- locates the selected/target generated asset
- builds the portable snapshot from Blender data and Asset Assistant metadata
- checks generated ownership versus artist/unknown ownership
- stages and applies an approved plan
- restores/preserves unrelated scene state
- runs the existing validation pipeline after apply
- reports the resulting snapshot and any warnings to the UI

## First UI workflow

The future Modify workspace should initially support:

1. select/use current Asset Assistant asset
2. Inspect
3. show provider + current parameters + generated capabilities/components
4. edit supported fields
5. Preview Changes / Review Plan
6. Apply Changes
7. show validation result and exactly what changed

The UI must not apply destructive changes merely because a property field was edited.

## Testing requirements

Core tests:

- deterministic snapshots/plans from portable fixtures
- omitted values are preserved
- invalid/out-of-range provider values are rejected before mutation
- impact planning remains provider-driven
- metadata-only rename does not request geometry/rig rebuild

Blender tests:

- inspect Human, Quadruped, and Avian generated assets
- apply one representative provider parameter change per deforming provider
- preserve unrelated transforms and scene objects
- preserve generated animation export names through compatible rebuilds
- refuse modification when artist-owned animation/NLA/constraints would be overwritten
- failure does not silently destroy the previous asset
- revalidation runs after a successful apply

## Release boundary

Modify is release-ready when a user can inspect a generated Human, Quadruped, or Avian, make a supported targeted change, review its impact, apply it without unrelated artist data being silently replaced, and receive a truthful validation result.

More ambitious semantic edits (for example, "make the shoulders broader" when no explicit provider parameter represents that concept) can be layered on later by translating higher-level intent into this same explicit modification-request contract.